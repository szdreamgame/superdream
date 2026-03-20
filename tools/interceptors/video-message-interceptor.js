/**
 * 飞书视频消息拦截器 - 译文视频识别
 * 
 * 处理漫剧群的视频消息，调用 Coze 工作流进行识别，
 * 并自动创建/更新飞书表格记录
 */

const COZE_WORKFLOW_URL = "https://ny5xtnd234.coze.site/run";
const COZE_TOKEN = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjUyMmYxMWE3LTM2Y2EtNGQ0Ny04NjEyLWVlZTk5MTg5MWM3YSJ9.eyJpc3MiOiJodHRwczovL2FwaS5jb3plLmNuIiwiYXVkIjpbIlRzRFU3SlBXWnU1aTdxQ2JjbHFIdTJydEZ0R0ltM3UzIl0sImV4cCI6ODIxMDI2Njg3Njc5OSwiaWF0IjoxNzczNDk1MzE4LCJzdWIiOiJzcGlmZmU6Ly9hcGkuY296ZS5jbi93b3JrbG9hZF9pZGVudGl0eS9pZDo3NjE3MDkwOTEyNDA5MDkyMTM2Iiwic3JjIjoiaW5ib3VuZF9hdXRoX2FjY2Vzc190b2tlbl9pZDo3NjE3MTA0Mzk0MTMxMDc5MTk0In0.DkmxlJW3cUNvWBoVsQpOIhs1oNkpWeZe3sQ7PL78H1Opgs2qf7Qsnx7kBQs1zE2UnjcGUG_MIpG492ixCzYGkN85539OUR8cTMzHP6XE8H0calvXCRvXDJoAZT0wh-ANHaC6aXYBRGhOf4h3SenYe57DXDoGxQDrpKMoUcuIAIFV43niNZh3bxYA4p231AGItskbDIKznL8557ORQ21JL8Qfz1OibIcEZTHcSy4LbGyYyKfTw2RhBCenbuIIMa4R_Hfl45XRldklZj-XTDTlqLxPvas1PfNeeNVm8GSZqiaEosWx7b9YhygsyVr7mJBCnk-xAPPi_dJiqyK5XBAQsQ";

const TARGET_CHAT_ID = "oc_95a9882e1aca9546c1930b2d27660a6a"; // 漫剧 - 文案评审群

// 飞书表格配置
const BITABLE_APP_TOKEN = "GHrubiTjnayG4fsWP2IcJIotnfc";
const BITABLE_TABLE_ID = "tbl8ik4qLltAlXvp";

/**
 * 检查消息是否是视频消息
 */
function isVideoMessage(event) {
  const messageType = event.message?.message_type;
  
  if (messageType === "video") return true;
  
  const attachments = event.message?.attachments;
  if (attachments && Array.isArray(attachments)) {
    return attachments.some(a => a.type === "video" || a.file_type === "video");
  }
  
  const content = event.message?.content;
  if (content && typeof content === "string") {
    return content.includes("video") || content.includes("file_type");
  }
  
  return false;
}

/**
 * 检查是否@了 Bot
 */
function isBotMentioned(event, botName, botOpenId) {
  const mentions = event.message?.mentions;
  if (!mentions || !Array.isArray(mentions)) return false;
  
  return mentions.some(m => 
    m.name === "译文" || 
    m.name === "feishubot" ||
    m.name === botName ||
    m.user_id === botOpenId
  );
}

/**
 * 从消息中提取视频信息
 */
function extractVideoInfo(event, account) {
  const attachments = event.message?.attachments;
  if (attachments && attachments.length > 0) {
    const videoAttachment = attachments.find(a => a.type === "video" || a.file_type === "video");
    if (videoAttachment) {
      return {
        file_key: videoAttachment.file_key,
        file_name: videoAttachment.file_name || "video.mp4",
        url: videoAttachment.url
      };
    }
  }
  
  const content = event.message?.content;
  if (content) {
    const urlMatch = content.match(/https?:\/\/[^\s<>"{}|\\^`\[\]]+/);
    if (urlMatch) {
      return { url: urlMatch[0], file_name: "video.mp4" };
    }
  }
  
  return null;
}

/**
 * 下载飞书视频文件
 */
async function downloadFeishuVideo(account, messageId, fileKey, log) {
  const { createFeishuClient } = await import('./feishu-client-wrapper.js');
  const client = createFeishuClient(account);
  
  try {
    log(`[译文拦截器] 下载视频：${fileKey}`);
    const response = await client.im.message.resource.get({
      path: { 
        message_id: messageId,
        file_key: fileKey 
      },
      query: { type: "file" }
    });
    
    return response;
  } catch (error) {
    log(`[译文拦截器] 下载视频失败：${error.message}`);
    throw error;
  }
}

/**
 * 上传视频到 OSS
 */
async function uploadToOSS(videoData, log) {
  // 这里需要调用 Python 脚本或 OSS API
  // 简化处理：假设已有 OSS URL
  log(`[译文拦截器] 上传视频到 OSS...`);
  
  // TODO: 实现 OSS 上传
  // 暂时返回一个占位 URL
  return `https://openclaw-mjai.oss-cn-shanghai.aliyuncs.com/coze/video_${Date.now()}.mp4`;
}

/**
 * 调用 Coze 工作流进行视频识别
 */
async function callCozeWorkflow(videoUrl, log) {
  try {
    log(`[译文拦截器] 调用 Coze API: ${videoUrl}`);
    
    const response = await fetch(COZE_WORKFLOW_URL, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${COZE_TOKEN}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        video_file: {
          url: videoUrl,
          file_type: "video"
        }
      })
    });
    
    const result = await response.json();
    log(`[译文拦截器] Coze 响应状态：${response.status}`);
    
    return { response, result };
  } catch (error) {
    log(`[译文拦截器] Coze 调用失败：${error.message}`);
    throw error;
  }
}

/**
 * 从 Coze 结果中提取文字稿和剧本
 */
function extractContentFromResult(result) {
  const data = result.data || result;
  
  // 尝试不同字段
  const extractedText = data.extracted_content || data.text || data.result || data.output || data.answer || "";
  const scriptContent = data.script_content || data.script || "";
  
  // 如果没有单独的剧本字段，尝试从文字稿中解析
  let transcript = extractedText;
  let script = scriptContent;
  let characters = "";
  let scene = "";
  
  // 尝试解析剧本格式
  if (extractedText.includes("【") && extractedText.includes("】")) {
    // 可能包含角色信息
    const charMatches = extractedText.match(/【([^】]+)】/g);
    if (charMatches) {
      characters = [...new Set(charMatches)].join("\n").replace(/[【】]/g, "");
    }
  }
  
  return { transcript, script, characters, scene };
}

/**
 * 创建或更新飞书表格记录
 */
async function createOrUpdateBitableRecord(params) {
  const { videoInfo, content, senderId, senderName, log } = params;
  
  try {
    log(`[译文拦截器] 创建飞书表格记录...`);
    
    // 使用 feishu_bitable_create_record API
    const fields = {
      "文本": `视频识别 - ${videoInfo.file_name || "未知"}`,
      "文字稿": content.transcript || "",
      "视频链接": videoInfo.url ? { text: "视频链接", link: videoInfo.url } : null,
      "主要角色": content.characters || "",
      "场景设定": content.scene || "",
      "完整剧本": content.script || content.transcript || "",
      "状态": "待评审",
      "需求人": senderId ? [{ id: senderId }] : null,
      "标题": `视频识别-${new Date().toLocaleString('zh-CN')}`
    };
    
    // 清理 null 值
    Object.keys(fields).forEach(key => {
      if (fields[key] === null || fields[key] === undefined) {
        delete fields[key];
      }
    });
    
    log(`[译文拦截器] 表格字段：${JSON.stringify(fields, null, 2)}`);
    
    // TODO: 调用 feishu_bitable_create_record
    // 这里需要通过 OpenClaw runtime 调用
    const runtime = globalThis.__openclaw_runtime__;
    if (runtime && runtime.createBitableRecord) {
      const record = await runtime.createBitableRecord({
        app_token: BITABLE_APP_TOKEN,
        table_id: BITABLE_TABLE_ID,
        fields
      });
      log(`[译文拦截器] ✅ 表格记录创建成功：${record.id}`);
      return record;
    } else {
      log(`[译文拦截器] ⚠️ 无法创建表格记录（runtime 不可用）`);
      return null;
    }
    
  } catch (error) {
    log(`[译文拦截器] ❌ 创建表格记录失败：${error.message}`);
    return null;
  }
}

/**
 * 格式化识别结果消息
 */
function formatRecognitionResult(content, recordCreated) {
  let reply = "✅ **识别完成！**\n\n";
  
  if (content.transcript) {
    reply += `**文字稿**：\n${content.transcript.substring(0, 1000)}${content.transcript.length > 1000 ? "..." : ""}\n\n`;
  }
  
  if (content.script && content.script !== content.transcript) {
    reply += `**剧本**：\n${content.script.substring(0, 1000)}${content.script.length > 1000 ? "..." : ""}\n\n`;
  }
  
  if (content.characters) {
    reply += `**主要角色**：\n${content.characters}\n\n`;
  }
  
  if (recordCreated) {
    reply += `📊 **已自动创建评审记录**\n`;
    reply += `状态：待评审\n`;
  }
  
  return reply;
}

/**
 * 主处理函数
 */
export async function tryProcessVideoMessage(params) {
  const { event, account, botName, botOpenId, log, sendMessage } = params;
  
  const chatId = event.message?.chat_id || event.chat_id;
  if (chatId !== TARGET_CHAT_ID) {
    return false;
  }
  
  if (!isVideoMessage(event)) {
    return false;
  }
  
  if (!isBotMentioned(event, botName, botOpenId)) {
    return false;
  }
  
  log(`[译文拦截器] ✅ 匹配成功，开始处理视频消息`);
  log(`[译文拦截器] 消息 ID: ${event.message.message_id}`);
  log(`[译文拦截器] 群聊 ID: ${chatId}`);
  
  const senderId = event.sender?.sender_id?.user_id || event.sender?.open_id;
  const senderName = event.sender?.name || "未知";
  
  try {
    // 1. 获取视频信息
    const videoInfo = extractVideoInfo(event, account);
    
    if (!videoInfo) {
      await sendMessage({
        to: chatId,
        text: "⚠️ 未找到视频文件，请确认视频已正确上传"
      });
      return true;
    }
    
    log(`[译文拦截器] 视频信息：${JSON.stringify(videoInfo)}`);
    
    let videoUrl = videoInfo.url;
    
    // 如果有 file_key，需要下载并上传到 OSS
    if (videoInfo.file_key && !videoUrl) {
      log(`[译文拦截器] 通过 file_key 下载视频...`);
      const downloadResult = await downloadFeishuVideo(
        account, 
        event.message.message_id, 
        videoInfo.file_key, 
        log
      );
      
      log(`[译文拦截器] 上传到 OSS...`);
      videoUrl = await uploadToOSS(downloadResult, log);
      
      if (videoUrl) {
        videoInfo.url = videoUrl;
      }
    }
    
    if (!videoUrl) {
      await sendMessage({
        to: chatId,
        text: "⚠️ 视频处理失败：无法获取视频 URL"
      });
      return true;
    }
    
    log(`[译文拦截器] 视频 URL: ${videoUrl}`);
    
    // 2. 调用 Coze 工作流
    const { response, result } = await callCozeWorkflow(videoUrl, log);
    
    if (response.status === 200 && (result.data || result.extracted_content)) {
      // 3. 提取内容
      const content = extractContentFromResult(result);
      
      log(`[译文拦截器] 识别内容：${JSON.stringify(content, null, 2).substring(0, 500)}`);
      
      // 4. 创建表格记录
      const record = await createOrUpdateBitableRecord({
        videoInfo,
        content,
        senderId,
        senderName,
        log
      });
      
      // 5. 发送结果到群聊
      const reply = formatRecognitionResult(content, !!record);
      
      await sendMessage({
        to: chatId,
        text: reply
      });
      
      log(`[译文拦截器] ✅ 处理完成！`);
      return true;
    } else {
      await sendMessage({
        to: chatId,
        text: `❌ 识别失败：${result.msg || result.message || "未知错误"}`
      });
      return true;
    }
    
  } catch (error) {
    log(`[译文拦截器] ❌ 处理失败：${error.message}`);
    
    await sendMessage({
      to: chatId,
      text: `❌ 处理失败：${error.message}`
    });
    
    return true;
  }
}

/**
 * 兼容性导出（CommonJS）
 */
if (typeof module !== "undefined" && module.exports) {
  module.exports = { tryProcessVideoMessage, isVideoMessage, isBotMentioned };
}
