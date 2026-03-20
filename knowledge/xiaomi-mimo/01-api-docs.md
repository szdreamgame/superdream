# 小米 MiMo API 文档

**抓取时间**: 2026-03-20 17:56
**来源**: https://platform.xiaomimimo.com/#/docs/api/chat/openai-api

---

## 请求地址

```
POST https://api.xiaomimimo.com/v1/chat/completions
```

## 请求头

认证方式（二选一）：

**方式一**：
```
api-key: $MIMO_API_KEY
Content-Type: application/json
```

**方式二**：
```
Authorization: Bearer $MIMO_API_KEY
Content-Type: application/json
```

## 可用模型

| 模型 ID | 描述 | 默认 max_tokens | 默认 temperature | 默认 thinking |
|---------|------|-----------------|------------------|---------------|
| `mimo-v2-pro` | 万亿参数多模态模型 | 131072 | 1.0 | enabled |
| `mimo-v2-omni` | 全能多模态模型 | 32768 | 1.0 | enabled |
| `mimo-v2-tts` | 语音合成模型 | 8192 | 0.6 | 不支持 |
| `mimo-v2-flash` | 快速模型 | 65536 | 0.3 | disabled |

## 模型参数详情

### MiMo-V2-Pro
- **上下文窗口**: 未明确（推测 128K+）
- **默认 max_completion_tokens**: 131072
- **默认 temperature**: 1.0
- **默认 thinking**: enabled
- **特点**: 万亿参数，面向 Agent 时代，融合全模态感知与拟人级交互

### MiMo-V2-Omni
- **上下文窗口**: 未明确（推测 128K+）
- **默认 max_completion_tokens**: 32768
- **默认 temperature**: 1.0
- **默认 thinking**: enabled
- **特点**: 全能多模态

### MiMo-V2-Flash
- **默认 max_completion_tokens**: 65536
- **默认 temperature**: 0.3
- **默认 thinking**: disabled
- **特点**: 快速响应

### MiMo-V2-TTS
- **默认 max_completion_tokens**: 8192（范围：0-8192）
- **默认 temperature**: 0.6
- **thinking**: 不支持
- **特点**: 语音合成，支持 audio 输出

## 请求体参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `model` | string | 是 | - | 模型 ID：`mimo-v2-pro`, `mimo-v2-omni`, `mimo-v2-tts`, `mimo-v2-flash` |
| `messages` | array | 是 | - | 对话消息列表 |
| `max_completion_tokens` | integer | 否 | 见上 | 生成 token 上限 |
| `temperature` | number | 否 | 见上 | 采样温度 (0-1.5) |
| `top_p` | number | 否 | 0.95 | 核采样阈值 (0.01-1.0) |
| `stream` | boolean | 否 | false | 是否流式输出 |
| `thinking.type` | string | 否 | 见上 | `enabled` 或 `disabled` |
| `frequency_penalty` | number | 否 | 0 | 频率惩罚 (-2.0 到 2.0) |
| `presence_penalty` | number | 否 | 0 | 存在惩罚 (-2.0 到 2.0) |
| `stop` | string/array | 否 | null | 停止序列（最多 4 个） |
| `tools` | array | 否 | - | 工具列表（支持 function, web_search） |
| `tool_choice` | string | 否 | auto | 工具选择策略 |
| `response_format` | object | 否 | - | 响应格式（text 或 json_object） |
| `audio` | object | 否 | - | 音频输出参数（仅 mimo-v2-tts 支持） |

## 示例请求

```bash
curl --location --request POST 'https://api.xiaomimimo.com/v1/chat/completions' \
  --header 'api-key: $MIMO_API_KEY' \
  --header 'Content-Type: application/json' \
  --data-raw '{
    "model": "mimo-v2-pro",
    "messages": [
      {
        "role": "system",
        "content": "You are MiMo, an AI assistant developed by Xiaomi."
      },
      {
        "role": "user",
        "content": "please introduce yourself"
      }
    ],
    "max_completion_tokens": 1024,
    "temperature": 1.0,
    "top_p": 0.95,
    "stream": false,
    "stop": null,
    "frequency_penalty": 0,
    "presence_penalty": 0,
    "thinking": {
      "type": "disabled"
    }
  }'
```

## 特性支持

| 特性 | mimo-v2-pro | mimo-v2-omni | mimo-v2-flash | mimo-v2-tts |
|------|-------------|--------------|---------------|-------------|
| 思考模式 | ✅ | ✅ | ✅ | ❌ |
| 函数调用 | ✅ | ✅ | ✅ | ❌ |
| 联网搜索 | ✅ | ✅ | ✅ | ❌ |
| 图像输入 | ✅ | ✅ | ✅ | ❌ |
| 音频输入 | ✅ | ✅ | ✅ | ❌ |
| 视频输入 | ✅ | ✅ | ✅ | ❌ |
| 语音合成 | ❌ | ❌ | ❌ | ✅ |
| 结构化输出 | ✅ | ✅ | ✅ | ❌ |

---

**更新时间**: 2026-03-20
