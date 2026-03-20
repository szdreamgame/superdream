# Triggers - 触发器配置

**创建时间**: 2026-03-20 22:45
**维护者**: 超梦（主智能体）

---

## 🎯 什么是 Triggers？

Triggers 是 Agent 的**自主触发机制**，让 Agent 从被动等待变为主动感知。

每个 Trigger 必须关联一个 Focus Item（关注点），当 Focus 完成时自动取消 Trigger。

---

## 📋 当前激活的触发器

### 1. 周末升级计划 - 每日进度检查

**关联 Focus**: 周末升级计划 - Clawith 功能引进

**配置**:
```yaml
type: cron
schedule: "0 2 * * *"  # 每天凌晨 2:00
action: "检查升级进度并发布日报"
enabled: true
```

**触发时行为**:
1. 检查 focus.md 中的任务状态
2. 更新进度统计
3. 在 plaza.md 发布日报
4. 如果有阻塞问题，通知潘总

---

### 2. 周末升级计划 - 最终检查

**关联 Focus**: 周末升级计划 - Clawith 功能引进

**配置**:
```yaml
type: once
time: "2026-03-22 23:59"
action: "最终检查并提交总结报告"
enabled: true
```

**触发时行为**:
1. 检查所有 P0/P1/P2 任务完成状态
2. 生成总结报告
3. 更新 troubleshooting-guide.md
4. 归档到 memory/ 目录

---

### 3. 技能安装 - Rate Limit 重试

**关联 Focus**: 智能体技能批量安装

**配置**:
```yaml
type: interval
interval: 300  # 每 5 分钟
action: "重试安装剩余技能"
max_retries: 10
enabled: true
```

**触发时行为**:
1. 检查 clawhub list
2. 识别未安装的技能
3. 尝试批量安装
4. 如果成功，取消此触发器

---

### 4. Gateway 健康检查

**关联 Focus**: 系统稳定性维护

**配置**:
```yaml
type: cron
schedule: "0 */4 * * *"  # 每 4 小时
action: "检查 Gateway 进程和系统状态"
enabled: true
```

**触发时行为**:
1. 检查 Gateway 进程数量（应该=1）
2. 检查 CPU/内存使用
3. 检查磁盘空间
4. 异常时立即通知

---

## 🔧 触发器类型说明

| 类型 | 说明 | 示例 |
|------|------|------|
| `cron` | 定时循环 | `0 2 * * *`（每天凌晨 2 点） |
| `once` | 单次定时 | `2026-03-22 23:59` |
| `interval` | 固定间隔 | `300`（每 5 分钟） |
| `poll` | HTTP 端点监控 | `https://api.example.com/health` |
| `on_message` | 等待特定消息 | `用户：开始升级` |
| `webhook` | 接收外部回调 | `POST /webhook/github` |

---

## 📊 触发器统计

| 状态 | 数量 |
|------|------|
| 激活中 | 4 |
| 已暂停 | 0 |
| 已完成 | 0 |
| 已取消 | 0 |

---

## 🎛️ 管理命令

```bash
# 查看触发器状态
cat /root/.openclaw/workspace/triggers.md

# 暂停触发器
# 编辑 triggers.md，设置 enabled: false

# 恢复触发器
# 编辑 triggers.md，设置 enabled: true

# 手动触发（测试用）
# 运行触发器关联的 action
```

---

## 🔗 Focus-Trigger 绑定规则

**重要**: 每个 Trigger 必须关联一个 Focus Item

**示例**:
```yaml
Focus: "周末升级计划"
  Triggers:
    - cron: "0 2 * * *"
    - once: "2026-03-22 23:59"

Focus: "智能体技能批量安装"
  Triggers:
    - interval: 300
```

当 Focus 状态变为 `[x]` 已完成时，自动取消所有关联的 Trigger。

---

**最后更新**: 2026-03-20 22:45
**下次检查**: 2026-03-21 02:00 (每日进度检查)
