/**
 * 飞书视频消息拦截器
 * 拦截漫剧群中的视频消息，调用 Coze 工作流处理
 */

const COZE_WORKFLOW_URL = "https://ny5xtnd234.coze.site/run";
const COZE_TOKEN = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjUyMmYxMWE3LTM2Y2EtNGQ0Ny04NjEyLWVlZTk5MTg5MWM3YSJ9.eyJpc3MiOiJodHRwczovL2FwaS5jb3plLmNuIiwiYXVkIjpbIlRzRFU3SlBXWnU1aTdxQ2JjbHFIdTJydEZ0R0ltM3UzIl0sImV4cCI6ODIxMDI2Njg3Njc5OSwiaWF0IjoxNzczNDk1MzE4LCJzdWIiOiJzcGlmZmU6Ly9hcGkuY296ZS5jbi93b3JrbG9hZF9pZGVudGl0eS9pZDo3NjE3MDkwOTEyNDA5MDkyMTM2Iiwic3JjIjoiaW5ib3VuZF9hdXRoX2FjY2Vzc190b2tlbl9pZDo3NjE3MTA0Mzk0MTMxMDc5MTk0In0.DkmxlJW3cUNvWBoVsQpOIhs1oNkpWeZe3sQ7PL78H1Opgs2qf7Qsnx7kBQs1zE2UnjcGUG_MIpG492ixCzYGkN85539OUR8cTMzHP6XE8H0calvXCRvXDJoAZT0wh-ANHaC6aXYBRGhOf4h3SenYe57DXDoGxQDrpKMoUcuIAIFV43niNZh3bxYA4p231AGItskbDIKznL8557ORQ21JL8Qfz1OibIcEZTHcSy4LbGyYyKfTw2RhBCenbuIIMa4R_Hfl45XRldklZj-XTDTlqLxPvas1PfNeeNVm8GSZqiaEosWx7b9YhygsyVr7mJBCnk-xAPPi_dJiqyK5XBAQsQ";

const TARGET_CHAT_ID = "oc_95a9882e1aca9546c1930b2d27660a6a";

/**
 * 拦截飞书消息
 * @param {Object} message - 飞书消息对象
 * @returns {Promise<Object|null>} - 处理结果或 null（不拦截）
 */
async function interceptFeishuMessage(message) {
  console.log("[译文拦截器] 收到消息:", JSON.stringify(message, null, 2));
  
  // 检查是否是目标群聊
  if (message.chat_id !== TARGET_CHAT_ID) {
    console.log("[译文拦截器] 非目标群聊，跳过");
    return null;
  }
  
  // 检查是否@Bot
  const isMentioned = message.mentions?.some(m => 
    m.name === "译文" || m.name === "feishubot"
  );
  
  // 检查是否是命令
  const isCommand = message.text?.startsWith("/文字") || 
                    message.text?.startsWith("/转写") ||
                    message.text?.startsWith("/识别") ||
                    message.text?.startsWith("/译文");
  
  if (!isMentioned && !isCommand) {
    console.log("[译文拦截器] 未@Bot 且不是命令，跳过");
    return null;
  }
  
  // 检查是否有视频
  const hasVideo = message.message_type === "video" || 
                   message.attachments?.some(a => a.type === "video") ||
                   message.files?.some(f => f.mime_type?.startsWith("video/"));
  
  if (!hasVideo) {
    console.log("[译文拦截器] 无视频，跳过");
    return null;
  }
  
  console.log("[译文拦截器] ✅ 匹配成功，处理视频");
  
  // 获取视频文件信息
  const videoFile = message.attachments?.find(a => a.type === "video") ||
                    message.files?.find(f => f.mime_type?.startsWith("video/"));
  
  if (!videoFile) {
    return {
      text: "⚠️ 未找到视频文件"
    };
  }
  
  // 获取视频 URL（飞书会提供临时下载链接）
  const videoUrl = videoFile.url || videoFile.download_url;
  
  if (!videoUrl) {
    return {
      text: "⚠️ 视频文件不可访问，请确认权限配置"
    };
  }
  
  console.log("[译文拦截器] 视频 URL:", videoUrl);
  
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
    console.log("[译文拦截器] Coze 响应:", result);
    
    if (response.status === 200) {
      const extractedText = result.extracted_content || result.script_content || JSON.stringify(result);
      const scriptText = result.script_content || "";
      
      let reply = "✅ **识别完成！**\n\n";
      reply += `**文字稿**：\n${extractedText.substring(0, 500)}${extractedText.length > 500 ? "..." : ""}\n\n`;
      
      if (scriptText) {
        reply += `**剧本**：\n${scriptText.substring(0, 500)}${scriptText.length > 500 ? "..." : ""}`;
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
    console.error("[译文拦截器] 错误:", error);
    return {
      text: `❌ 处理失败：${error.message}`
    };
  }
}

// 导出拦截器
module.exports = {
  interceptFeishuMessage
};
