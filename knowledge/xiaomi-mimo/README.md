# 小米 MiMo 文档知识库

**创建时间**: 2026-03-20 17:56
**最后更新**: 2026-03-20 18:00
**来源**: https://platform.xiaomimimo.com

## 文件列表

| 文件 | 描述 |
|------|------|
| README.md | 本索引文件 |
| 00-welcome.md | 欢迎页面 |
| 01-api-docs.md | API 文档详情 |

## 模型信息

| 模型 ID | 名称 | 上下文 | 默认 max_tokens | 默认 temperature | thinking |
|---------|------|---------|-----------------|------------------|----------|
| `mimo-v2-pro` | MiMo-V2-Pro | 131K | 131072 | 1.0 | enabled |
| `mimo-v2-omni` | MiMo-V2-Omni | 128K | 32768 | 1.0 | enabled |
| `mimo-v2-flash` | MiMo-V2-Flash | 64K | 65536 | 0.3 | disabled |
| `mimo-v2-tts` | MiMo-V2-TTS | 8K | 8192 | 0.6 | 不支持 |

## API 信息

- **Base URL**: `https://api.xiaomimimo.com/v1`
- **认证方式**: 
  - `api-key: $MIMO_API_KEY`
  - 或 `Authorization: Bearer $MIMO_API_KEY`
- **接口类型**: OpenAI 兼容 (`openai-completions`)
- **特性支持**:
  - ✅ 思考模式（pro/omni/flash）
  - ✅ 函数调用
  - ✅ 联网搜索
  - ✅ 多模态输入（图像/音频/视频）
  - ✅ 语音合成（仅 tts）

## 已配置模型

在 `openclaw.json` 中已配置：
- `xiaomi/mimo-v2-pro`
- `xiaomi/mimo-v2-omni`
- `xiaomi/mimo-v2-flash`
- `xiaomi/mimo-v2-tts`

## 更新日志

- 2026-03-20: 初始版本，完成 API 文档抓取和配置
