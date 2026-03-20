#!/bin/bash
# 上传视频到 OSS 并发送链接到飞书群

VIDEO_FILE="$1"
CHAT_ID="oc_95a9882e1aca9546c1930b2d27660a6a"

if [ -z "$VIDEO_FILE" ]; then
  echo "用法：$0 <视频文件路径>"
  echo "示例：$0 /path/to/video.mp4"
  exit 1
fi

echo "======================================"
echo "上传视频到 OSS"
echo "======================================"

# 上传到 OSS
OSS_URL=$(python3.8 /root/.openclaw/workspace/tools/coze_transcribe.py "$VIDEO_FILE" 2>&1 | grep "✅ 上传成功" | grep -o "https://[^ ]*")

if [ -z "$OSS_URL" ]; then
  echo "❌ 上传失败"
  exit 1
fi

echo "✅ 上传成功！"
echo "URL: $OSS_URL"
echo ""
echo "======================================"
echo "发送到飞书群"
echo "======================================"

# 发送到飞书群
curl -X POST "http://localhost:15427/api/message/send" \
  -H "Content-Type: application/json" \
  -d "{
    \"channel\": \"feishu\",
    \"target\": \"$CHAT_ID\",
    \"message\": \"@译文 $OSS_URL\"
  }"

echo ""
echo "✅ 已发送到飞书群！"
echo "======================================"
