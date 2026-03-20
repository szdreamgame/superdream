# OpenClaw 消息拦截器 - 译文视频处理

## 📋 配置说明

### 拦截器位置
`/root/.openclaw/workspace/interceptors/feishu_video.js`

### 触发条件
- **群聊**: `oc_95a9882e1aca9546c1930b2d27660a6a`（漫剧 - 文案评审群）
- **消息类型**: 视频文件
- **触发方式**: @译文 或 发送 `/文字` 等命令

### 处理流程
```
飞书消息 → 拦截器检查 → 匹配成功 → 调用 Coze → 返回结果
```

---

## 🔧 激活拦截器

### 方法 1：OpenClaw 配置（推荐）

在 OpenClaw 主配置中添加拦截器：

```json
{
  "interceptors": {
    "feishu_video": {
      "enabled": true,
      "path": "/root/.openclaw/workspace/interceptors/feishu_video.js",
      "priority": 10
    }
  }
}
```

### 方法 2：飞书插件配置

在飞书插件配置中添加消息处理器：

```javascript
// extensions/feishu/src/channel.ts
import { interceptFeishuMessage } from "../../../workspace/interceptors/feishu_video.js";

// 在消息处理逻辑中添加
if (message.chat_id === "oc_95a9882e1aca9546c1930b2d27660a6a") {
  const result = await interceptFeishuMessage(message);
  if (result) {
    return result; // 拦截并返回结果
  }
}
```

---

## 🚀 测试

在"漫剧 - 文案评审群"中：

1. 发送视频文件
2. @译文
3. 等待处理（30-60 秒）
4. 收到文字稿 + 剧本

---

## 📁 相关文件

| 文件 | 说明 |
|------|------|
| `feishu_video.js` | 拦截器脚本 |
| `../agents/message_handler.py` | Python 消息处理器 |
| `../tools/coze_transcribe.py` | Coze 调用工具 |
| `../skills/译文视频处理/SKILL.md` | 技能说明 |

---

## ⚠️ 注意事项

1. **优先级**: 拦截器优先级设为 10（高于默认处理）
2. **超时**: Coze 调用超时设为 300 秒
3. **文件大小**: 建议视频 < 100MB
4. **Token**: 定期检查 Coze Token 是否有效
