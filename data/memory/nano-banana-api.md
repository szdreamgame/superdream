# Nano Banana 绘画接口文档

## 接口信息

**接口名称**: Nano Banana 绘画 API  
**请求方式**: POST  
**响应方式**: stream 流式响应 或 回调接口 (webhook)

---

## 请求配置

### 请求头 Headers
```
Content-Type: application/json
```

### 请求参数 (JSON)

| 参数 | 类型 | 必填 | 示例 | 说明 |
|------|------|------|------|------|
| **model** | string | ✅ 必填 | `"nano-banana-fast"` | 模型选择（见下方模型列表） |
| **prompt** | string | ✅ 必填 | `"一只可爱的猫咪在草地上玩耍"` | 绘画提示词 |
| **urls** | array | ❌ 可选 | `["https://example.com/img.png"]` | 参考图 URL 或 Base64 |
| **aspectRatio** | string | ❌ 可选 | `"auto"` | 输出图像比例（默认 auto） |
| **imageSize** | string | ❌ 可选 | `"1K"` | 输出图像大小（默认 1K） |
| **webHook** | string | ❌ 可选 | `"https://your-webhook.com/callback"` | 回调地址，填 `"-1"` 则立即返回 id |
| **shutProgress** | boolean | ❌ 可选 | `false` | 关闭进度回复，默认 false |

---

## 支持的模型 (model)

```
nano-banana-2
nano-banana-fast
nano-banana
nano-banana-pro
nano-banana-pro-vt
nano-banana-pro-cl
nano-banana-pro-vip
nano-banana-pro-4k-vip
```

---

## 支持的比例 (aspectRatio)

```
auto (默认)
1:1
16:9
9:16
4:3
3:4
3:2
2:3
5:4
4:5
21:9
```

---

## 支持的图像大小 (imageSize)

**适用模型**: nano-banana-2, nano-banana-pro, nano-banana-pro-vt, nano-banana-pro-cl

```
1K (默认)
2K
4K
```

**注意**:
- nano-banana-pro-vip 只支持 1K、2K
- nano-banana-pro-4k-vip 只支持 4K
- 分辨率越高，生成时间越长

---

## 响应参数

### 流式响应 / WebHook 响应

| 参数 | 类型 | 示例 | 说明 |
|------|------|------|------|
| **id** | string | `"f44bcf50-f2d0-4c26-a467-26f2014a771b"` | 任务 ID |
| **results** | array | `[{"url": "https://...", "content": "..."}]` | 结果数组 |
| **results[].url** | string | `"https://example.com/generated-image.jpg"` | 图片 URL（**有效期 2 小时**） |
| **results[].content** | string | `"这是一只可爱的猫咪..."` | 回复内容 |
| **progress** | number | `100` | 任务进度 (0~100) |
| **status** | string | `"succeeded"` | 任务状态 |
| **failure_reason** | string | `"error"` | 失败原因 |
| **error** | string | `"Invalid input parameters"` | 失败详细信息 |

---

## 任务状态 (status)

| 状态 | 说明 |
|------|------|
| `"running"` | 进行中 |
| `"succeeded"` | 成功 |
| `"failed"` | 失败 |

---

## 失败原因 (failure_reason)

| 原因 | 说明 |
|------|------|
| `"output_moderation"` | 输出违规 |
| `"input_moderation"` | 输入违规 |
| `"error"` | 其他错误 |

**提示**: 当触发 `"error"` 时，可尝试重新提交任务来确保系统稳定性。

---

## WebHook 回调模式

### 使用方式
设置 `webHook` 参数为回调地址，或填 `"-1"` 立即返回任务 ID。

### 回调请求
**请求头**: `Content-Type: application/json`  
**请求方法**: POST

### WebHook 结果格式

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "id": "f44bcf50-f2d0-4c26-a467-26f2014a771b"
  }
}
```

| 参数 | 类型 | 示例 | 说明 |
|------|------|------|------|
| **code** | number | `0` | 状态码：0 为成功 |
| **msg** | string | `"success"` | 状态信息 |
| **data.id** | string | `"f44bcf50-..."` | 任务 ID，对应回调数据 |

---

## 使用示例

### 示例 1: 流式响应（同步等待）

```bash
curl -X POST "https://api.nanobanana.ai/v1/generate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "nano-banana-fast",
    "prompt": "一只可爱的猫咪在草地上玩耍",
    "aspectRatio": "16:9",
    "imageSize": "1K"
  }'
```

### 示例 2: WebHook 回调（异步）

```bash
curl -X POST "https://api.nanobanana.ai/v1/generate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "nano-banana-fast",
    "prompt": "一位 25 岁的女性角色，长发，穿着现代休闲装",
    "webHook": "https://your-server.com/callback",
    "shutProgress": true
  }'
```

### 示例 3: 立即返回 ID（轮询模式）

```bash
curl -X POST "https://api.nanobanana.ai/v1/generate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "nano-banana-fast",
    "prompt": "城市街头场景，路边停放着私家车，周围有行人",
    "webHook": "-1",
    "aspectRatio": "16:9"
  }'
```

响应：
```json
{
  "id": "f44bcf50-f2d0-4c26-a467-26f2014a771b"
}
```

然后用 ID 轮询结果：
```bash
curl -X GET "https://api.nanobanana.ai/v1/result/f44bcf50-f2d0-4c26-a467-26f2014a771b" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

---

## 注意事项

1. **图片 URL 有效期**: 生成的图片 URL 有效期为 **2 小时**，需及时下载或转存
2. **生成时间**: 分辨率越高，生成时间越长
3. **错误处理**: 遇到 `"error"` 状态时，可尝试重新提交
4. **内容审核**: 注意输入和输出的内容合规，避免触发审核机制
5. **API Key**: 需要有效的 API Key（用户需提供）

---

## 集成到飞书表格流程

### 流程设计

```
1. 监听表格状态 → "待生成图片"
   ↓
2. 读取"修改后角色"、"修改后场景"
   ↓
3. 调用 Nano Banana API
   - 角色提示词 → 生成角色图
   - 场景提示词 → 生成场景图
   ↓
4. 下载图片（URL 有效期 2 小时）
   ↓
5. 上传到飞书云文档
   ↓
6. 回写图片链接到表格
   ↓
7. 更新状态 → "图片已完成"
```

### 表格字段需求

| 字段名 | 类型 | 说明 |
|--------|------|------|
| 角色设定图 | 附件/URL | 生成的角色图片 |
| 场景设定图 | 附件/URL | 生成的场景图片 |
| 图片生成状态 | 单选 | 待生成/生成中/已完成/失败 |
| 图片生成时间 | 日期 | 完成时间 |
| 图片任务 ID | 文本 | Nano Banana 任务 ID（用于轮询） |

---

## 待确认信息

- [ ] API 基础 URL（示例中使用的是假设地址）
- [ ] API Key 获取方式
- [ ] 认证方式（Bearer Token 或其他）
- [ ] 是否有速率限制
- [ ] 价格/配额信息

---

**文档创建时间**: 2026-03-16  
**最后更新**: 2026-03-16
