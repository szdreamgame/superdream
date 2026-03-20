#!/bin/bash
# 修改飞书插件 bot.ts，添加译文 AGENT 拦截器

BOT_TS="/root/.local/share/pnpm/global/5/.pnpm/openclaw@2026.3.13_@discordjs+opus@0.10.0_@napi-rs+canvas@0.1.97_@types+express@5.0.6_node-llama-cpp@3.16.2/node_modules/openclaw/extensions/feishu/src/bot.ts"

# 备份
cp "$BOT_TS" "${BOT_TS}.backup"

# 在 import 部分添加译文拦截器导入（在第 35 行之后）
sed -i '35a\
import { tryProcessYiwenVideoMessage } from "../../../../../../../../.openclaw/workspace/scripts/yiwen-agent-integration.js";' "$BOT_TS"

# 在去重检查后添加拦截器调用（在 "let ctx = parseFeishuMessageEvent" 之前）
sed -i '/let ctx = parseFeishuMessageEvent(event, botOpenId, botName);/i\
  // === 译文 AGENT 拦截器 START ===\
  try {\
    const yiwenProcessed = await tryProcessYiwenVideoMessage({\
      event,\
      account,\
      botName: botName ?? account.config?.botName,\
      botOpenId,\
      log,\
      sendMessage: async ({ to, text }) => {\
        await sendMessageFeishu({ cfg, to: `chat:${to}`, text, accountId: account.accountId });\
      },\
    });\
    if (yiwenProcessed) {\
      log(`feishu[${account.accountId}]: video message processed by 译文 AGENT`);\
      return;\
    }\
  } catch (err) {\
    log(`feishu[${account.accountId}]: 译文 AGENT error: ${String(err)}`);\
  }\
  // === 译文 AGENT 拦截器 END ===
' "$BOT_TS"

echo "✅ bot.ts 修改完成"
echo "请重启 OpenClaw: openclaw gateway restart"
