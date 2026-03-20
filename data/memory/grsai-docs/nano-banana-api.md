---
title: Nano Banana 绘画接口详细文档
source_url: https://grsai.ai/zh/dashboard/documents/nano-banana
crawled_date: 2026-03-16
tags: [nano-banana, api, image-generation, drawing]
---

# Nano Banana 绘画接口详细文档

> 🎨 AI 图像生成 API - 支持多种模型和分辨率

---

## 📋 接口概览

| 项目 | 值 |
|------|-----|
| **接口名称** | Nano Banana 绘画 API |
| **请求方式** | POST |
| **响应方式** | Stream 流式响应 或 WebHook 回调 |
| **Content-Type** | `application/json` |

---

## 🔌 请求配置

### 接口地址

```
POST /v1/draw/nano-banana
```

### 请求头

```http
Content-Type: application/json
Authorization: Bearer YOUR_API_KEY
```

### 请求参数

| 参数 | 类型 | 必填 | 示例 | 说明 |
|------|------|------|------|------|
| **model** | string | ✅ | `"nano-banana-fast"` | 模型选择 |
| **prompt** | string | ✅ | `"一只可爱的猫咪"` | 绘画提示词 |
| **urls** | array | ❌ | `["https://..."]` | 参考图 URL |
| **aspectRatio** | string | ❌ | `"16:9"` | 输出比例 |
| **imageSize** | string | ❌ | `"1K"` | 输出尺寸 |
| **webHook** | string | ❌ | `"https://..."` | 回调地址 |
| **shutProgress** | boolean | ❌ | `false` | 关闭进度 |

---

## 🎯 支持的模型

```
nano-banana-2
nano-banana-fast          ← 推荐用于快速测试
nano-banana
nano-banana-pro
nano-banana-pro-vt
nano-banana-pro-cl
nano-banana-pro-vip
nano-banana-pro-4k-vip    ← 最高质量
```

---

## 📐 支持的比例

| 比例 | 适用场景 |
|------|----------|
| `auto` | 自动（默认） |
| `1:1` | 正方形头像 |
| `16:9` | 横屏壁纸 |
| `9:16` | 手机壁纸 |
| `4:3` | 传统照片 |
| `3:4` | 竖版照片 |
| `3:2` | 标准照片 |
| `2:3` | 证件照 |
| `5:4` | 特殊比例 |
| `4:5` | 社交媒体 |
| `21:9` | 超宽屏 |

---

## 📏 支持的尺寸

### 适用模型
- nano-banana-2
- nano-banana-pro
- nano-banana-pro-vt
- nano-banana-pro-cl
- nano-banana-pro-vip (仅 1K, 2K)
- nano-banana-pro-4k-vip (仅 4K)

### 尺寸选项
| 尺寸 | 说明 | 生成时间 |
|------|------|----------|
| `1K` | 标准（默认） | 快 |
| `2K` | 高清 | 中 |
| `4K` | 超高清 | 慢 |

---

## 📤 请求示例

### 示例 1: 基础调用（流式响应）

```bash
curl -X POST "https://api.grsai.ai/v1/draw/nano-banana" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "nano-banana-fast",
    "prompt": "一只可爱的猫咪在草地上玩耍",
    "aspectRatio": "16:9",
    "imageSize": "1K"
  }'
```

### 示例 2: WebHook 回调

```bash
curl -X POST "https://api.grsai.ai/v1/draw/nano-banana" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "nano-banana-pro",
    "prompt": "一位 25 岁的女性角色，长发，现代休闲装",
    "webHook": "https://your-server.com/callback",
    "shutProgress": true,
    "aspectRatio": "9:16"
  }'
```

### 示例 3: 轮询模式

```bash
# 提交任务
curl -X POST "https://api.grsai.ai/v1/draw/nano-banana" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "nano-banana-fast",
    "prompt": "城市街头场景，私家车，行人",
    "webHook": "-1",
    "aspectRatio": "16:9"
  }'

# 响应：{"id": "f44bcf50-f2d0-4c26-a467-26f2014a771b"}

# 查询结果
curl -X GET "https://api.grsai.ai/v1/draw/result" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{"id": "f44bcf50-f2d0-4c26-a467-26f2014a771b"}'
```

---

## 📥 响应参数

### 流式响应 / WebHook 响应

```json
{
  "id": "f44bcf50-f2d0-4c26-a467-26f2014a771b",
  "results": [
    {
      "url": "https://example.com/generated-image.jpg",
      "content": "这是一只可爱的猫咪"
    }
  ],
  "progress": 100,
  "status": "succeeded",
  "failure_reason": null,
  "error": null
}
```

| 参数 | 类型 | 说明 |
|------|------|------|
| **id** | string | 任务 ID |
| **results** | array | 结果数组 |
| **results[].url** | string | 图片 URL（⚠️ 有效期 2 小时） |
| **results[].content** | string | 回复内容 |
| **progress** | number | 进度 0-100 |
| **status** | string | 任务状态 |
| **failure_reason** | string | 失败原因 |
| **error** | string | 错误详情 |

---

## 🚦 任务状态

| 状态 | 说明 |
|------|------|
| `running` | 进行中 |
| `succeeded` | 成功 ✅ |
| `failed` | 失败 ❌ |

---

## ⚠️ 失败原因

| 原因 | 说明 | 解决方案 |
|------|------|----------|
| `output_moderation` | 输出违规 | 修改提示词 |
| `input_moderation` | 输入违规 | 检查参考图 |
| `error` | 其他错误 | 重试任务 |

---

## 🔄 WebHook 回调

### 回调格式

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "id": "f44bcf50-f2d0-4c26-a467-26f2014a771b"
  }
}
```

### 回调参数

| 参数 | 类型 | 说明 |
|------|------|------|
| **code** | number | 状态码（0=成功） |
| **msg** | string | 状态信息 |
| **data.id** | string | 任务 ID |

---

## 💡 最佳实践

### 1. 图片保存
⚠️ **图片 URL 有效期仅 2 小时**，生成后应立即下载或转存。

```python
import requests

# 下载图片
response = requests.get(image_url)
with open('character.png', 'wb') as f:
    f.write(response.content)
```

### 2. 错误重试
```python
def generate_with_retry(prompt, max_retries=3):
    for i in range(max_retries):
        result = call_api(prompt)
        if result['status'] == 'succeeded':
            return result
        time.sleep(2 ** i)  # 指数退避
    raise Exception("生成失败")
```

### 3. 提示词优化
```
好的提示词 = 主体 + 细节 + 风格 + 质量

示例:
"一位 25 岁的女性角色，黑色长发，穿着现代休闲装，
站在城市街头，写实风格，高质量，细节丰富"
```

---

## 🔗 相关资源

- [GRS AI 控制台](https://grsai.ai/zh/dashboard)
- [积分查询](https://grsai.ai/zh/dashboard/credits)
- [文档首页](./README.md)

---

*文档来源：GRS AI 官方文档 | 整理时间：2026-03-16*
