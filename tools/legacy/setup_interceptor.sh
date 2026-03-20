#!/bin/bash
# 设置译文视频处理拦截器

echo "======================================"
echo "设置译文视频处理拦截器"
echo "======================================"

# 检查 OpenClaw 配置目录
OPENCLAW_DIR="/root/.local/share/pnpm/global/5/.pnpm/openclaw@2026.3.8_@discordjs+opus@0.10.0_@napi-rs+canvas@0.1.96_@types+express@5.0.6_hono@4.12.5_node-llama-cpp@3.16.2/node_modules/openclaw"

# 备份原配置
echo "备份原配置..."
cp "$OPENCLAW_DIR/extensions/feishu/src/channel.ts" "$OPENCLAW_DIR/extensions/feishu/src/channel.ts.bak" 2>/dev/null

# 创建拦截器配置
echo "创建拦截器配置..."
cat > "$OPENCLAW_DIR/interceptors.config.json" << 'EOF'
{
  "interceptors": [
    {
      "id": "feishu_video_translator",
      "name": "译文 - 视频处理",
      "enabled": true,
      "path": "/root/.openclaw/workspace/interceptors/feishu_video.js",
      "priority": 10,
      "conditions": {
        "channel": "feishu",
        "chat_id": "oc_95a9882e1aca9546c1930b2d27660a6a",
        "message_type": "video",
        "mention_bot": true
      }
    }
  ]
}
EOF

echo "✅ 拦截器配置完成！"
echo ""
echo "配置文件位置："
echo "  - $OPENCLAW_DIR/interceptors.config.json"
echo ""
echo "拦截器脚本："
echo "  - /root/.openclaw/workspace/interceptors/feishu_video.js"
echo ""
echo "现在重启 OpenClaw 使配置生效："
echo "  openclaw restart"
echo ""
echo "======================================"
