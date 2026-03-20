# AGENT 集成文档 - 译文 & 画语

## 概述

将译文和画语两个 AGENT 集成到 OpenClaw 飞书插件中，实现自动消息处理。

---

## 文件结构

```
/root/.openclaw/workspace/interceptors/
├── agent-message-interceptor.js      # 主拦截器（译文 + 画语）
├── feishu-bitable-wrapper.js         # 飞书表格 API 包装器
├── video-message-interceptor.js      # 旧版本（已废弃）
└── AGENT-INTEGRATION.md              # 本文档
```

---

## 配置信息

### 译文 AGENT

| 配置项 | 值 |
|--------|-----|
| 专属群 | 漫剧 - 文案评审群 |
| 群 ID | `oc_95a9882e1aca9546c1930b2d27660a6a` |
| Bot 名称 | 译文 |
| 功能 | 视频识别 → 文字稿 + 剧本 |
| 表格 | `GHrubiTjnayG4fsWP2IcJIotnfc` (tbl8ik4qLltAlXvp) |
| Coze URL | `https://ny5xtnd234.coze.site/run` |

### 画语 AGENT

| 配置项 | 值 |
|--------|-----|
| 专属群 | AI 图片生成工作室 |
| 群 ID | `oc_f22ffe36d557729c0d77f8b11c74e0bd` |
| Bot 名称 | 画语 |
| 功能 | 图片生成指令响应 |
| 表格 | `GHrubiTjnayG4fsWP2IcJIotnfc` (tbl8ik4qLltAlXvp) |
| GRS API | `https://grsai.dakka.com.cn` |

---

## 集成位置

**飞书插件**: `/home/admin/.local/share/pnpm/global/5/.pnpm/openclaw@2026.3.2*/node_modules/openclaw/extensions/feishu/src/bot.ts`

### 导入语句（第 39-40 行）

```typescript
// 视频处理拦截器
import { tryProcessAgentMessage as tryProcessAgentMessageInterceptor } from "../../../../../../../../.openclaw/workspace/interceptors/agent-message-interceptor.js";
```

### 调用位置（约第 867-893 行）

```typescript
// === AGENT 消息拦截器 START (译文 + 画语) ===
try {
  const videoProcessed = await tryProcessAgentMessageInterceptor({
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
    log(`feishu[${account.accountId}]: message processed by AGENT interceptor`);
    return; // 已处理，不再继续
  }
} catch (err) {
  log(`feishu[${account.accountId}]: AGENT interceptor error: ${String(err)}`);
  // 继续正常处理流程
}
// === AGENT 消息拦截器 END ===
```

---

## 使用方法

### 译文 AGENT

在**漫剧 - 文案评审群**中：

1. **上传视频文件**
2. **@译文** 或 **@feishubot**
3. 等待处理（约 30-60 秒）
4. 查看识别结果和表格记录

**示例**：
```
[视频文件] @译文
```

**输出**：
```
✅ **识别完成！**

**文字稿**：
你是做什么工作的？这不刚从缅甸回来...

**主要角色**：
介绍人
相亲女

📊 **已创建评审记录**
状态：待评审
```

### 画语 AGENT

在**AI 图片生成工作室**群中：

1. **发送图片生成命令**
2. **@画语** 或 **@feishubot**（可选）

**支持命令**：
- `/生成 角色图 一个勇敢的骑士`
- `/画 场景 中世纪城堡`
- `/图片 角色 魔法师`
- `/画语 角色 精灵公主`

**示例**：
```
/生成 角色图 一个穿着红色斗篷的魔法师
```

**输出**：
```
✅ **生成完成！**

描述：一个穿着红色斗篷的魔法师

![图片 1](https://...)
![图片 2](https://...)

⚠️ 图片 URL 有效期 2 小时，请及时保存
```

---

## 处理流程

### 译文 AGENT 流程

```
1. 接收飞书视频消息
   ↓
2. 检查群 ID + @Bot
   ↓
3. 获取视频 URL
   ↓
4. 调用 Coze API 识别
   ↓
5. 提取文字稿 + 剧本 + 角色
   ↓
6. 创建飞书表格记录
   ↓
7. 发送结果到群聊
```

### 画语 AGENT 流程

```
1. 接收群消息
   ↓
2. 检查命令前缀（/生成、/画等）
   ↓
3. 解析命令参数
   ↓
4. 调用 GRS AI API
   ↓
5. 获取图片 URL
   ↓
6. 发送结果到群聊
```

---

## 故障排查

### 问题 1：AGENT 无响应

**检查**：
1. Gateway 是否运行：`openclaw gateway status`
2. bot.ts 修改是否生效：检查日志
3. 群 ID 是否正确

**解决**：
```bash
openclaw gateway restart
```

### 问题 2：表格记录创建失败

**检查**：
1. 飞书 App 权限是否充足
2. Token 是否有效
3. 表格 ID 是否正确

**日志**：
```bash
tail -f /tmp/openclaw-0/openclaw-*.log | grep "飞书表格"
```

### 问题 3：Coze/GRS API 调用失败

**检查**：
1. Token 是否过期
2. 网络是否通畅
3. API 额度是否充足

---

## 日志位置

```bash
# OpenClaw 主日志
tail -f /tmp/openclaw-0/openclaw-*.log

# 筛选 AGENT 日志
tail -f /tmp/openclaw-0/openclaw-*.log | grep "AGENT\|译文\|画语"
```

---

## 下一步优化

1. **画语 AGENT 表格轮询** - 自动检查表格任务并处理
2. **结果缓存** - 避免重复处理相同视频/图片
3. **错误重试** - API 失败时自动重试
4. **进度通知** - 长时间任务发送进度更新

---

**创建时间**: 2026-03-17  
**最后更新**: 2026-03-17  
**维护**: 潘泽霖团队
