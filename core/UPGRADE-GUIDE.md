# 超梦 (小梦同学) - traé CN 升级指南

> **备份时间**: 2026-03-16 17:34  
> **当前版本**: OpenClaw 2026.3.8  
> **目标版本**: OpenClaw 3.13+

---

## 📦 备份文件位置

### 完整备份
- **路径**: `/tmp/chaomeng-full-backup.tar.gz`
- **大小**: 7.3MB
- **内容**: 整个工作区（包括所有知识库、脚本、配置）

### 配置备份
- **路径**: `/root/.openclaw/openclaw.json.backup`
- **内容**: 飞书 BOT 配置、API Keys 等

### 索引文档
- **路径**: `/root/.openclaw/workspace/BACKUP-INDEX.md`
- **内容**: 完整的文件清单和配置说明

---

## 🔑 关键配置信息

### 飞书应用
```json
{
  "appId": "cli_a92e8b3399b85cd6",
  "appSecret": "tMiX2hL0wTf7ujPSK2pqnf3d3aeg8AGa"
}
```

### GRS AI API
```
Host: https://grsai.dakka.com.cn
API Key: sk-10eee66de80245e78277514e88a67401
模型：nano-banana-2
```

### 飞书表格
```
Token: GHrubiTjnayG4fsWP2IcJIotnfc
Table ID: tbl8ik4qLltAlXvp
```

### 专属群
```
文案评审群：oc_95a9882e1aca9546c1930b2d27660a6a (BOT: 译文)
图片生成群：oc_f22ffe36d557729c0d77f8b11c74e0bd (BOT: 画语)
```

---

## 🤖 BOT 架构

### BOT 1: 译文
- **职责**: 文案评审流程
- **集成**: OpenClaw 飞书插件
- **状态**: 运行中

### BOT 2: 画语
- **职责**: 图片生成
- **集成**: 独立 Python 脚本
- **脚本**: `scripts/nano-banana-agent.py`
- **状态**: 运行中

---

## 📚 核心知识库

### 必须保留
1. `IDENTITY.md` - 超梦身份配置
2. `memory/prompts/image-generation.md` - 提示词模板（周瑜维护）
3. `memory/agents/image-generation-agent.md` - 画语 AGENT 配置
4. `scripts/nano-banana-agent.py` - 画语 BOT 脚本
5. `scripts/nano-banana-generator-full.py` - 图片生成脚本

---

## 🚀 traé CN 升级步骤

### 1. 恢复备份
```bash
# 如果升级后配置丢失，恢复备份
tar -xzf /tmp/chaomeng-full-backup.tar.gz -C /root/.openclaw/
cp /root/.openclaw/openclaw.json.backup /root/.openclaw/openclaw.json
```

### 2. 验证配置
```bash
# 检查飞书配置
cat /root/.openclaw/openclaw.json | grep -A2 "feishu"

# 检查工作区文件
ls -la /root/.openclaw/workspace/memory/
ls -la /root/.openclaw/workspace/scripts/
```

### 3. 重启 BOT 服务
```bash
# 停止旧进程
pkill -f nano-banana-agent

# 启动画语 BOT
cd /root/.openclaw/workspace
nohup python3 scripts/nano-banana-agent.py > /tmp/huayu-bot.log 2>&1 &

# 验证运行
ps aux | grep nano-banana-agent
tail -f /tmp/huayu-bot.log
```

### 4. 测试功能
- 在文案评审群测试译文 BOT
- 在图片生成群测试画语 BOT
- 验证提示词模板功能

---

## ⚠️ 注意事项

### 升级可能影响的
1. OpenClaw 飞书插件配置
2. 运行中的 BOT 进程
3. Gateway 服务

### 不受影响的
1. 工作区文件（已备份）
2. 独立 Python 脚本
3. 知识库文档

---

## 📞 升级后检查清单

- [ ] 验证 OpenClaw 版本
- [ ] 检查飞书配置
- [ ] 验证工作区文件完整
- [ ] 重启画语 BOT
- [ ] 测试文案评审流程
- [ ] 测试图片生成流程
- [ ] 确认提示词模板正常
- [ ] 验证群 BOT 响应

---

## 🔄 回滚方案

如果升级后有问题：

```bash
# 1. 停止所有服务
pkill -f nano-banana-agent
openclaw gateway stop

# 2. 恢复备份
tar -xzf /tmp/chaomeng-full-backup.tar.gz -C /root/.openclaw/
cp /root/.openclaw/openclaw.json.backup /root/.openclaw/openclaw.json

# 3. 重启服务
openclaw gateway restart
cd /root/.openclaw/workspace
nohup python3 scripts/nano-banana-agent.py > /tmp/huayu-bot.log 2>&1 &
```

---

## 📊 文件统计

| 类别 | 文件数 | 大小 |
|------|--------|------|
| 知识库 | ~10 个 | ~50KB |
| 脚本 | 5 个 | ~60KB |
| 配置 | 1 个 | ~5KB |
| 总备份 | - | 7.3MB |

---

*备份完成时间：2026-03-16 17:34*  
*用于 traé CN 升级实现*
