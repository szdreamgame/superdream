# 译文 - 视频处理技能

## 描述
在漫剧群中接收视频文件，调用 Coze 工作流生成文字稿和剧本。

## 触发条件
- **群聊 ID**: `oc_95a9882e1aca9546c1930b2d27660a6a`（漫剧 - 文案评审群）
- **消息类型**: 视频文件
- **提及**: @译文 或 @feishubot
- **命令**: `/文字`, `/转写`, `/识别`, `/译文`

## 处理流程

### 1. 接收视频消息
当群聊中收到视频消息且满足触发条件时，激活此技能。

### 2. 下载视频文件
从飞书下载视频文件到本地临时目录。

### 3. 上传到 OSS
```python
python3 /root/.openclaw/workspace/tools/coze_transcribe.py
# 或直接调用 upload_to_oss() 函数
```

### 4. 调用 Coze 工作流
```bash
curl -X POST "https://ny5xtnd234.coze.site/run" \
  -H "Authorization: Bearer {COZE_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "video_file": {
      "url": "{OSS_URL}",
      "file_type": "video"
    }
  }'
```

### 5. 返回结果
将识别结果（文字稿 + 剧本）发送到飞书群。

## 配置

### Coze 配置
- **Workflow URL**: `https://ny5xtnd234.coze.site/run`
- **Token**: 存储在 `/root/.openclaw/credentials/coze.json`

### OSS 配置
- **Bucket**: `openclaw-mjai`
- **Region**: `cn-shanghai`
- **凭证**: 存储在 `/root/.openclaw/credentials/aliyun-nls.json`

## 示例

### 用户消息
```
[视频文件] @译文
```

### Bot 回复
```
✅ **识别完成！**

**文字稿**：
你是做什么工作的？这不刚从缅甸回来，还没找到工作吗？他是海归...

**剧本**：
【主要角色】
介绍人：男，48 岁，职业媒人...
【场景设定】
连锁奶茶店卡座...
【完整剧本】
【介绍人】：你是做什么工作的？
【相亲女】：我在酒吧跳舞...
```

## 注意事项

1. **视频大小限制**: 建议 < 100MB
2. **处理时间**: 约 30-60 秒
3. **支持格式**: mp4, mov, avi, mkv, flv
4. **Token 有效期**: 定期检查 Coze Token 是否有效

## 相关文件

- `/root/.openclaw/workspace/agents/message_handler.py` - 消息处理脚本
- `/root/.openclaw/workspace/tools/coze_transcribe.py` - Coze 调用工具
- `/root/.openclaw/workspace/agents/routes.json` - 路由配置
- `/root/.openclaw/workspace/agents/config.json` - Agent 配置
