# OpenClaw 官方文档索引

**创建时间**: 2026-03-21 20:02  
**来源**: https://docs.openclaw.ai  
**用途**: 快速查阅 OpenClaw 核心概念和配置

---

## 📚 核心文档

### 架构说明

**关键概念**：
1. **Gateway** - 单一控制平面，管理会话、渠道、工具和事件
2. **Pi Agent** - RPC 模式的智能体运行时
3. **Session 模型** - `main` 用于私聊，群组隔离
4. **多智能体路由** - 根据渠道/账号/对等方路由到隔离的智能体

### 飞书渠道

**关键配置**：
- **连接模式**: WebSocket 长连接（不需要公网 URL）
- **事件订阅**: `im.message.receive_v1`
- **配对策略**: `dmPolicy: "pairing"`（默认）
- **群组策略**: `groupPolicy: "open"`（默认需要@提及）

**配置位置**: `~/.openclaw/openclaw.json`

```json5
{
  channels: {
    feishu: {
      defaultAccount: "feishubot",
      accounts: {
        feishubot: {
          appId: "cli_xxx",
          appSecret: "xxx",
          enabled: true,
          domain: "feishu"
        }
      }
    }
  },
  bindings: [
    {
      agentId: "yueying",
      match: {
        channel: "feishu",
        peer: { kind: "group", id: "oc_xxx" }
      }
    }
  ]
}
```

### 多智能体路由

**原理**：
- 通过 `bindings` 数组配置路由规则
- 根据 `channel` + `peer.kind` + `peer.id` 匹配
- 每个绑定指向一个 `agentId`

**示例**：
```json5
bindings: [
  {
    // 用户 A 私聊 → main agent
    agentId: "main",
    match: { channel: "feishu", peer: { kind: "dm", id: "ou_xxx" } }
  },
  {
    // 群组 → yueying agent
    agentId: "yueying",
    match: { channel: "feishu", peer: { kind: "group", id: "oc_xxx" } }
  }
]
```

---

## 🔧 常用命令

```bash
# 网关管理
openclaw gateway status
openclaw gateway restart
openclaw logs --follow

# 渠道管理
openclaw channels status
openclaw channels add

# 智能体管理
openclaw agents list --bindings
openclaw agent --message "test"

# 配对管理
openclaw pairing list feishu
openclaw pairing approve feishu <CODE>

# 诊断
openclaw doctor
```

---

## 📖 文档链接

| 主题 | URL |
|------|-----|
| 入门指南 | https://docs.openclaw.ai/start/getting-started |
| 网关配置 | https://docs.openclaw.ai/gateway/configuration |
| 飞书渠道 | https://docs.openclaw.ai/channels/feishu |
| 多智能体路由 | https://docs.openclaw.ai/gateway/configuration#multi-agent-routing |
| 安全配置 | https://docs.openclaw.ai/gateway/security |
| 故障排除 | https://docs.openclaw.ai/channels/troubleshooting |

---

**最后更新**: 2026-03-21 20:02
