# GRS AI 知识库完整索引

> 📚 自动同步的 GRS AI 产品文档库

**最后更新**: 2026-03-16  
**文档总数**: 4  
**源地址**: https://grsai.ai/zh/dashboard/documents

---

## 📖 可用文档

### 1. Nano Banana API
- **文件**: [`nano-banana-api.md`](./nano-banana-api.md)
- **源链接**: https://grsai.ai/zh/dashboard/documents/nano-banana
- **内容**: Nano Banana 绘画接口完整文档
- **状态**: ✅ 已同步

### 2. GPT Image API
- **文件**: `gpt-image.md` (待爬取)
- **源链接**: https://grsai.ai/zh/dashboard/documents/gpt-image
- **内容**: GPT Image 图像生成 API
- **状态**: ⏳ 待处理

### 3. Other API
- **文件**: `other.md` (待爬取)
- **源链接**: https://grsai.ai/zh/dashboard/documents/other
- **内容**: 其他 API 接口
- **状态**: ⏳ 待处理

### 4. Nano Banana 2 生成工具
- **文件**: [`nano-banana-generator.py`](../../scripts/nano-banana-generator.py)
- **类型**: Python 脚本
- **功能**: 自动监听表格并生成角色/场景设定图
- **状态**: ✅ 已实现

---

## 🚀 快速开始

### 使用 Nano Banana 2 生成图片

#### 1. 配置 API Key

```bash
# 设置环境变量
export GRS_API_KEY="your_api_key_here"
```

#### 2. 测试 API

```bash
# 运行测试
python3 /root/.openclaw/workspace/scripts/nano-banana-generator.py test
```

#### 3. 启动服务

```bash
# 后台运行
nohup python3 /root/.openclaw/workspace/scripts/nano-banana-generator.py > /tmp/nano-banana.log 2>&1 &

# 查看日志
tail -f /tmp/nano-banana.log
```

---

## 📋 飞书表格集成流程

### 表格字段要求

| 字段名 | 类型 | 说明 |
|--------|------|------|
| 修改后角色 | 长文本 | 角色描述（用于生成角色图） |
| 修改后场景 | 长文本 | 场景描述（用于生成场景图） |
| 角色设定图 | 附件/URL | 生成的角色图片 |
| 场景设定图 | 附件/URL | 生成的场景图片 |
| 图片生成状态 | 单选 | 待生成/生成中/已完成/失败 |
| 图片生成时间 | 日期 | 完成时间 |

### 工作流程

```
1. 表格状态 → "待生成图片"
   ↓
2. 脚本轮询检测到新任务
   ↓
3. 读取"修改后角色"和"修改后场景"
   ↓
4. 调用 Nano Banana API
   - 角色提示词 → 生成角色图 (3:4)
   - 场景提示词 → 生成场景图 (16:9)
   ↓
5. 下载图片（URL 有效期 2 小时）
   ↓
6. 上传到飞书云文档
   ↓
7. 回写图片链接到表格
   ↓
8. 更新状态 → "图片已完成"
```

---

## 🛠️ 工具脚本

| 脚本 | 功能 | 位置 |
|------|------|------|
| `grsai-doc-crawler.py` | 爬取 GRS AI 文档 | `scripts/grsai-doc-crawler.py` |
| `nano-banana-generator.py` | Nano Banana 2 图片生成 | `scripts/nano-banana-generator.py` |
| `extract_grs_docs.py` | 提取 HTML 文档为 Markdown | `scripts/extract_grs_docs.py` |

---

## 📂 目录结构

```
/root/.openclaw/workspace/
├── scripts/
│   ├── grsai-doc-crawler.py       # 文档爬虫
│   ├── nano-banana-generator.py   # 图片生成工具
│   └── extract_grs_docs.py        # HTML 提取工具
│
└── memory/
    ├── grsai-docs/                 # GRS AI 文档库
    │   ├── README.md              # 主入口
    │   ├── INDEX.md               # 自动索引
    │   ├── nano-banana.md         # 爬取的原始文档
    │   ├── nano-banana-api.md     # 完整 API 文档
    │   └── documents.json         # JSON 索引
    │
    └── nano-banana-api.md         # 手动整理的 API 文档
```

---

## 🔧 配置说明

### 环境变量

```bash
# GRS AI API Key（必需）
export GRS_API_KEY="your_api_key"

# 可选配置
export GRS_API_HOST="https://grsai.dakka.com.cn"  # 国内直连
export BITABLE_APP_TOKEN="GHrubiTjnayG4fsWP2IcJIotnfc"
export BITABLE_TABLE_ID="tbl8ik4qLltAlXvp"
```

### API 配置

```python
# Nano Banana 模型选择
NANO_BANANA_MODEL = "nano-banana-2"  # 或 nano-banana-fast, nano-banana-pro

# 图片参数
DEFAULT_ASPECT_RATIO = "16:9"  # 1:1, 16:9, 9:16, 3:4, 4:3 等
DEFAULT_IMAGE_SIZE = "1K"      # 1K, 2K, 4K

# 轮询配置
POLL_INTERVAL = 60  # 秒
```

---

## ⚠️ 注意事项

1. **图片 URL 有效期**: 生成的图片 URL 有效期为 **2 小时**，需及时下载或转存
2. **API Key 安全**: 不要将 API Key 提交到代码仓库
3. **生成时间**: 分辨率越高，生成时间越长（1K 约 10-30 秒，4K 约 1-3 分钟）
4. **错误处理**: 遇到 `"error"` 状态时，脚本会自动重试（最多 30 次）
5. **飞书上传**: 需要实现飞书云文档上传 API（当前为占位实现）

---

## 📝 待办事项

- [ ] 实现飞书云文档上传功能
- [ ] 实现飞书表格轮询 API
- [ ] 添加 GPT Image 文档到知识库
- [ ] 添加 Other API 文档到知识库
- [ ] 添加 WebHook 支持（实时回调）
- [ ] 添加批量生成支持
- [ ] 添加图片风格预设

---

## 🔗 相关资源

- [GRS AI 控制台](https://grsai.ai/zh/dashboard)
- [Nano Banana 文档](./nano-banana-api.md)
- [飞书多维表格 API](https://open.feishu.cn/document/ukTMukTMukTM/uEjNwUjL2YDM14SM2ATN)

---

*自动生成 by OpenClaw | Powered by GRS AI*
