#!/bin/bash
# 测试 Coze 工作流 API

echo "======================================"
echo "测试 Coze 工作流 API"
echo "======================================"

# 测试视频 URL（替换成你的 OSS 视频 URL）
VIDEO_URL="https://openclaw-mjai.oss-cn-shanghai.aliyuncs.com/coze/238a805f8bc447318b08bc7aa865244d_test_video.mp4"

# Coze 配置
COZE_URL="https://ny5xtnd234.coze.site/run"
COZE_TOKEN="eyJhbGciOiJSUzI1NiIsImtpZCI6IjUyMmYxMWE3LTM2Y2EtNGQ0Ny04NjEyLWVlZTk5MTg5MWM3YSJ9.eyJpc3MiOiJodHRwczovL2FwaS5jb3plLmNuIiwiYXVkIjpbIlRzRFU3SlBXWnU1aTdxQ2JjbHFIdTJydEZ0R0ltM3UzIl0sImV4cCI6ODIxMDI2Njg3Njc5OSwiaWF0IjoxNzczNDk1MzE4LCJzdWIiOiJzcGlmZmU6Ly9hcGkuY296ZS5jbi93b3JrbG9hZF9pZGVudGl0eS9pZDo3NjE3MDkwOTEyNDA5MDkyMTM2Iiwic3JjIjoiaW5ib3VuZF9hdXRoX2FjY2Vzc190b2tlbl9pZDo3NjE3MTA0Mzk0MTMxMDc5MTk0In0.DkmxlJW3cUNvWBoVsQpOIhs1oNkpWeZe3sQ7PL78H1Opgs2qf7Qsnx7kBQs1zE2UnjcGUG_MIpG492ixCzYGkN85539OUR8cTMzHP6XE8H0calvXCRvXDJoAZT0wh-ANHaC6aXYBRGhOf4h3SenYe57DXDoGxQDrpKMoUcuIAIFV43niNZh3bxYA4p231AGItskbDIKznL8557ORQ21JL8Qfz1OibIcEZTHcSy4LbGyYyKfTw2RhBCenbuIIMa4R_Hfl45XRldklZj-XTDTlqLxPvas1PfNeeNVm8GSZqiaEosWx7b9YhygsyVr7mJBCnk-xAPPi_dJiqyK5XBAQsQ"

echo "视频 URL: $VIDEO_URL"
echo "Coze URL: $COZE_URL"
echo ""
echo "调用 Coze API..."
echo ""

# 调用 API
curl -X POST "$COZE_URL" \
  -H "Authorization: Bearer $COZE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"video_file\": {
      \"url\": \"$VIDEO_URL\",
      \"file_type\": \"video\"
    }
  }" | jq '.'

echo ""
echo "======================================"
