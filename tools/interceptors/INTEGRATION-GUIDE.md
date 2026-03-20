# 飞书视频处理集成指南

## 概述

本文档说明如何将视频处理功能集成到飞书插件中，实现自动处理漫剧群的视频消息。

## 文件结构

```
/root/.openclaw/workspace/interceptors/
├── video-message-interceptor.js    # 视频处理拦截器（已创建）
├── feishu-client-wrapper.js         # 飞书客户端包装器（已创建）
└── INTEGRATION-GUIDE.md             # 本文档
```

## 集成步骤

### 方案 A：修改飞书插件 bot.ts（推荐）

#### 1. 在 bot.ts 顶部添加导入

**文件**: `/home/admin/.local/share/pnpm/global/5/.pnpm/openclaw@2026.3.2*/node_modules/openclaw/extensions/feishu/src/bot.ts`

在文件顶部（其他 import 之后）添加：

```typescript
// 视频处理拦截器
import { tryProcessVideoMessage as tryProcessVideoMessageInterceptor } from "../../../../../../.openclaw/workspace/interceptors/video-message-interceptor.js";
```

#### 2. 在 handleFeishuMessage 函数中添加调用

**位置**: 在 `handleFeishuMessage` 函数的开始部分，在 dedup 检查之后

找到以下代码（约第 853-860 行）：

```typescript
// Persistent dedup survives restarts and reconnects.
if (!(await tryRecordMessagePersistent(messageId, account.accountId, log))) {
  log(`feishu: skipping duplicate message ${messageId}`);
  return;
}
```

在其**之后**添加：

```typescript
// === 视频处理拦截器 START ===
try {
  const videoProcessed = await tryProcessVideoMessageInterceptor({
    event,
    account,
    botName: botName ?? account.config?.botName,
    botOpenId,
    log,
    sendMessage: async ({ to, text }: { to: string; text: string }) => {
      await sendMessageFeishu({
        cfg,
        to: `chat:${to}`,
        text,
        accountId: account.accountId,
      });
    },
  });
  
  if (videoProcessed) {
    log(`feishu[${account.accountId}]: video message processed by interceptor`);
    return; // 已处理，不再继续
  }
} catch (err) {
  log(`feishu[${account.accountId}]: video interceptor error: ${String(err)}`);
  // 继续正常处理流程
}
// === 视频处理拦截器 END ===
```

#### 3. 重启 OpenClaw Gateway

```bash
openclaw gateway restart
```

### 方案 B：使用 OpenClaw 配置（无需修改插件代码）

如果不想修改插件代码，可以创建一个独立的监听服务：

#### 1. 创建独立监听脚本

```javascript
// /root/.openclaw/workspace/video-listener.js
const { tryProcessVideoMessage } = require('./interceptors/video-message-interceptor.js');

// 通过 OpenClaw API 监听飞书消息
// 需要 OpenClaw 提供消息钩子 API
```

#### 2. 在 OpenClaw 配置中注册

编辑 `/root/.openclaw/openclaw.json`，添加钩子配置。

---

## 配置说明

### 目标群聊

- **群名称**: 漫剧 - 文案评审群
- **群 ID**: `oc_95a9882e1aca9546c1930b2d27660a6a`

### 触发条件

- 消息类型：视频
- 提及：@译文 或 @feishubot

### Coze 工作流

- **URL**: `https://ny5xtnd234.coze.site/run`
- **Token**: 存储在 `/root/.openclaw/credentials/coze.json`

---

## 测试方法

### 1. 在漫剧群发送测试视频

```
[上传视频文件] @译文
```

### 2. 查看日志

```bash
# 查看 OpenClaw 日志
tail -f ~/.openclaw/logs/openclaw.log | grep "译文"
```

### 3. 预期输出

```
[译文拦截器] ✅ 匹配成功，开始处理视频消息
[译文拦截器] 消息 ID: om_xxx
[译文拦截器] 群聊 ID: oc_xxx
[译文拦截器] 视频 URL: https://...
[译文拦截器] 调用 Coze API: https://...
[译文拦截器] Coze 响应状态：200
[译文拦截器] ✅ 处理完成！
```

---

## 故障排查

### 问题 1：拦截器未触发

**检查**:
1. 确认群 ID 正确
2. 确认@了 Bot
3. 确认消息类型是视频

### 问题 2：Coze API 调用失败

**检查**:
1. Token 是否过期
2. 视频 URL 是否公网可访问
3. 视频是否需要先上传到 OSS

### 问题 3：飞书消息发送失败

**检查**:
1. 飞书 App 权限是否充足
2. `receive_id_type` 参数位置是否正确
3. `content` 字段是否双重 JSON 编码

---

## 下一步

完成集成后，建议：

1. **添加配置选项** - 在 `openclaw.json` 中添加视频处理开关
2. **支持更多群聊** - 将目标群 ID 配置化
3. **结果缓存** - 对相同视频进行去重
4. **错误重试** - 添加重试机制处理临时失败

---

**创建时间**: 2026-03-17  
**最后更新**: 2026-03-17
