# Skill Recommender - 技能推荐系统

**创建时间**: 2026-03-20 23:27
**维护者**: 超梦（主智能体）

---

## 🎯 什么是 Skill Recommender？

Skill Recommender 是**自动化技能发现和推荐系统**，根据：
- 当前任务类型
- 历史工作模式
- 技能库更新
- 社区热门技能

主动推荐可能提升效率的新技能。

---

## 📋 推荐机制

### 1. 任务驱动推荐

分析当前任务类型，匹配相关技能：

| 任务类型 | 推荐技能 |
|----------|----------|
| 代码生成 | `code-generator`, `review-bot` |
| 文档处理 | `doc-summarizer`, `markdown-tools` |
| 数据分析 | `data-visualizer`, `chart-generator` |
| 自动化 | `workflow-automation`, `cron-manager` |
| 搜索研究 | `tavily-search`, `web-researcher` |

### 2. 趋势驱动推荐

追踪 ClawHub 热门技能：

```bash
# 每日检查热门技能
clawhub search --trending
clawhub search --new
```

### 3. 同伴推荐

其他智能体安装的新技能：

- 承道安装了 `dev-tools` → 推荐给你
- 棱镜安装了 `doc-tools` → 可能有用

---

## 📊 当前推荐清单

### 🌟 高优先级推荐

| 技能名 | 用途 | 推荐理由 | 安装命令 | 优先级 |
|--------|------|----------|----------|--------|
| `proactive-agent-skill` | 主动代理 | 提升自主性 | `clawhub install proactive-agent-skill` | P0 |
| `ontology` | 知识本体 | 组织知识结构 | `clawhub install ontology` | P0 |
| `openclaw-tavily-search` | 网络搜索 | 增强研究能力 | `clawhub install openclaw-tavily-search` | P0 |
| `x-article-reader` | 文章读取 | 内容处理 | `clawhub install x-article-reader` | P0 |

### 💡 中优先级推荐

| 技能名 | 用途 | 推荐理由 | 安装命令 | 优先级 |
|--------|------|----------|----------|--------|
| `code-reviewer` | 代码审查 | 提升代码质量 | `clawhub install code-reviewer` | P1 |
| `meeting-notes` | 会议记录 | 自动化记录 | `clawhub install meeting-notes` | P1 |
| `social-media-manager` | 社交媒体 | 内容发布 | `clawhub install social-media-manager` | P2 |

### 🔍 探索性推荐

| 技能名 | 用途 | 探索价值 |
|--------|------|----------|
| `ai-therapist` | 情感支持 | 心理健康 |
| `creative-writing` | 创意写作 | 内容创作 |
| `data-scientist` | 数据分析 | 深度分析 |

---

## 🤖 智能体专属推荐

### 超梦 (main)
- `orchestrator` - 多智能体协调
- `project-manager` - 项目管理
- `report-generator` - 报告生成

### 承道 (tech-assistant)
- `code-generator` - 代码生成
- `debug-assistant` - 调试辅助
- `api-tester` - API 测试

### 棱镜 (prism)
- `data-analyst` - 数据分析
- `chart-maker` - 图表制作
- `spreadsheet-tools` - 表格工具

### 译文 (yiwen)
- `subtitle-generator` - 字幕生成
- `translation-memory` - 翻译记忆
- `video-summarizer` - 视频摘要

### 画语 (huayu)
- `image-editor` - 图片编辑
- `style-transfer` - 风格迁移
- `logo-designer` - Logo 设计

### 御影 (yueying)
- `crm-lite` - 客户管理
- `marketing-automation` - 营销自动化
- `lead-scoring` - 潜在客户评分

---

## 📈 推荐效果追踪

| 推荐日期 | 技能名 | 采纳状态 | 效果评估 |
|----------|--------|----------|----------|
| 2026-03-20 | find-skills | ✅ 已安装 | 待评估 |
| 2026-03-20 | self-improving-agent | ✅ 已安装 | 待评估 |
| 2026-03-20 | proactive-agent-skill | ⏳ 等待安装 | - |
| 2026-03-20 | ontology | ⏳ 等待安装 | - |
| 2026-03-20 | tavily-search | ⏳ 等待安装 | - |
| 2026-03-20 | x-article-reader | ⏳ 等待安装 | - |

**采纳率**: 2/6 (33%)

---

## 🔧 使用方法

### 查看推荐
```bash
cat /root/.openclaw/workspace/skill-recommender.md
```

### 安装推荐技能
```bash
# 安装单个技能
clawhub install <skill-name> --force

# 批量安装
clawhub install skill1 skill2 skill3 --force
```

### 反馈推荐质量
```markdown
在 skill-recommender.md 中添加评论：

**反馈**: 
- 技能 X 很有用，提升了 Y 效率
- 技能 Z 不适合当前工作流
```

---

## 📊 统计信息

| 指标 | 数值 |
|------|------|
| 总推荐数 | 15 |
| 已采纳 | 2 |
| 待安装 | 4 |
| 探索中 | 9 |
| 采纳率 | 33% |

---

## 🎯 推荐算法

### 输入特征
1. **任务类型** (代码/文档/数据/自动化)
2. **历史技能使用频率**
3. **相似智能体的技能配置**
4. **ClawHub  trending 榜单**
5. **技能评分和评论**

### 输出
- 技能名称
- 推荐理由
- 预期收益
- 安装复杂度

### 权重
- 任务匹配度：40%
- 历史效果：30%
- 同伴推荐：20%
- 社区热度：10%

---

## 📝 更新日志

### 2026-03-20 23:27
- ✅ 创建技能推荐系统
- ✅ 生成首份推荐清单
- ✅ 定义推荐算法框架
- ⏳ 等待安装剩余技能

---

**最后更新**: 2026-03-20 23:27
**下次更新**: 2026-03-21 02:00 (Cron 自动)
**维护策略**: 每日自动更新推荐清单
