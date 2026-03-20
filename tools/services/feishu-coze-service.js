#!/usr/bin/env node
/**
 * 飞书视频处理服务 - 译文
 * 
 * 监听飞书事件，当收到视频消息时调用 Coze 工作流
 */

const http = require('http');
const crypto = require('crypto');

// 配置
const COZE_WORKFLOW_URL = "https://ny5xtnd234.coze.site/run";
const COZE_TOKEN = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjUyMmYxMWE3LTM2Y2EtNGQ0Ny04NjEyLWVlZTk5MTg5MWM3YSJ9.eyJpc3MiOiJodHRwczovL2FwaS5jb3plLmNuIiwiYXVkIjpbIlRzRFU3SlBXWnU1aTdxQ2JjbHFIdTJydEZ0R0ltM3UzIl0sImV4cCI6ODIxMDI2Njg3Njc5OSwiaWF0IjoxNzczNDk1MzE4LCJzdWIiOiJzcGlmZmU6Ly9hcGkuY296ZS5jbi93b3JrbG9hZF9pZGVudGl0eS9pZDo3NjE3MDkwOTEyNDA5MDkyMTM2Iiwic3JjIjoiaW5ib3VuZF9hdXRoX2FjY2Vzc190b2tlbl9pZDo3NjE3MTA0Mzk0MTMxMDc5MTk0In0.DkmxlJW3cUNvWBoVsQpOIhs1oNkpWeZe3sQ7PL78H1Opgs2qf7Qsnx7kBQs1zE2UnjcGUG_MIpG492ixCzYGkN85539OUR8cTMzHP6XE8H0calvXCRvXDJoAZT0wh-ANHaC6aXYBRGhOf4h3SenYe57DXDoGxQDrpKMoUcuIAIFV43niNZh3bxYA4p231AGItskbDIKznL8557ORQ21JL8Qfz1OibIcEZTHcSy4LbGyYyKfTw2RhBCenbuIIMa4R_Hfl45XRldklZj-XTDTlqLxPvas1PfNeeNVm8GSZqiaEosWx7b9YhygsyVr7mJBCnk-xAPPi_dJiqyK5XBAQsQ";
const TARGET_CHAT_ID = "oc_95a9882e1aca9546c1930b2d27660a6a";
const PORT = process.env.PORT || 15428;

/**
 * 处理飞书视频消息
 */
async function processVideoMessage(messageData) {
  const { chat_id, message, mentions } = messageData;
  
  console.log(`[译文] 收到消息：chat_id=${chat_id}`);
  
  // 检查是否是目标群聊
  if (chat_id !== TARGET_CHAT_ID) {
    return null;
  }
  
  // 检查是否@Bot
  const isMentioned = mentions?.some(m => 
    m.name === "译文" || 
    m.name === "feishubot"
  );
  
  if (!isMentioned) {
    return null;
  }
  
  // 检查是否有视频
  const hasVideo = message?.message_type === "video" ||
                   message?.attachments?.some(a => a.type === "video");
  
  if (!hasVideo) {
    return null;
  }
  
  console.log("[译文] ✅ 匹配成功，处理视频");
  
  // 获取视频 URL
  const videoUrl = message?.video_url || 
                   message?.content?.match(/https?:\/\/[^\s<>"{}|\\^`\[\]]+/)?.[0];
  
  if (!videoUrl) {
    return {
      text: "⚠️ 未找到视频 URL"
    };
  }
  
  console.log(`[译文] 视频 URL: ${videoUrl}`);
  
  // 调用 Coze 工作流
  try {
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
    console.log("[译文] Coze 响应:", result);
    
    if (response.status === 200 && result.extracted_content) {
      const extractedText = result.extracted_content;
      const scriptText = result.script_content || "";
      
      let reply = "✅ **识别完成！**\n\n";
      reply += `**文字稿**：\n${extractedText.substring(0, 1000)}${extractedText.length > 1000 ? "..." : ""}\n\n`;
      
      if (scriptText) {
        reply += `**剧本**：\n${scriptText.substring(0, 1000)}${scriptText.length > 1000 ? "..." : ""}`;
      }
      
      return {
        text: reply,
        full_result: result
      };
    } else {
      return {
        text: `❌ 识别失败：${result.msg || "未知错误"}`
      };
    }
  } catch (error) {
    console.error("[译文] 错误:", error);
    return {
      text: `❌ 处理失败：${error.message}`
    };
  }
}

/**
 * HTTP 服务器 - 接收飞书 Webhook
 */
const server = http.createServer(async (req, res) => {
  if (req.method === "POST" && req.url === "/webhook/feishu-coze") {
    let body = "";
    
    req.on("data", chunk => {
      body += chunk.toString();
    });
    
    req.on("end", async () => {
      try {
        const eventData = JSON.parse(body);
        console.log("[译文] 收到 Webhook 事件:", eventData);
        
        const result = await processVideoMessage(eventData);
        
        if (result) {
          console.log("[译文] 处理结果:", result.text.substring(0, 100));
          res.writeHead(200, { "Content-Type": "application/json" });
          res.end(JSON.stringify(result));
        } else {
          res.writeHead(200, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ status: "ignored" }));
        }
      } catch (error) {
        console.error("[译文] 处理错误:", error);
        res.writeHead(500, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ error: error.message }));
      }
    });
  } else if (req.method === "GET" && req.url === "/health") {
    res.writeHead(200, { "Content-Type": "text/plain" });
    res.end("OK - 译文服务运行中");
  } else {
    res.writeHead(404);
    res.end("Not Found");
  }
});

server.listen(PORT, () => {
  console.log("====================================");
  console.log("译文 - 飞书视频处理服务");
  console.log("====================================");
  console.log(`端口：${PORT}`);
  console.log(`Webhook URL: http://localhost:${PORT}/webhook/feishu-coze`);
  console.log(`健康检查：http://localhost:${PORT}/health`);
  console.log("====================================");
  console.log("服务已启动，等待飞书事件...");
});
