# 超梦 (小梦同学) - 完整备份索引

> **备份时间**: 2026-03-16 17:32  
> **当前版本**: OpenClaw 2026.3.8  
> **用途**: 用于 trae CN 升级实现

---

## 📋 目录结构

```
/root/.openclaw/workspace/
├── IDENTITY.md                 # 身份配置
├── memory/                     # 知识库
│   ├── prompts/               # 提示词模板
│   ├── agents/                # AGENT 配置
│   └── grsai-docs/            # GRS AI 文档
├── scripts/                    # 脚本文件
└── openclaw.json              # 主配置
```

---

## 📚 知识库文件清单

### 1. 身份配置
- **文件**: `IDENTITY.md`
- **内容**: 超梦（小梦同学）的身份定义和职责
- **重要性**: ⭐⭐⭐⭐⭐

### 2. 提示词模板库
- **文件**: `memory/prompts/image-generation.md`
- **内容**: 图片生成提示词模板（8 种角色风格 + 4 种场景风格）
- **维护人**: 周瑜
- **重要性**: ⭐⭐⭐⭐⭐

### 3. AGENT 配置
- **文件**: `memory/agents/image-generation-agent.md`
- **内容**: 画语 BOT 的完整配置文档
- **重要性**: ⭐⭐⭐⭐⭐

### 4. GRS AI 文档库
- `memory/grsai-docs/README.md` - 文档库索引
- `memory/grsai-docs/nano-banana.md` - 原始文档
- `memory/grsai-docs/nano-banana-api.md` - 完整 API 文档
- **重要性**: ⭐⭐⭐⭐

### 5. 配置文档
- `memory/feishu-app-config.md` - 飞书应用配置
- `memory/grsai-api-key.md` - GRS API Key 配置
- `memory/nano-banana-deployment.md` - 部署指南
- **重要性**: ⭐⭐⭐⭐⭐

---

## 🛠️ 脚本文件清单

### 1. 图片生成 AGENT（画语）
- **文件**: `scripts/nano-banana-agent.py`
- **功能**: 专属群图片生成 BOT
- **配置群**: `oc_f22ffe36d557729c0d77f8b11c74e0bd`
- **重要性**: ⭐⭐⭐⭐⭐

### 2. 图片生成完整脚本
- **文件**: `scripts/nano-banana-generator-full.py`
- **功能**: 飞书表格集成 + 图片生成
- **重要性**: ⭐⭐⭐⭐⭐

### 3. 图片生成简化脚本
- **文件**: `scripts/nano-banana-generator.py`
- **功能**: 基础图片生成
- **重要性**: ⭐⭐⭐

### 4. 文档爬虫
- **文件**: `scripts/grsai-doc-crawler.py`
- **功能**: 爬取 GRS AI 文档
- **重要性**: ⭐⭐⭐

### 5. HTML 提取工具
- **文件**: `scripts/extract_grs_docs.py`
- **功能**: HTML 转 Markdown
- **重要性**: ⭐⭐

---

## 🔑 关键配置信息

### 飞书应用配置
```json
{
  "appId": "cli_a92e8b3399b85cd6",
  "appSecret": "tMiX2hL0wTf7ujPSK2pqnf3d3aeg8AGa"
}
```

### GRS AI API
```
API Host: https://grsai.dakka.com.cn
API Key: sk-10eee66de80245e78277514e88a67401
模型：nano-banana-2
```

### 飞书表格
```
表格 Token: GHrubiTjnayG4fsWP2IcJIotnfc
表格 ID: tbl8ik4qLltAlXvp
URL: https://szdreamgame.feishu.cn/base/GHrubiTjnayG4fsWP2IcJIotnfc
```

### 专属群 ID
| 群名 | 群 ID | BOT 名字 |
|------|------|----------|
| 漫剧 - 文案评审群 | `oc_95a9882e1aca9546c1930b2d27660a6a` | 译文 |
| AI 图片生成工作室 | `oc_f22ffe36d557729c0d77f8b11c74e0bd` | 画语 |

---

## 🤖 BOT 架构

### BOT 1: 译文
- **职责**: 文案评审流程管理
- **专属群**: 漫剧 - 文案评审群
- **集成方式**: OpenClaw 飞书插件
- **状态**: ✅ 运行中

### BOT 2: 画语
- **职责**: 角色/场景设定图生成
- **专属群**: AI 图片生成工作室
- **集成方式**: 独立 Python 脚本
- **状态**: ✅ 运行中

---

## 🔄 工作流程

### 文案评审流程
```
1. 群内发视频 + @译文
   ↓
2. 调用 Coze 工作流识别
   ↓
3. 写入飞书表格
   ↓
4. @需求人评审
   ↓
5. 评审完成 → 归档
```

### 图片生成流程
```
1. 表格状态 → "待生成图片"
   ↓
2. 群内发送指令
   ↓
3. 画语读取表格 + 应用模板
   ↓
4. 调用 Nano Banana API
   ↓
5. 下载并群内通知
```

---

## 📝 升级注意事项

### 必须保留的配置
1. ✅ `openclaw.json` - 飞书 BOT 配置
2. ✅ `IDENTITY.md` - 身份配置
3. ✅ `memory/` - 所有知识库文件
4. ✅ `scripts/nano-banana-agent.py` - 画语 BOT
5. ✅ `scripts/nano-banana-generator-full.py` - 生成脚本

### 可以重新生成的
1. ⚪ `memory/grsai-docs/` - 可重新爬取
2. ⚪ `scripts/grsai-doc-crawler.py` - 可重新创建

### 需要重新配置的
1. ⚠️ 飞书 BOT webhook URL
2. ⚠️ 运行中的进程（需要重启）

---

## 🚀 升级步骤建议

### 1. 备份现有配置
```bash
# 备份主配置
cp /root/.openclaw/openclaw.json /root/.openclaw/openclaw.json.backup

# 备份工作区
tar -czf /tmp/workspace-backup.tar.gz /root/.openclaw/workspace/
```

### 2. 升级 OpenClaw
```bash
pnpm update -g openclaw@latest
# 或
pnpm add -g openclaw@3.13
```

### 3. 恢复配置
```bash
# 恢复主配置
cp /root/.openclaw/openclaw.json.backup /root/.openclaw/openclaw.json

# 恢复工作区（如果需要）
tar -xzf /tmp/workspace-backup.tar.gz -C /root/.openclaw/
```

### 4. 重启服务
```bash
# 重启画语 BOT
pkill -f nano-banana-agent
nohup python3 scripts/nano-banana-agent.py > /tmp/huayu-bot.log 2>&1 &
```

---

## 📊 文件清单总结

| 类别 | 文件数 | 总大小 |
|------|--------|--------|
| 知识库 (.md) | ~10 个 | ~50KB |
| 脚本 (.py) | 5 个 | ~60KB |
| 配置文件 | 1 个 | ~5KB |
| **总计** | **~16 个** | **~115KB** |

---

## 🔗 相关文档链接

- [画语 AGENT 配置](./memory/agents/image-generation-agent.md)
- [提示词模板](./memory/prompts/image-generation.md)
- [部署指南](./memory/nano-banana-deployment.md)
- [飞书配置](./memory/feishu-app-config.md)

---

*备份完成时间：2026-03-16 17:32*  
*用于 trae CN 升级实现*
