# OpenClaw 故障排查指南

**创建时间**: 2026-03-20  
**最后更新**: 2026-03-20  
**维护人**: 超梦 / 承道

---

## 问题索引

| 编号 | 问题类型 | 症状 | 解决方案 |
|------|----------|------|----------|
| [P001](#p001-多 gateway 进程) | Gateway 异常 | CPU 占用高，回复慢 | 清理多余进程 |
| [P002](#p002-承道路由错误) | 路由配置 | @承道 却路由到超梦 | 使用 bindings 路由 |
| [P003](#p003-foxcode 模型空响应) | 模型配置 | API 返回空响应 | 修改 api 字段 |
| [P004](#p004-agent 配置覆盖) | 配置隔离 | Gateway 重启后配置丢失 | 独立 agentDir |

---

## P001: 多 Gateway 进程

### 症状
- CPU 占用异常上升（>100%）
- 回复速度大幅下降
- `ps aux | grep openclaw-gateway` 显示多个进程

### 原因
- 配置变更时触发 Gateway 重新加载
- 旧进程未正确退出
- 某些 agent 调用会触发新进程创建

### 诊断命令
```bash
# 检查 Gateway 进程数量（正常应该是 1 个）
ps aux | grep openclaw-gateway | grep -v grep | wc -l

# 查看详细信息
ps aux | grep openclaw-gateway | grep -v grep
```

### 解决方案
```bash
# 1. 保留主进程（运行时间最长的那个），清理其他
kill -9 <异常进程 PID>

# 2. 验证只剩 1 个进程
ps aux | grep openclaw-gateway | grep -v grep
```

### 预防措施
- 确保每个 agent 有独立的 `agentDir` 和 `workspace`
- 使用 `openclaw gateway restart` 而不是手动杀进程
- 定期检查 Gateway 进程数量

### 相关配置
```json5
{
  agents: {
    list: [
      {
        id: "main",
        agentDir: "~/.openclaw/agents/main/agent",
        workspace: "~/.openclaw/workspace"
      },
      {
        id: "tech-assistant",
        agentDir: "~/.openclaw/agents/tech-assistant/agent",
        workspace: "~/.openclaw/workspace-tech-assistant"
      }
    ]
  }
}
```

---

## P002: 承道路由错误

### 症状
- 在承道专属群里 @承道，回复却来自超梦
- 飞书消息路由混乱

### 原因
- 使用了旧的 `channels.feishu.agents` 配置方式
- 没有使用 `bindings` 进行精确路由

### 诊断命令
```bash
# 检查当前路由配置
openclaw agents list --bindings
```

### 解决方案

**错误的配置**（不要使用）：
```json5
{
  channels: {
    feishu: {
      agents: {
        "oc_xxx": "tech-assistant"  // ❌ 这种方式不精确
      }
    }
  }
}
```

**正确的配置**：
```json5
{
  bindings: [
    {
      agentId: "tech-assistant",
      match: {
        channel: "feishu",
        peer: {
          kind: "group",
          id: "oc_05c2227c357b46a430d984a481664a7d"
        }
      }
    },
    {
      agentId: "main",
      match: { channel: "feishu" }  // 默认路由
    }
  ]
}
```

### 路由优先级
1. `peer` match（最精确）
2. `parentPeer` match
3. `guildId + roles`
4. `guildId`
5. `teamId`
6. `accountId`
7. channel-level match
8. 默认路由

### 验证
```bash
# 确认路由正确应用
openclaw agents list --bindings

# 输出示例：
# - tech-assistant (承道)
#   Routing rules: 1
#   Routing rules:
#     - feishu peer=group:oc_05c2227c357b46a430d984a481664a7d
```

---

## P003: foxcode 模型空响应

### 症状
- 调用 `foxcode/claude-*` 或 `foxcode-ultra/claude-*` 模型
- 返回空响应（`content: []`）
- usage 统计都是 0
- 无错误信息

### 原因
**API 接口类型不匹配**：
- foxcode 使用 **Anthropic 原生接口**
- 但配置中设置了 `"api": "openai-completions"`（OpenAI 兼容接口）
- 请求格式不匹配导致 API 返回空响应

### 诊断命令
```bash
# 检查配置中的 api 字段
grep -A 5 '"foxcode"' /root/.openclaw/openclaw.json

# 测试 API（应该返回正常响应）
curl -s -X POST https://code.newcli.com/claude/ultra/v1/chat/completions \
  -H "Authorization: Bearer sk-ant-..." \
  -H "Content-Type: application/json" \
  -H "User-Agent: claude-cli/2.0.76 (external, cli)" \
  -d '{"model":"claude-opus-4-6","messages":[{"role":"user","content":"测试"}],"max_tokens":10}'
```

### 解决方案

**错误的配置**：
```json5
{
  models: {
    providers: {
      foxcode: {
        baseUrl: "https://code.newcli.com/claude/droid",
        apiKey: "sk-ant-...",
        api: "openai-completions",  // ❌ 错误！
        // ...
      }
    }
  }
}
```

**正确的配置**：
```json5
{
  models: {
    providers: {
      foxcode: {
        baseUrl: "https://code.newcli.com/claude/droid",
        apiKey: "sk-ant-...",
        api: "anthropic-messages",  // ✅ 正确！
        headers: {
          "User-Agent": "claude-cli/2.0.76 (external, cli)"
        },
        models: [
          {
            id: "claude-opus-4-6",
            name: "claude-opus-4-6"
          }
        ]
      }
    }
  }
}
```

### 需要修改的文件
1. `/root/.openclaw/openclaw.json` - 主配置
2. `/root/.openclaw/agents/main/agent/models.json` - main agent
3. `/root/.openclaw/agents/tech-assistant/agent/models.json` - 承道 agent
4. 其他 agent 的 `models.json`

### 验证
```bash
# 测试承道模型调用
openclaw agent --agent tech-assistant --message "测试：请回复'承道已就绪'"

# 检查会话日志
cat /root/.openclaw/agents/tech-assistant/sessions/*.jsonl | tail -20
```

### 经验教训
**Anthropic 原生接口 vs OpenAI 兼容接口**：

| 提供商 | 接口类型 | api 字段值 |
|--------|----------|-----------|
| OpenAI | OpenAI 兼容 | `openai-completions` |
| DashScope | OpenAI 兼容 | `openai-completions` |
| **foxcode** | **Anthropic 原生** | **`anthropic-messages`** |
| Anthropic | Anthropic 原生 | `anthropic-messages` |
| Google | Google 原生 | `google-generative-ai` |

---

## P004: Agent 配置覆盖

### 症状
- Gateway 重启后，某些 agent 的配置丢失
- 多个 agent 共享同一个 `models.json`
- 配置被"同步"成一样的

### 原因
- 多个 agent 共享同一个 `agentDir`
- Gateway 重启时，活跃 agent 会从 main 复制配置
- 没有为每个 agent 配置独立的 `agentDir`

### 诊断命令
```bash
# 检查各 agent 的配置目录
ls -la /root/.openclaw/agents/*/agent/

# 检查配置是否独立
diff /root/.openclaw/agents/main/agent/models.json \
     /root/.openclaw/agents/tech-assistant/agent/models.json
```

### 解决方案

**在 `openclaw.json` 中为每个 agent 配置独立的 `agentDir` 和 `workspace`**：

```json5
{
  agents: {
    list: [
      {
        id: "main",
        name: "超梦",
        model: "dashscope-coding/qwen3.5-plus",
        agentDir: "~/.openclaw/agents/main/agent",
        workspace: "~/.openclaw/workspace"
      },
      {
        id: "tech-assistant",
        name: "承道",
        model: "dashscope-coding/MiniMax-M2.5",
        agentDir: "~/.openclaw/agents/tech-assistant/agent",
        workspace: "~/.openclaw/workspace-tech-assistant"
      },
      {
        id: "prism",
        name: "棱镜",
        model: "dashscope-coding/MiniMax-M2.5",
        agentDir: "~/.openclaw/agents/prism/agent",
        workspace: "~/.openclaw/workspace-prism"
      }
    ]
  }
}
```

### 为每个 agent 创建独立配置
```bash
# 为每个 agent 复制 models.json
cp /root/.openclaw/agents/main/agent/models.json \
   /root/.openclaw/agents/prism/agent/models.json

cp /root/.openclaw/agents/main/agent/models.json \
   /root/.openclaw/agents/yiwen/agent/models.json

# ... 对其他 agent 执行相同操作
```

### 验证
```bash
# 确认每个 agent 有独立的配置
openclaw agents list --bindings

# 输出应该显示每个 agent 的独立 workspace 和 agentDir
```

---

## 快速检查脚本

```bash
#!/bin/bash
# OpenClaw 健康检查脚本

echo "=== Gateway 进程检查 ==="
GW_COUNT=$(ps aux | grep openclaw-gateway | grep -v grep | wc -l)
echo "Gateway 进程数：$GW_COUNT (正常：1)"
if [ $GW_COUNT -ne 1 ]; then
  echo "⚠️  警告：Gateway 进程数量异常！"
  ps aux | grep openclaw-gateway | grep -v grep
fi

echo ""
echo "=== Agent 路由检查 ==="
openclaw agents list --bindings 2>&1 | grep -E "^[a-z]"

echo ""
echo "=== 配置完整性检查 ==="
for agent in main tech-assistant prism yiwen huayu yueying; do
  if [ -f "/root/.openclaw/agents/$agent/agent/models.json" ]; then
    echo "✅ $agent: models.json 存在"
  else
    echo "❌ $agent: models.json 缺失"
  fi
done
```

---

## 相关文档

- [Multi-Agent Routing](/root/.local/share/pnpm/global/5/.pnpm/openclaw@2026.3.13_@discordjs+opus@0.10.0_@napi-rs+canvas@0.1.97_@types+express@5.0.6_node-llama-cpp@3.16.2/node_modules/openclaw/docs/concepts/multi-agent.md)
- [Configuration Reference](/root/.local/share/pnpm/global/5/.pnpm/openclaw@2026.3.13_@discordjs+opus@0.10.0_@napi-rs+canvas@0.1.97_@types+express@5.0.6_node-llama-cpp@3.16.2/node_modules/openclaw/docs/gateway/configuration-reference.md)
- [Model Providers](/root/.local/share/pnpm/global/5/.pnpm/openclaw@2026.3.13_@discordjs+opus@0.10.0_@napi-rs+canvas@0.1.97_@types+express@5.0.6_node-llama-cpp@3.16.2/node_modules/openclaw/docs/concepts/model-providers.md)

---

## 更新日志

| 日期 | 更新内容 | 更新人 |
|------|----------|--------|
| 2026-03-20 | 初始版本，添加 P001-P004 | 超梦 |
