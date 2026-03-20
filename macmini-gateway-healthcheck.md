# Mac mini 御影 Gateway 健康检查指南

## 问题背景
御影 (Mac mini) 对话间歇性连接中断，需要检查和修复。

---

## 1. 检查 Gateway 状态

```bash
# 检查 Gateway 进程
ps aux | grep openclaw-gateway

# 检查 Gateway 状态
openclaw gateway status

# 查看 Gateway 日志（最近 100 行）
tail -100 ~/.openclaw/logs/openclaw.log
```

**预期输出**：
- Gateway 进程应该运行中
- 日志中不应该有连续的 `ERROR` 或 `failed` 记录

---

## 2. 检查飞书配置

```bash
# 查看飞书配置
cat ~/.openclaw/openclaw.json | python3 -c "import sys,json; c=json.load(sys.stdin); print(json.dumps(c.get('channels',{}).get('feishu',{}), indent=2))"
```

**检查项**：
- `appId` 和 `appSecret` 是否正确
- `enabled: true` 是否设置
- 群聊路由配置是否正确

---

## 3. 测试飞书连接

```bash
# 测试飞书 Token 获取
curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d '{"app_id":"cli_a931156747bbdcc6","app_secret":"lpLaHWcu94jzi0A4acwbKehcZNvIgjyB"}' | python3 -c "import sys,json; r=json.load(sys.stdin); print('Token:', r.get('tenant_access_token','获取失败')); print('Code:', r.get('code','N/A'))"
```

**预期输出**：
- `Token: t-xxx`（有 Token 返回）
- `Code: 0`（成功）

---

## 4. 启用推送失败日志

编辑 Gateway 配置，启用详细日志：

```bash
# 备份配置
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.backup

# 编辑配置，添加日志级别
# 在 openclaw.json 中添加或修改：
# "logging": {
#   "level": "debug",
#   "feishu": {
#     "push_failures": true
#   }
# }
```

**或者设置环境变量**：
```bash
export OPENCLAW_LOG_LEVEL=debug
```

---

## 5. 部署飞书健康检查脚本

### 创建脚本

```bash
cat > ~/.openclaw/workspace/feishu-healthcheck.sh << 'EOF'
#!/bin/bash
# 飞书健康检查脚本

LOG_FILE="/tmp/feishu-healthcheck.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$TIMESTAMP] 开始健康检查..." >> $LOG_FILE

# 1. 检查 Gateway 进程
if ! pgrep -f "openclaw.*gateway" > /dev/null; then
    echo "[$TIMESTAMP] ❌ Gateway 未运行" >> $LOG_FILE
    # 尝试重启 Gateway
    openclaw gateway restart >> $LOG_FILE 2>&1
    exit 1
fi
echo "[$TIMESTAMP] ✅ Gateway 运行正常" >> $LOG_FILE

# 2. 检查飞书 Token
TOKEN_RESPONSE=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d '{"app_id":"cli_a931156747bbdcc6","app_secret":"lpLaHWcu94jzi0A4acwbKehcZNvIgjyB"}')

TOKEN=$(echo $TOKEN_RESPONSE | python3 -c "import sys,json; print(json.load(sys.stdin).get('tenant_access_token',''))" 2>/dev/null)
CODE=$(echo $TOKEN_RESPONSE | python3 -c "import sys,json; print(json.load(sys.stdin).get('code',''))" 2>/dev/null)

if [ -z "$TOKEN" ] || [ "$CODE" != "0" ]; then
    echo "[$TIMESTAMP] ❌ 飞书 Token 获取失败 (code: $CODE)" >> $LOG_FILE
    exit 1
fi
echo "[$TIMESTAMP] ✅ 飞书连接正常" >> $LOG_FILE

# 3. 检查 Tailscale 连接
if ! ping -c 1 100.82.219.91 > /dev/null 2>&1; then
    echo "[$TIMESTAMP] ❌ Tailscale 连接失败（阿里云不可达）" >> $LOG_FILE
else
    echo "[$TIMESTAMP] ✅ Tailscale 连接正常" >> $LOG_FILE
fi

echo "[$TIMESTAMP] 健康检查完成" >> $LOG_FILE
exit 0
EOF

chmod +x ~/.openclaw/workspace/feishu-healthcheck.sh
```

### 配置定时检查

```bash
# 添加 cron 任务（每 5 分钟检查一次）
(crontab -l 2>/dev/null; echo "*/5 * * * * ~/.openclaw/workspace/feishu-healthcheck.sh") | crontab -

# 验证 cron 配置
crontab -l
```

### 手动测试脚本

```bash
# 运行一次健康检查
~/.openclaw/workspace/feishu-healthcheck.sh

# 查看日志
tail -20 /tmp/feishu-healthcheck.log
```

---

## 6. 查看 NAS 共享状态

```bash
# 检查 NAS 挂载
df -h | grep -i nas

# 检查挂载点内容
ls -la /Volumes/yokeplay/openclaw/
```

---

## 7. 问题排查清单

| 问题 | 检查命令 | 解决方案 |
|------|---------|---------|
| Gateway 未运行 | `ps aux \| grep openclaw` | `openclaw gateway restart` |
| 飞书 Token 失败 | `curl` 测试 | 检查 App ID/Secret |
| Tailscale 断开 | `ping 100.82.219.91` | `tailscale up` |
| NAS 挂载丢失 | `df -h \| grep nas` | 重新挂载 |

---

## 8. 汇报信息

请将以下信息发送给潘总：

1. **Gateway 状态输出**
2. **飞书配置（脱敏后）**
3. **Token 测试结果**
4. **健康检查脚本部署状态**
5. **最近日志中的错误（如有）**

---

*创建时间：2026-03-20*
*适用于：御影 (Mac mini) Gateway 健康检查*
