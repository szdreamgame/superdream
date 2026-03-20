/**
 * 飞书消息处理钩子 - 译文视频识别
 * 
 * 这个钩子会在飞书插件处理消息前被调用
 * 拦截漫剧群的视频消息，调用 Coze 工作流
 */

const COZE_WORKFLOW_URL = "https://ny5xtnd234.coze.site/run";
const COZE_TOKEN = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjUyMmYxMWE3LTM2Y2EtNGQ0Ny04NjEyLWVlZTk5MTg5MWM3YSJ9.eyJpc3MiOiJodHRwczovL2FwaS5jb3plLmNuIiwiYXVkIjpbIlRzRFU3SlBXWnU1aTdxQ2JjbHFIdTJydEZ0R0ltM3UzIl0sImV4cCI6ODIxMDI2Njg3Njc5OSwiaWF0IjoxNzczNDk1MzE4LCJzdWIiOiJzcGlmZmU6Ly9hcGkuY296ZS5jbi93b3JrbG9hZF9pZGVudGl0eS9pZDo3NjE3MDkwOTEyNDA5MDkyMTM2Iiwic3JjIjoiaW5ib3VuZF9hdXRoX2FjY2Vzc190b2tlbl9pZDo3NjE3MTA0Mzk0MTMxMDc5MTk0In0.DkmxlJW3cUNvWBoVsQpOIhs1oNkpWeZe3sQ7PL78H1Opgs2qf7Qsnx7kBQs1zE2UnjcGUG_MIpG492ixCzYGkN85539OUR8cTMzHP6XE8H0calvXCRvXDJoAZT0wh-ANHaC6aXYBRGhOf4h3SenYe57DXDoGxQDrpKMoUcuIAIFV43niNZh3bxYA4p231AGItskbDIKznL8557ORQ21JL8Qfz1OibIcEZTHcSy4LbGyYyKfTw2RhBCenbuIIMa4R_Hfl45XRldklZj-XTDTlqLxPvas1PfNeeNVm8GSZqiaEosWx7b9YhygsyVr7mJBCnk-xAPPi_dJiqyK5XBAQsQ";

const TARGET_CHAT_ID = "oc_95a9882e1aca9546c1930b2d27660a6a";

/**
 * 处理飞书视频消息
 * @param {Object} context - 消息上下文
 * @returns {Promise<Object|null>} - 处理结果或 null（不拦截）
 */
async function handleFeishuVideoMessage(context) {
  const { message, chat_id, mentions, account_id } = context;
  
  console.log("[译文钩子] 收到消息:", { chat_id, message_type: message?.message_type });
  
  // 1. 检查是否是目标群聊
  if (chat_id !== TARGET_CHAT_ID) {
    return null;
  }
  
  // 2. 检查是否@Bot
  const isMentioned = mentions?.some(m => 
    m.name === "译文" || 
    m.name === "feishubot" ||
    m.user_id === account_id
  );
  
  if (!isMentioned) {
    return null;
  }
  
  // 3. 检查是否有视频
  const hasVideo = message?.message_type === "video" ||
                   message?.content?.includes("video") ||
                   message?.attachments?.some(a => a.type === "video");
  
  if (!hasVideo) {
    return null;
  }
  
  console.log("[译文钩子] ✅ 匹配成功，处理视频");
  
  // 4. 获取视频 URL
  const videoUrl = message?.video_url || 
                   message?.content?.match(/https?:\/\/[^\s<>"{}|\\^`\[\]]+/)?.[0];
  
  if (!videoUrl) {
    return {
      text: "⚠️ 未找到视频 URL，请确认视频文件可访问"
    };
  }
  
  console.log("[译文钩子] 视频 URL:", videoUrl);
  
  // 5. 调用 Coze 工作流
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
    console.log("[译文钩子] Coze 响应:", result);
    
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
    console.error("[译文钩子] 错误:", error);
    return {
      text: `❌ 处理失败：${error.message}`
    };
  }
}

// 导出钩子函数
if (typeof module !== "undefined" && module.exports) {
  module.exports = { handleFeishuVideoMessage };
}
