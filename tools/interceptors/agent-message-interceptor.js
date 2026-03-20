/**
 * OpenClaw 飞书消息拦截器 - 译文 & 画语 AGENT
 * 
 * 集成两个 AGENT 到飞书插件消息处理流程：
 * - 译文：漫剧群视频识别 + 表格更新
 * - 画语：图片生成工作室指令响应 + 表格任务处理
 */

import { createBitableRecord, updateBitableRecord, getBitableRecords } from './feishu-bitable-wrapper.js';

// ==================== 配置区域 ====================

// 译文配置
const TRANSLATE_CONFIG = {
  chatId: "oc_95a9882e1aca9546c1930b2d27660a6a",  // 漫剧 - 文案评审群
  botName: "译文",
  cozeUrl: "https://ny5xtnd234.coze.site/run",
  cozeToken: "eyJhbGciOiJSUzI1NiIsImtpZCI6IjUyMmYxMWE3LTM2Y2EtNGQ0Ny04NjEyLWVlZTk5MTg5MWM3YSJ9.eyJpc3MiOiJodHRwczovL2FwaS5jb3plLmNuIiwiYXVkIjpbIlRzRFU3SlBXWnU1aTdxQ2JjbHFIdTJydEZ0R0ltM3UzIl0sImV4cCI6ODIxMDI2Njg3Njc5OSwiaWF0IjoxNzczNDk1MzE4LCJzdWIiOiJzcGlmZmU6Ly9hcGkuY296ZS5jbi93b3JrbG9hZF9pZGVudGl0eS9pZDo3NjE3MDkwOTEyNDA5MDkyMTM2Iiwic3JjIjoiaW5ib3VuZF9hdXRoX2FjY2Vzc190b2tlbl9pZDo3NjE3MTA0Mzk0MTMxMDc5MTk0In0.DkmxlJW3cUNvWBoVsQpOIhs1oNkpWeZe3sQ7PL78H1Opgs2qf7Qsnx7kBQs1zE2UnjcGUG_MIpG492ixCzYGkN85539OUR8cTMzHP6XE8H0calvXCRvXDJoAZT0wh-ANHaC6aXYBRGhOf4h3SenYe57DXDoGxQDrpKMoUcuIAIFV43niNZh3bxYA4p231AGItskbDIKznL8557ORQ21JL8Qfz1OibIcEZTHcSy4LbGyYyKfTw2RhBCenbuIIMa4R_Hfl45XRldklZj-XTDTlqLxPvas1PfNeeNVm8GSZqiaEosWx7b9YhygsyVr7mJBCnk-xAPPi_dJiqyK5XBAQsQ",
  bitableAppToken: "GHrubiTjnayG4fsWP2IcJIotnfc",
  bitableTableId: "tbl8ik4qLltAlXvp"
};

// 画语配置
const DRAW_CONFIG = {
  chatId: "oc_f22ffe36d557729c0d77f8b11c74e0bd",  // AI 图片生成工作室
  botName: "画语",
  grsApiHost: "https://grsai.dakka.com.cn",
  grsApiKey: "sk-10eee66de80245e78277514e88a67401",
  bitableAppToken: "GHrubiTjnayG4fsWP2IcJIotnfc",
  bitableTableId: "tbl8ik4qLltAlXvp",
  commands: ["/生成", "/画", "/图片", "/画语"]
};

// ==================== 工具函数 ====================

/**
 * 检查是否是指定的 Bot
 */
function isBotMentioned(mentions, botName, botOpenId) {
  if (!mentions || !Array.isArray(mentions)) return false;
  return mentions.some(m => 
    m.name === botName || 
    m.name === "feishubot" ||
    m.user_id === botOpenId
  );
}

/**
 * 检查是否包含命令
 */
function hasCommand(content, commands) {
  if (!content) return false;
  return commands.some(cmd => content.startsWith(cmd) || content.includes(cmd));
}

/**
 * 检查是否是视频消息
 */
function isVideoMessage(event) {
  const messageType = event.message?.message_type;
  if (messageType === "video") return true;
  
  const attachments = event.message?.attachments;
  if (attachments && Array.isArray(attachments)) {
    return attachments.some(a => a.type === "video" || a.file_type === "video");
  }
  
  return false;
}

/**
 * 从 Coze 结果中提取内容
 */
function extractContentFromResult(result) {
  const data = result.data || result;
  const transcript = data.extracted_content || data.text || data.result || "";
  const script = data.script_content || data.script || transcript;
  
  let characters = "";
  if (transcript.includes("【") && transcript.includes("】")) {
    const charMatches = transcript.match(/【([^】]+)】/g);
    if (charMatches) {
      characters = [...new Set(charMatches)].join("\n").replace(/[【】]/g, "");
    }
  }
  
  return { transcript, script, characters, scene: "" };
}

// ==================== 译文 AGENT ====================

/**
 * 处理译文视频消息
 */
async function processTranslateVideo(params) {
  const { event, account, botName, botOpenId, log, sendMessage, createBitableRecord } = params;
  
  const chatId = event.message?.chat_id || event.chat_id;
  if (chatId !== TRANSLATE_CONFIG.chatId) return false;
  if (!isVideoMessage(event)) return false;
  if (!isBotMentioned(event.message?.mentions, TRANSLATE_CONFIG.botName, botOpenId)) return false;
  
  log(`[译文 AGENT] ✅ 匹配视频消息`);
  
  try {
    // 1. 获取视频信息
    const attachments = event.message?.attachments;
    const videoAttachment = attachments?.find(a => a.type === "video" || a.file_type === "video");
    
    if (!videoAttachment) {
      await sendMessage({ to: chatId, text: "⚠️ 未找到视频文件" });
      return true;
    }
    
    const videoUrl = videoAttachment.url || `https://open.feishu.cn/file/${videoAttachment.file_key}`;
    log(`[译文 AGENT] 视频 URL: ${videoUrl}`);
    
    // 2. 调用 Coze 识别
    log(`[译文 AGENT] 调用 Coze API...`);
    const response = await fetch(TRANSLATE_CONFIG.cozeUrl, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${TRANSLATE_CONFIG.cozeToken}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        video_file: { url: videoUrl, file_type: "video" }
      })
    });
    
    const result = await response.json();
    
    if (response.status !== 200 || !result.data) {
      await sendMessage({ to: chatId, text: `❌ 识别失败：${result.msg || "未知错误"}` });
      return true;
    }
    
    // 3. 提取内容
    const content = extractContentFromResult(result);
    log(`[译文 AGENT] 识别完成，文字稿长度：${content.transcript?.length || 0}`);
    
    // 4. 创建表格记录
    let recordId = null;
    if (createBitableRecord) {
      recordId = await createBitableRecord({
        app_token: TRANSLATE_CONFIG.bitableAppToken,
        table_id: TRANSLATE_CONFIG.bitableTableId,
        fields: {
          "文本": `视频识别 - ${new Date().toLocaleString('zh-CN')}`,
          "文字稿": content.transcript || "",
          "视频链接": { text: "视频", link: videoUrl },
          "主要角色": content.characters || "",
          "场景设定": content.scene || "",
          "完整剧本": content.script || content.transcript || "",
          "状态": "待评审",
          "标题": `视频识别-${new Date().toLocaleString('zh-CN')}`
        }
      });
      log(`[译文 AGENT] 表格记录：${recordId || "创建失败"}`);
    }
    
    // 5. 发送结果
    let reply = "✅ **识别完成！**\n\n";
    reply += `**文字稿**：\n${(content.transcript || "").substring(0, 1000)}${content.transcript?.length > 1000 ? "..." : ""}\n\n`;
    if (content.characters) {
      reply += `**主要角色**：\n${content.characters}\n\n`;
    }
    if (recordId) {
      reply += `📊 **已创建评审记录**\n状态：待评审\n`;
    }
    
    await sendMessage({ to: chatId, text: reply });
    log(`[译文 AGENT] ✅ 处理完成`);
    return true;
    
  } catch (error) {
    log(`[译文 AGENT] ❌ 错误：${error.message}`);
    await sendMessage({ to: chatId, text: `❌ 处理失败：${error.message}` });
    return true;
  }
}

// ==================== 画语 AGENT ====================

/**
 * 处理画语图片生成指令
 */
async function processDrawCommand(params) {
  const { event, account, botName, botOpenId, log, sendMessage, getBitableRecords, updateBitableRecord } = params;
  
  const chatId = event.message?.chat_id || event.chat_id;
  if (chatId !== DRAW_CONFIG.chatId) return false;
  
  const content = event.message?.content || "";
  if (!hasCommand(content, DRAW_CONFIG.commands)) return false;
  
  // 检查是否@Bot
  if (!isBotMentioned(event.message?.mentions, DRAW_CONFIG.botName, botOpenId)) {
    // 没有@Bot 但有命令，也响应（方便使用）
    log(`[画语 AGENT] 检测到命令但未@Bot`);
  }
  
  log(`[画语 AGENT] ✅ 匹配图片生成命令`);
  
  try {
    // 1. 解析命令
    const commandMatch = content.match(/(\/生成 | \/画 | \/图片 | \/画语)\s*(.*)/);
    if (!commandMatch || !commandMatch[2]) {
      await sendMessage({
        to: chatId,
        text: "📖 **使用示例**：\n\n" +
              "`/生成 角色图 一个勇敢的骑士`\n" +
              "`/画 场景 中世纪城堡`\n" +
              "`/图片 角色 魔法师`\n\n" +
              "或使用表格任务自动处理"
      });
      return true;
    }
    
    const [, type, description] = commandMatch;
    log(`[画语 AGENT] 命令类型：${type}, 描述：${description}`);
    
    // 2. 调用 GRS AI API
    const grsResponse = await fetch(`${DRAW_CONFIG.grsApiHost}/v1/images/generations`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${DRAW_CONFIG.grsApiKey}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        model: "nano-banana-2",
        prompt: description,
        n: 2,
        size: "1024x1024",
        response_format: "url"
      })
    });
    
    const grsResult = await grsResponse.json();
    
    if (grsResult.data && grsResult.data.length > 0) {
      // 3. 发送结果
      let reply = `✅ **生成完成！**\n\n`;
      reply += `描述：${description}\n\n`;
      
      grsResult.data.forEach((img, i) => {
        reply += `![图片${i+1}](${img.url})\n`;
      });
      
      reply += `\n⚠️ 图片 URL 有效期 2 小时，请及时保存`;
      
      await sendMessage({ to: chatId, text: reply });
      log(`[画语 AGENT] ✅ 发送 ${grsResult.data.length} 张图片`);
    } else {
      await sendMessage({ to: chatId, text: `❌ 生成失败：${grsResult.error?.message || "未知错误"}` });
    }
    
    return true;
    
  } catch (error) {
    log(`[画语 AGENT] ❌ 错误：${error.message}`);
    await sendMessage({ to: chatId, text: `❌ 处理失败：${error.message}` });
    return true;
  }
}

/**
 * 检查并处理表格任务（画语 AGENT 轮询表格）
 */
async function checkBitableTasks(params) {
  const { log, sendMessage, getBitableRecords, updateBitableRecord } = params;
  
  // 这个函数应该由定时器定期调用
  // 简化实现：暂不自动轮询，由用户手动触发
  
  log(`[画语 AGENT] 表格任务检查（暂不自动轮询）`);
  return [];
}

// ==================== 主入口 ====================

/**
 * 统一消息处理入口
 * 在飞书插件的 handleFeishuMessage 中调用
 */
export async function tryProcessAgentMessage(params) {
  const { event, account, botName, botOpenId, log, sendMessage, createBitableRecord, getBitableRecords, updateBitableRecord } = params;
  
  // 尝试译文 AGENT
  const translateProcessed = await processTranslateVideo({
    event, account, botName, botOpenId, log, sendMessage, createBitableRecord
  });
  
  if (translateProcessed) {
    log(`[AGENT 拦截器] 译文 AGENT 已处理`);
    return true;
  }
  
  // 尝试画语 AGENT
  const drawProcessed = await processDrawCommand({
    event, account, botName, botOpenId, log, sendMessage, getBitableRecords, updateBitableRecord
  });
  
  if (drawProcessed) {
    log(`[AGENT 拦截器] 画语 AGENT 已处理`);
    return true;
  }
  
  return false;
}

/**
 * 兼容性导出（CommonJS）
 */
if (typeof module !== "undefined" && module.exports) {
  module.exports = { 
    tryProcessAgentMessage,
    processTranslateVideo,
    processDrawCommand,
    checkBitableTasks
  };
}
