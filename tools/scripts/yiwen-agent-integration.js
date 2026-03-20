/**
 * 译文 AGENT 集成模块
 * 被飞书插件 bot.ts 调用
 */

const COZE_WORKFLOW_URL = "https://ny5xtnd234.coze.site/run";
const COZE_TOKEN = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjUyMmYxMWE3LTM2Y2EtNGQ0Ny04NjEyLWVlZTk5MTg5MWM3YSJ9.eyJpc3MiOiJodHRwczovL2FwaS5jb3plLmNuIiwiYXVkIjpbIlRzRFU3SlBXWnU1aTdxQ2JjbHFIdTJydEZ0R0ltM3UzIl0sImV4cCI6ODIxMDI2Njg3Njc5OSwiaWF0IjoxNzczNDk1MzE4LCJzdWIiOiJzcGlmZmU6Ly9hcGkuY296ZS5jbi93b3JrbG9hZF9pZGVudGl0eS9pZDo3NjE3MDkwOTEyNDA5MDkyMTM2Iiwic3JjIjoiaW5ib3VuZF9hdXRoX2FjY2Vzc190b2tlbl9pZDo3NjE3MTA0Mzk0MTMxMDc5MTk0In0.DkmxlJW3cUNvWBoVsQpOIhs1oNkpWeZe3sQ7PL78H1Opgs2qf7Qsnx7kBQs1zE2UnjcGUG_MIpG492ixCzYGkN85539OUR8cTMzHP6XE8H0calvXCRvXDJoAZT0wh-ANHaC6aXYBRGhOf4h3SenYe57DXDoGxQDrpKMoUcuIAIFV43niNZh3bxYA4p231AGItskbDIKznL8557ORQ21JL8Qfz1OibIcEZTHcSy4LbGyYyKfTw2RhBCenbuIIMa4R_Hfl45XRldklZj-XTDTlqLxPvas1PfNeeNVm8GSZqiaEosWx7b9YhygsyVr7mJBCnk-xAPPi_dJiqyK5XBAQsQ";
const TARGET_CHAT_ID = "oc_95a9882e1aca9546c1930b2d27660a6a";

export async function tryProcessYiwenVideoMessage(params) {
  const { event, account, botName, botOpenId, log, sendMessage } = params;
  
  const chatId = event.message?.chat_id || event.chat_id;
  if (chatId !== TARGET_CHAT_ID) return false;
  
  const messageType = event.message?.message_type;
  if (messageType !== 'video') return false;
  
  const mentions = event.message?.mentions || [];
  const isMentioned = mentions.some(m => m.name === '译文' || m.name === 'feishubot' || m.name === botName);
  if (!isMentioned) return false;
  
  log(`[译文 AGENT] ✅ 匹配视频消息`);
  
  try {
    const attachments = event.message?.attachments || [];
    const videoAtt = attachments.find(a => a.type === 'video' || a.file_type === 'video');
    
    if (!videoAtt || !videoAtt.file_key) {
      await sendMessage({ to: chatId, text: "⚠️ 未找到视频文件" });
      return true;
    }
    
    const messageId = event.message.message_id;
    const senderName = event.sender?.name || '未知';
    
    log(`[译文 AGENT] 消息 ID: ${messageId}, 发送者：${senderName}`);
    
    // 调用 Python 脚本处理
    const { exec } = await import('child_process');
    const scriptPath = '/root/.openclaw/workspace/scripts/yiwen-process-video.py';
    
    await new Promise((resolve, reject) => {
      const proc = exec(`python3 ${scriptPath} "${messageId}" "${videoAtt.file_key}" "${chatId}" "${senderName}"`, (error, stdout, stderr) => {
        if (error) {
          log(`[译文 AGENT] ❌ 执行失败：${error.message}`);
          reject(error);
        } else {
          log(`[译文 AGENT] ${stdout}`);
          resolve(stdout);
        }
      });
    });
    
    return true;
    
  } catch (error) {
    log(`[译文 AGENT] ❌ 错误：${error.message}`);
    await sendMessage({ to: chatId, text: `❌ 处理失败：${error.message}` });
    return true;
  }
}
