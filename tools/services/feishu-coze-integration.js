/**
 * 飞书视频消息处理 - 集成到 OpenClaw 飞书插件
 * 
 * 使用方法：
 * 1. 将此文件复制到 OpenClaw 飞书插件目录
 * 2. 在 bot.ts 中导入并调用
 */

const COZE_WORKFLOW_URL = "https://ny5xtnd234.coze.site/run";
const COZE_TOKEN = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjUyMmYxMWE3LTM2Y2EtNGQ0Ny04NjEyLWVlZTk5MTg5MWM3YSJ9.eyJpc3MiOiJodHRwczovL2FwaS5jb3plLmNuIiwiYXVkIjpbIlRzRFU3SlBXWnU1aTdxQ2JjbHFIdTJydEZ0R0ltM3UzIl0sImV4cCI6ODIxMDI2Njg3Njc5OSwiaWF0IjoxNzczNDk1MzE4LCJzdWIiOiJzcGlmZmU6Ly9hcGkuY296ZS5jbi93b3JrbG9hZF9pZGVudGl0eS9pZDo3NjE3MDkwOTEyNDA5MDkyMTM2Iiwic3JjIjoiaW5ib3VuZF9hdXRoX2FjY2Vzc190b2tlbl9pZDo3NjE3MTA0Mzk0MTMxMDc5MTk0In0.DkmxlJW3cUNvWBoVsQpOIhs1oNkpWeZe3sQ7PL78H1Opgs2qf7Qsnx7kBQs1zE2UnjcGUG_MIpG492ixCzYGkN85539OUR8cTMzHP6XE8H0calvXCRvXDJoAZT0wh-ANHaC6aXYBRGhOf4h3SenYe57DXDoGxQDrpKMoUcuIAIFV43niNZh3bxYA4p231AGItskbDIKznL8557ORQ21JL8Qfz1OibIcEZTHcSy4LbGyYyKfTw2RhBCenbuIIMa4R_Hfl45XRldklZj-XTDTlqLxPvas1PfNeeNVm8GSZqiaEosWx7b9YhygsyVr7mJBCnk-xAPPi_dJiqyK5XBAQsQ";
const TARGET_CHAT_ID = "oc_95a9882e1aca9546c1930b2d27660a6a";
const BOT_NAME = "译文";

/**
 * 尝试处理视频消息
 * @param {Object} event - 飞书消息事件
 * @param {string} accountId - Bot 账号 ID
 * @returns {Promise<boolean>} - 是否已处理
 */
async function tryProcessVideoWithCoze(event, accountId) {
  const chat_id = event.chat_id;
  const message = event.message;
  
  // 1. 检查是否是目标群聊
  if (chat_id !== TARGET_CHAT_ID) {
    return false;
  }
  
  // 2. 检查消息类型是否是视频
  const isVideo = message?.message_type === "video" || 
                  message?.attachments?.some(a => a.type === "video");
  
  if (!isVideo) {
    return false;
  }
  
  // 3. 检查是否@Bot
  const mentions = message?.mentions || [];
  const isMentioned = mentions.some(m => 
    m.name === BOT_NAME || 
    m.name === "feishubot"
  );
  
  if (!isMentioned) {
    return false;
  }
  
  console.log("[译文] 检测到视频消息，开始处理...");
  
  // 4. 获取视频文件信息
  const fileKey = message?.file_key || message?.content?.file_key;
  const videoUrl = message?.video_url;
  
  if (!fileKey && !videoUrl) {
    console.log("[译文] 未找到视频文件信息");
    return false;
  }
  
  // 5. 下载视频文件
  let localPath = null;
  if (fileKey) {
    console.log("[译文] 下载视频文件:", fileKey);
    // TODO: 调用飞书 API 下载文件
    // localPath = await downloadFeishuFile(fileKey, accountId);
  }
  
  // 6. 上传到 OSS
  let ossUrl = videoUrl;
  if (localPath) {
    console.log("[译文] 上传到 OSS:", localPath);
    // TODO: 上传到 OSS
    // ossUrl = await uploadToOss(localPath);
  }
  
  if (!ossUrl) {
    console.log("[译文] 无法获取视频 URL");
    return false;
  }
  
  // 7. 调用 Coze 工作流
  console.log("[译文] 调用 Coze 工作流:", ossUrl);
  try {
    const response = await fetch(COZE_WORKFLOW_URL, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${COZE_TOKEN}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        video_file: {
          url: ossUrl,
          file_type: "video"
        }
      })
    });
    
    const result = await response.json();
    console.log("[译文] Coze 响应:", result);
    
    if (response.status === 200 && result.extracted_content) {
      // 8. 发送结果到群聊
      const extractedText = result.extracted_content;
      const scriptText = result.script_content || "";
      
      let reply = "✅ **识别完成！**\n\n";
      reply += `**文字稿**：\n${extractedText.substring(0, 1000)}${extractedText.length > 1000 ? "..." : ""}\n\n`;
      
      if (scriptText) {
        reply += `**剧本**：\n${scriptText.substring(0, 1000)}${scriptText.length > 1000 ? "..." : ""}`;
      }
      
      // TODO: 发送消息到飞书群
      // await sendMessageFeishu({ to: chat_id, text: reply });
      
      console.log("[译文] 处理完成！");
      return true;
    } else {
      console.log("[译文] Coze 调用失败:", result);
      return false;
    }
  } catch (error) {
    console.error("[译文] 错误:", error);
    return false;
  }
}

// 导出函数
if (typeof module !== "undefined" && module.exports) {
  module.exports = { tryProcessVideoWithCoze };
}
