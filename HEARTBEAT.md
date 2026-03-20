# HEARTBEAT.md

# 定期检查任务（每 4-6 小时执行一次）

## Gateway 健康检查
- [ ] Gateway 进程数量 = 1（`ps aux | grep openclaw-gateway`）
- [ ] 无异常进程占用 CPU

## 智能体配置检查

**注意**：模型配置以 `~/.openclaw/openclaw.json` 和 `~/.openclaw/agents/*/agent/config.json` 为准。
修改模型后，**同步更新本文档**，避免心跳检查误报。

### 当前配置（最后更新：2026-03-21）

| 智能体 | 模型 | 专属群 |
|--------|------|--------|
| 承道 | dashscope-coding/MiniMax-M2.5 | oc_05c2227c357b46a430d984a481664a7d |
| 棱镜 | dashscope-coding/MiniMax-M2.5 | oc_ac0b758330a732a46d8a6ca9f3985260 |
| 译文 | dashscope-coding/qwen3.5-plus | oc_95a9882e1aca9546c1930b2d27660a6a |
| 画语 | dashscope-coding/MiniMax-M2.5 | oc_f22ffe36d557729c0d77f8b11c74e0bd |
| 御影 | dashscope-coding/qwen3.5-plus | 暂无 |

### 心跳检查项
- [ ] 承道模型与配置一致
- [ ] 棱镜路由正确
- [ ] 译文路由正确
- [ ] 画语路由正确

## 发现异常时
1. 立即清理异常进程
2. 记录到 memory/YYYY-MM-DD.md
3. 向潘总汇报

---

## 修改模型后的操作清单

当修改智能体模型时：

1. **修改配置**：
   - `~/.openclaw/openclaw.json` → `agents.list[].model`
   - `~/.openclaw/agents/<name>/agent/config.json` → `model`

2. **重启 Gateway**：
   ```bash
   openclaw gateway restart
   ```

3. **更新本文档**：
   - 修改 "当前配置" 表格中的模型信息
   - 更新 "最后更新" 日期

4. **验证**：
   ```bash
   openclaw agents list --bindings | grep -A 3 <agent-id>
   ```
