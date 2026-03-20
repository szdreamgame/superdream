#!/bin/bash
# 飞书健康检查脚本
# 检查 Gateway 状态和飞书连接

LOG_FILE="/tmp/feishu-healthcheck.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$TIMESTAMP] 开始健康检查..." >> "$LOG_FILE"

# 检查 Gateway 状态
if ! pgrep -f "openclaw.*gateway" > /dev/null; then
    echo "[$TIMESTAMP] ❌ Gateway 未运行" >> "$LOG_FILE"
    exit 1
fi
echo "[$TIMESTAMP] ✅ Gateway 运行正常" >> "$LOG_FILE"

# 检查飞书 Token
APP_ID="cli_a92e8b3399b85cd6"
APP_SECRET="tMiX2hL0wTf7ujPSK2pqnf3d3aeg8AGa"

TOKEN=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d "{\"app_id\":\"$APP_ID\",\"app_secret\":\"$APP_SECRET\"}" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tenant_access_token',''))")

if [ -z "$TOKEN" ]; then
    echo "[$TIMESTAMP] ❌ 飞书 Token 获取失败" >> "$LOG_FILE"
    exit 1
fi
echo "[$TIMESTAMP] ✅ 飞书连接正常 (Token: ${TOKEN:0:20}...)" >> "$LOG_FILE"

# 检查 Gateway 端口监听状态
if ss -tlnp 2>/dev/null | grep -q ":15427" || netstat -tlnp 2>/dev/null | grep -q ":15427"; then
    echo "[$TIMESTAMP] ✅ Gateway 端口 15427 监听正常" >> "$LOG_FILE"
else
    echo "[$TIMESTAMP] ⚠️ Gateway 端口 15427 未监听" >> "$LOG_FILE"
fi

echo "[$TIMESTAMP] 健康检查完成" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
exit 0
