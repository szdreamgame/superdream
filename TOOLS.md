# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## 本地配置笔记

### 智能体配置

| 智能体 | 模型 | 专属群 |
|--------|------|--------|
| 超梦 (main) | dashscope-coding/qwen3.5-plus | 默认 |
| 承道 (tech-assistant) | dashscope-coding/MiniMax-M2.5 | oc_05c2227c357b46a430d984a481664a7d |
| 棱镜 (prism) | dashscope-coding/MiniMax-M2.5 | oc_ac0b758330a732a46d8a6ca9f3985260 |
| 译文 (yiwen) | dashscope-coding/qwen3.5-plus | oc_95a9882e1aca9546c1930b2d27660a6a |
| 画语 (huayu) | dashscope-coding/MiniMax-M2.5 | oc_f22ffe36d557729c0d77f8b11c74e0bd |
| 御影 (yueying) | dashscope-coding/qwen3.5-plus | 暂无 |

### foxcode 配置（Anthropic 接口）

```json
"foxcode": {
  "baseUrl": "https://code.newcli.com/claude/droid",
  "apiKey": "sk-ant-...",
  "api": "anthropic-messages",  // ⚠️ 必须是 anthropic-messages，不是 openai-completions
  "headers": {
    "User-Agent": "claude-cli/2.0.76 (external, cli)"
  }
}
```

**教训**：foxcode 是 Anthropic 原生接口，必须用 `"api": "anthropic-messages"`，否则会返回空响应。

### Gateway 进程检查

```bash
# 正常状态：应该只有 1 个进程
ps aux | grep openclaw-gateway | grep -v grep

# 清理异常进程
kill -9 <异常进程 PID>
```
