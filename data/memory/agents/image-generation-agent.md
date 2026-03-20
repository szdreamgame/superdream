# AI 图片生成工作室 - 专属 AGENT 配置

> 🎨 Nano Banana 2 图片生成专属 AGENT  
> **创建时间**: 2026-03-16  
> **专属群**: AI 图片生成工作室

---

## 📋 AGENT 配置

### 基本信息

| 项目 | 值 |
|------|-----|
| **AGENT 名称** | 图片生成助手 |
| **专属群** | AI 图片生成工作室 |
| **触发方式** | 关键词 + @BOT |
| **处理模型** | Nano Banana 2 |

---

## 🎯 监听规则

### 1. 群聊限定

```json
{
  "target_chat_id": "待填写（创建群后更新）",
  "target_chat_name": "AI 图片生成工作室",
  "listen_only_this_chat": true
}
```

### 2. 触发关键词

| 关键词 | 动作 | 示例 |
|--------|------|------|
| `生成图片` | 生成图片任务 | "生成图片，记录 ID: xxx" |
| `生成角色` | 生成角色设定图 | "生成角色，风格：写实" |
| `生成场景` | 生成场景设定图 | "生成场景，风格：现代都市" |
| `@译文` | 响应提及 | "@译文 这条需要生成" |
| `/generate` | 命令模式 | "/generate recljJN0oH" |

---

## 🔄 处理流程

### 标准流程

```
1. 群内收到消息
   ↓
2. 检测关键词/提及
   ↓
3. 解析指令（记录 ID、风格等）
   ↓
4. 读取飞书表格
   ↓
5. 应用提示词模板
   ↓
6. 调用 Nano Banana API
   ↓
7. 下载并上传图片
   ↓
8. 群内通知结果
```

### 状态通知

| 阶段 | 群内通知 |
|------|----------|
| 接收任务 | "✅ 已接收任务，开始处理..." |
| 生成中 | "⏳ 图片生成中，进度：XX%" |
| 完成 | "✅ 生成完成！[图片链接]" |
| 失败 | "❌ 生成失败，原因：XXX" |

---

## 📝 指令格式

### 简单模式

```
生成图片
生成角色
生成场景
```

自动处理最新一条"待生成图片"状态的记录。

### 指定记录

```
生成图片，记录 ID: recljJN0oH
/generate recljJN0oH
```

处理指定记录。

### 指定风格

```
生成角色，风格：写实
生成场景，风格：现代都市，记录 ID: xxx
```

使用指定风格模板。

### 自定义提示词

```
生成角色，提示词：角色设定图，真实照片质感，...
```

使用自定义提示词。

---

## 🔧 技术实现

### 1. 消息监听器

```python
# nano-banana-agent.py

TARGET_CHAT_ID = "待填写"  # 专属群 ID

def should_process_message(event):
    """
    判断是否应该处理该消息
    """
    # 只处理专属群
    if event.chat_id != TARGET_CHAT_ID:
        return False
    
    # 检测关键词
    keywords = ['生成图片', '生成角色', '生成场景', '/generate']
    message_text = event.message.content.lower()
    
    # 检测是否@BOT
    is_mentioned = check_bot_mention(event)
    
    # 满足任一条件即处理
    return is_mentioned or any(kw in message_text for kw in keywords)
```

### 2. 指令解析器

```python
def parse_generation_command(message):
    """
    解析生成指令
    
    Returns:
        dict: {
            'record_id': str,
            'style': str,
            'type': 'character' | 'scene',
            'custom_prompt': str
        }
    """
    import re
    
    # 提取记录 ID
    record_match = re.search(r'记录 ID[:\s]*([a-zA-Z0-9]+)', message)
    record_id = record_match.group(1) if record_match else None
    
    # 提取风格
    style_match = re.search(r'风格[:\s]*(\S+)', message)
    style = style_match.group(1) if style_match else '写实风格'
    
    # 判断类型
    if '角色' in message:
        gen_type = 'character'
    elif '场景' in message:
        gen_type = 'scene'
    else:
        gen_type = 'both'
    
    return {
        'record_id': record_id,
        'style': style,
        'type': gen_type,
        'custom_prompt': None
    }
```

### 3. 群内通知

```python
def notify_chat(chat_id, status, message_data):
    """
    在群内发送进度通知
    
    Args:
        chat_id: 群 ID
        status: 'started' | 'progress' | 'completed' | 'failed'
        message_data: 通知内容数据
    """
    templates = {
        'started': "✅ 已接收任务\n📊 记录：{record_name}\n🎨 风格：{style}\n⏱️ 预计耗时：3-5 分钟",
        'progress': "⏳ 图片生成中...\n📈 进度：{progress}%",
        'completed': "✅ 生成完成！\n🎨 类型：{type}\n📎 图片：{image_url}\n💡 提示词：{prompt}",
        'failed': "❌ 生成失败\n原因：{error}\n建议：{suggestion}"
    }
    
    message = templates[status].format(**message_data)
    send_to_chat(chat_id, message)
```

---

## 📊 表格集成

### 状态流转

```
待生成图片 → 生成中 → 图片已完成
                ↓
            生成失败（可选）
```

### 字段更新

| 字段 | 更新时机 | 值 |
|------|----------|-----|
| 图片生成状态 | 开始生成 | "生成中" |
| 图片生成状态 | 生成完成 | "图片已完成" |
| 角色设定图 | 完成 | 图片 URL |
| 场景设定图 | 完成 | 图片 URL |
| 图片生成时间 | 完成 | 当前时间 |

---

## 🎨 提示词应用

### 自动选择模板

```python
def apply_style_template(record, style_name):
    """
    应用风格模板
    
    Args:
        record: 表格记录
        style_name: 风格名称（如"写实风格"）
    
    Returns:
        str: 最终提示词
    """
    # 从模板库读取
    template = load_prompt_template(style_name)
    
    # 获取角色/场景描述
    base_desc = record.get('修改后角色') or record.get('修改后场景')
    
    # 拼接提示词
    final_prompt = f"{template['prefix']}, {base_desc}, {template['quality']}, {template['suffix']}"
    
    return final_prompt
```

---

## ⚙️ 配置项

### 环境变量

```bash
# 专属群 ID
IMAGE_GEN_CHAT_ID="oc_xxxxxxxxxxxxx"

# GRS AI API
GRS_API_KEY="sk-xxxxx"

# 飞书应用
FEISHU_APP_ID="cli_xxxxx"
FEISHU_APP_SECRET="xxxxx"

# 表格配置
BITABLE_APP_TOKEN="GHrubiTjnayG4fsWP2IcJIotnfc"
BITABLE_TABLE_ID="tbl8ik4qLltAlXvp"
```

### 运行时配置

```python
# 轮询间隔
POLL_INTERVAL = 60  # 秒

# 并发限制
MAX_CONCURRENT_TASKS = 3

# 超时设置
API_TIMEOUT = 300  # 秒

# 重试次数
MAX_RETRIES = 3
```

---

## 📝 使用示例

### 示例 1: 简单生成

**用户**: `@译文 生成图片`

**BOT**:
```
✅ 已接收任务
📊 表格：街头摄影师搭讪车主
🎨 类型：角色设定图
🎭 风格：写实风格
⏱️ 预计耗时：3-5 分钟

开始处理...
```

**3 分钟后**:
```
✅ 生成完成！
📎 图片：https://...
💡 提示词：角色设定图，真实照片质感，车主：女，25 岁...
```

---

### 示例 2: 指定风格

**用户**: `生成角色，风格：卡通 Q 版，记录 ID: recljJN0oH`

**BOT**:
```
✅ 已接收任务
📊 记录：街头摄影师搭讪车主
🎨 类型：角色设定图
🎭 风格：卡通 Q 版
⏱️ 开始处理...
```

---

### 示例 3: 批量生成

**用户**: `生成这张的角色和场景`

**BOT**:
```
✅ 已接收任务
📊 记录：街头摄影师搭讪车主
🎨 任务：角色设定图 + 场景设定图
⏱️ 预计耗时：5-8 分钟

[1/2] 生成角色设定图...
```

---

## 🔐 权限控制

### 允许的用户

| 用户 | 权限 |
|------|------|
| 潘泽霖 | 管理员（所有权限） |
| 周瑜 | 编辑（生成 + 修改模板） |
| 倪亭玉 | 用户（仅生成） |

### 命令权限

| 命令 | 权限要求 |
|------|----------|
| 生成图片 | 所有成员 |
| 修改模板 | 管理员/周瑜 |
| 查看配置 | 管理员 |
| 重启服务 | 管理员 |

---

## 📈 监控和日志

### 日志记录

```python
# 记录每次生成
log_generation({
    'timestamp': '2026-03-16 16:00:00',
    'user': '潘泽霖',
    'record_id': 'recljJN0oH',
    'style': '写实风格',
    'duration': 245,  # 秒
    'status': 'success',
    'image_url': 'https://...'
})
```

### 统计数据

- 每日生成数量
- 平均生成时间
- 成功率统计
- 风格使用频率

---

## 🚀 部署步骤

1. **创建专属群**
   - 群名：AI 图片生成工作室
   - 成员：潘泽霖、周瑜、倪亭玉、译文 BOT

2. **获取群 ID**
   - 从飞书群信息中复制

3. **更新配置**
   - 设置 `TARGET_CHAT_ID`
   - 更新环境变量

4. **启动服务**
   ```bash
   python3 nano-banana-agent.py
   ```

5. **测试验证**
   - 在群内发送测试指令
   - 确认响应正常

---

*配置完成时间：2026-03-16*
