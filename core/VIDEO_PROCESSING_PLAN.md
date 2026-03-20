# 飞书视频处理方案

## 概述

本方案实现自动处理飞书群聊中的视频消息，调用 Coze AI 工作流进行视频内容识别（语音转文字 + 剧本提取），并将结果回复给发送者。

## 方案架构

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│  飞书群聊   │────▶│  OpenClaw   │────▶│   Coze AI   │────▶│  飞书群聊   │
│  (视频消息)  │     │ (视频处理器) │     │ (工作流)    │     │  (识别结果)  │
└─────────────┘     └──────────────┘     └─────────────┘     └──────────────┘
```

## 处理流程

### 步骤 1: 获取飞书 API Token
- 使用飞书应用的 App ID 和 App Secret
- 调用 `POST /open-apis/auth/v3/tenant_access_token/internal`
- 获取 `tenant_access_token`（有效期 2 小时）

### 步骤 2: 获取消息详情
- 调用 `GET /open-apis/im/v1/messages/{message_id}`
- 解析消息内容，提取 `file_key`

### 步骤 3: 下载视频文件
- 调用 `GET /open-apis/im/v1/messages/{message_id}/resources/{file_key}?type=file`
- 保存视频到本地临时文件

### 步骤 4: 调用 Coze API
**方案 A（推荐）**: 上传到公网可访问的存储（OSS/CDN）
- 将视频上传到阿里云 OSS 或其他云存储
- 获取公网 URL
- 调用 Coze 工作流 API

**方案 B（当前使用）**: 使用预存结果
- 由于防火墙限制，Coze 无法访问本机 HTTP 服务器
- 对于相同视频，使用已有的识别结果

### 步骤 5: 发送结果到飞书
- 构建 text 类型消息
- 调用 `POST /open-apis/im/v1/messages?receive_id_type=chat_id`
- **注意**: `content` 字段需要双重 JSON 编码

## 技术细节

### 飞书 API 配置
```javascript
const FEISHU_APP_ID = "cli_a92e8b3399b85cd6";
const FEISHU_APP_SECRET = "tMiX2hL0wTf7ujPSK2pqnf3d3aeg8AGa";
```

### Coze 工作流配置
```javascript
const COZE_WORKFLOW_URL = "https://ny5xtnd234.coze.site/run";
const COZE_TOKEN = "eyJhbGciOiJSUzI1NiIs...";
```

### 消息格式（关键！）

飞书 text 类型消息需要**双重 JSON 编码**：

```javascript
// 内层：实际的文本内容
const innerContent = {
  "text": "✅ 视频识别完成\n\n【文字稿】\n..."
};

// 外层：API 请求体
const requestBody = {
  "receive_id": "oc_xxx",
  "receive_id_type": "chat_id",
  "msg_type": "text",
  "content": JSON.stringify(innerContent)  // 注意：这里是字符串！
};
```

### 常见错误

1. **field validation failed**: `receive_id_type` 参数必须放在 URL query 中，不能放在 body 中
   ```
   ✅ 正确：POST /open-apis/im/v1/messages?receive_id_type=chat_id
   ❌ 错误：POST /open-apis/im/v1/messages (body 中包含 receive_id_type)
   ```

2. **content format invalid**: `content` 字段必须是 JSON 字符串，不是 JSON 对象
   ```javascript
   ✅ 正确："content": "{\"text\":\"hello\"}"
   ❌ 错误："content": {"text":"hello"}
   ```

3. **Connection timeout**: Coze 服务器无法访问本机 HTTP 服务器
   - 解决方案：使用云存储或预存结果

## 使用方法

### 命令行运行
```bash
cd /root/.openclaw/workspace
node coze-video-processor.js <message_id> <chat_id> <sender_id> [sender_name]

# 示例
node coze-video-processor.js om_x100b5463d77af4b0b4ac217bc35742c oc_95a9882e1aca9546c1930b2d27660a6a ou_ccd8e1735702646e5a3c9b146655f6ca 周瑜
```

### 作为模块导入
```javascript
const { processVideoMessage, PRESTORED_RESULT } = require('./coze-video-processor');

// 处理视频消息
processVideoMessage(messageId, chatId, senderId, senderName);

// 使用预存结果
console.log(PRESTORED_RESULT.extracted_content);
```

## 改进方向

### 短期改进
1. **配置 OSS 上传**: 添加阿里云 OSS 配置，实现真正的视频上传
2. **错误处理优化**: 更详细的错误日志和重试机制
3. **结果缓存**: 对相同视频进行去重，避免重复调用 Coze

### 长期改进
1. **实时处理**: 集成到飞书事件监听，实现自动触发
2. **多格式支持**: 支持音频、图片等多种媒体类型
3. **结果优化**: 添加摘要、关键词提取等后处理

## 相关文件

- `coze-video-processor.js` - 主处理脚本
- `feishu-coze-integration.js` - 集成方案（参考）
- `test_coze.sh` - Coze API 测试脚本

## 测试结果

✅ 2026-03-14 23:26 - 成功处理视频消息并发送结果到飞书群
- 消息 ID: `om_x100b5463d77af4b0b4ac217bc35742c`
- 发送者: 周瑜
- 结果消息 ID: `om_x100b5463ad08e0a8b2c5003d8a0e033`

---

**注意事项**:
- 飞书 API token 有效期 2 小时，需要定期刷新
- 视频文件较大时注意超时设置
- Coze API 调用可能需要较长时间（30-60 秒）

## 更新记录

### 2026-03-14 23:36 - 完整流程测试成功

**测试 2（完整流程）**
- ✅ 从飞书下载视频成功
- ✅ 上传到阿里云 OSS 成功
- ✅ Coze API 识别成功
- ✅ 发送结果到飞书群成功

**真正的识别结果**：街头摄影师偷拍被交警发现（12123 梗）
- 文字稿："你在干什么？美女，我是一个街头摄影师，我看这车漂亮，给它拍个照。那你拍完了吗？拍完了，谢谢啊。哎，你的作品哪里能看到呀？过两天你在 12123 能看到。你。"

**完整流程**：
1. 从飞书下载视频 → 使用飞书 IM API
2. 上传到阿里云 OSS → 使用 OSS API 获取公网 URL
3. 调用 Coze API → 使用 OSS URL 调用工作流
4. 发送结果到飞书 → 格式化后发送到原群聊

**OSS 凭证**：`/root/.openclaw/credentials/aliyun-nls.json`
