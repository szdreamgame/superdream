#!/usr/bin/env node
/**
 * 画语 AGENT - 独立运行版本
 * 
 * 监听飞书图片生成工作室群消息，响应图片生成命令
 */

const GRSAI_API_HOST = "https://grsai.dakka.com.cn";
const GRSAI_API_KEY = "sk-10eee66de80245e78277514e88a67401";
const FEISHU_APP_ID = "cli_a92e8b3399b85cd6";
const FEISHU_APP_SECRET = "tMiX2hL0wTf7ujPSK2pqnf3d3aeg8AGa";
const TARGET_CHAT_ID = "oc_f22ffe36d557729c0d77f8b11c74e0bd"; // AI 图片生成工作室

let tenantToken = null;
let tokenExpireAt = 0;

/**
 * 获取飞书 Token
 */
async function getFeishuToken() {
  const now = Date.now();
  if (tenantToken && now < tokenExpireAt) return tenantToken;
  
  const response = await fetch("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ app_id: FEISHU_APP_ID, app_secret: FEISHU_APP_SECRET })
  });
  
  const result = await response.json();
  if (result.code === 0) {
    tenantToken = result.tenant_access_token;
    tokenExpireAt = now + 7200000;
    return tenantToken;
  }
  throw new Error(`获取 Token 失败：${result.msg}`);
}

/**
 * 发送飞书消息
 */
async function sendFeishuMessage(chatId, text) {
  const token = await getFeishuToken();
  const response = await fetch(`https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      receive_id: chatId,
      msg_type: "text",
      content: JSON.stringify({ text })
    })
  });
  
  const result = await response.json();
  return result.code === 0;
}

/**
 * 调用 GRS AI API 生成图片
 */
async function generateImage(prompt) {
  const response = await fetch(`${GRSAI_API_HOST}/v1/images/generations`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${GRSAI_API_KEY}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      model: "nano-banana-2",
      prompt: prompt,
      n: 2,
      size: "1024x1024",
      response_format: "url"
    })
  });
  
  return await response.json();
}

/**
 * 处理图片生成命令
 */
async function processDrawCommand(messageId, chatId, content) {
  console.log(`[画语] 处理命令：${content}`);
  
  const match = content.match(/(\/生成 | \/画 | \/图片 | \/画语)\s*(.*)/);
  if (!match || !match[2]) {
    await sendFeishuMessage(chatId, "📖 **使用示例**：\n\n`/生成 角色图 一个勇敢的骑士`\n`/画 场景 中世纪城堡`");
    return;
  }
  
  const [, type, description] = match;
  console.log(`[画语] 生成图片：${description}`);
  
  try {
    const result = await generateImage(description);
    
    if (result.data && result.data.length > 0) {
      let reply = `✅ **生成完成！**\n\n描述：${description}\n\n`;
      result.data.forEach((img, i) => {
        reply += `![图片${i+1}](${img.url})\n`;
      });
      reply += `\n⚠️ 图片 URL 有效期 2 小时，请及时保存`;
      
      await sendFeishuMessage(chatId, reply);
      console.log(`[画语] ✅ 发送 ${result.data.length} 张图片`);
    } else {
      await sendFeishuMessage(chatId, `❌ 生成失败：${result.error?.message || "未知错误"}`);
    }
  } catch (error) {
    console.error(`[画语] ❌ 错误：${error.message}`);
    await sendFeishuMessage(chatId, `❌ 处理失败：${error.message}`);
  }
}

/**
 * 轮询飞书消息（简化实现）
 */
async function pollMessages() {
  console.log("[画语] 启动轮询...");
  
  // 这里应该实现飞书消息轮询或 webhook 监听
  // 简化版本：手动触发测试
  
  console.log("[画语] 监听中...（当前为简化版本，需要实现完整的消息轮询）");
}

// 启动
console.log("=".repeat(60));
console.log("画语 AGENT - AI 图片生成工作室");
console.log("=".repeat(60));
console.log(`目标群：${TARGET_CHAT_ID}`);
console.log(`命令：/生成、/画、/图片、/画语`);
console.log("=".repeat(60));

// 如果要实际运行，需要实现飞书消息监听
// pollMessages();

// 导出函数供其他模块调用
module.exports = { processDrawCommand, sendFeishuMessage, generateImage };
