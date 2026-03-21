# 跨实例 Agent 协同方案

**创建时间**: 2026-03-21 20:02  
**版本**: 1.0  
**状态**: 待实施

---

## 🎯 目标

实现云服务器（超梦）与 Mac Mini（御影）之间的有效协同，支持：
1. 独立飞书 Bot 配置
2. 消息路由不冲突
3. 任务委派和协作
4. 资源共享（NAS）

---

## 📋 方案对比

### 方案 A: 完全独立（推荐）

**架构**：
```
飞书消息 → 超梦 Bot → 云服务器 Gateway → 超梦/承道/棱镜/译文/画语
飞书消息 → 御影 Bot → Mac Mini Gateway → 御影
```

**配置**：
- 超梦 Bot (`cli_a92e8b3399b85cd6`) → 云服务器
- 御影 Bot (`cli_a931156747bbdcc6`) → Mac Mini
- 两个 Bot 在飞书开放平台分别配置事件订阅
- 路由不重叠

**优点**：
- ✅ 配置清晰，不混淆
- ✅ 故障隔离
- ✅ 易于扩展（御影 2 号、3 号）

**缺点**：
- ❌ 需要两个飞书应用
- ❌ 跨实例通信需要额外机制

---

### 方案 B: 主从模式

**架构**：
```
飞书消息 → 超梦 Bot → 云服务器 Gateway → 路由分发
                                    ├─ 本地处理（超梦/承道/棱镜/译文/画语）
                                    └─ 转发 → Mac Mini Gateway → 御影处理
```

**配置**：
- 只有一个飞书 Bot（超梦）
- 云服务器配置御影的路由绑定
- 御影在 Mac Mini 上作为"子智能体"运行

**优点**：
- ✅ 只需一个飞书应用
- ✅ 统一管理

**缺点**：
- ❌ 云服务器故障影响所有智能体
- ❌ 配置复杂，容易出错（今天的问题）
- ❌ Mac Mini 依赖云服务器

---

### 方案 C: 混合模式

**架构**：
```
飞书消息 → 超梦 Bot → 云服务器 Gateway → 超梦/承道/棱镜/译文/画语
                                           ↓
                                    任务委派（飞书/飞书表格）
                                           ↓
飞书消息 → 御影 Bot → Mac Mini Gateway → 御影处理
```

**配置**：
- 两个独立的飞书 Bot
- 通过飞书群或飞书表格进行任务委派
- NAS 共享文件

**优点**：
- ✅ 配置独立
- ✅ 通过飞书自然协作
- ✅ 易于理解和维护

**缺点**：
- ❌ 需要两个飞书应用
- ❌ 任务委派通过飞书（有延迟）

---

## ✅ 推荐方案：方案 A（完全独立）+ 飞书协作

### 实施步骤

#### 1. 飞书配置

**超梦 Bot** (`cli_a92e8b3399b85cd6`):
- 事件订阅：`im.message.receive_v1`
- Webhook：云服务器 WebSocket（长连接）
- 权限：消息发送与接收、群组管理

**御影 Bot** (`cli_a931156747bbdcc6`):
- 事件订阅：`im.message.receive_v1`
- Webhook：Mac Mini WebSocket（长连接）
- 权限：消息发送与接收、群组管理

#### 2. 云服务器配置

**文件**: `~/.openclaw/openclaw.json`

```json5
{
  channels: {
    feishu: {
      defaultAccount: "feishubot",
      accounts: {
        feishubot: {
          appId: "cli_a92e8b3399b85cd6",  // 超梦 Bot
          appSecret: "xxx",
          enabled: true
        }
      }
    }
  },
  bindings: [
    { agentId: "main", match: { channel: "feishu" } },  // 私聊
    { agentId: "tech-assistant", match: { channel: "feishu", peer: { kind: "group", id: "oc_05c2227c357b46a430d984a481664a7d" } } },
    { agentId: "prism", match: { channel: "feishu", peer: { kind: "group", id: "oc_ac0b758330a732a46d8a6ca9f3985260" } } },
    { agentId: "yiwen", match: { channel: "feishu", peer: { kind: "group", id: "oc_95a9882e1aca9546c1930b2d27660a6a" } } },
    { agentId: "huayu", match: { channel: "feishu", peer: { kind: "group", id: "oc_f22ffe36d557729c0d77f8b11c74e0bd" } } }
    // 注意：不包含 yueying
  ]
}
```

#### 3. Mac Mini 配置

**文件**: `~/.openclaw/openclaw.json`

```json5
{
  channels: {
    feishu: {
      defaultAccount: "feishubot",
      accounts: {
        feishubot: {
          appId: "cli_a931156747bbdcc6",  // 御影 Bot
          appSecret: "xxx",
          enabled: true
        }
      }
    }
  },
  bindings: [
    { agentId: "yueying", match: { channel: "feishu" } }  // 御影专属群
  ]
}
```

#### 4. 任务委派流程

**通过飞书群**：
```
1. 超梦在"漫剧制作群" @御影
   "@御影 新项目 MJ-001，脚本和分镜已上传 NAS"

2. 御影响应
   "收到，开始处理 MJ-001"

3. 御影完成后在群里汇报
   "MJ-001 已完成，视频已上传 NAS/exports/"
```

**通过飞书表格**：
```
1. 超梦更新"漫剧制作进度表"
   - 项目编号：MJ-001
   - 状态：待制作
   - 负责人：御影

2. 御影轮询表格（或订阅更新）
   - 发现新任务
   - 更新状态：制作中

3. 完成后更新表格
   - 状态：已完成
   - 视频链接：[NAS 链接]
```

---

## 🚨 配置修改检查清单

### 修改前

- [ ] 备份配置：`cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.$(date +%Y%m%d_%H%M%S).bak`
- [ ] 确认修改的是哪个 Bot（超梦 or 御影）
- [ ] 确认修改的是哪个设备（云服务器 or Mac Mini）
- [ ] 更新 INFRASTRUCTURE.md

### 修改后

- [ ] 验证 JSON 语法：`openclaw doctor`
- [ ] 重启 Gateway：`openclaw gateway restart`
- [ ] 检查渠道状态：`openclaw channels status`
- [ ] 检查路由配置：`openclaw agents list --bindings`
- [ ] 测试消息收发

---

## 📊 方案对比总结

| 方案 | 复杂度 | 可靠性 | 扩展性 | 推荐度 |
|------|--------|--------|--------|--------|
| A: 完全独立 | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ 推荐 |
| B: 主从模式 | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ❌ 不推荐 |
| C: 混合模式 | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ 备选 |

---

## 🎯 立即执行（如需重置 Mac Mini）

```bash
# 1. Mac Mini 备份配置
ssh panzelin@100.102.241.1 'cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak'

# 2. 重置 Mac Mini 配置
ssh panzelin@100.102.241.1 'openclaw channels remove feishu'
ssh panzelin@100.102.241.1 'openclaw channels add'  # 重新配置御影 Bot

# 3. 验证配置
ssh panzelin@100.102.241.1 'openclaw channels status'
ssh panzelin@100.102.241.1 'openclaw agents list --bindings'

# 4. 测试消息
# 在御影专属群发送测试消息
```

---

**最后更新**: 2026-03-21 20:02  
**下次审查**: 配置变更时
