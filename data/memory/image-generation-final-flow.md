# 画语 BOT - 最终版图片生成流程

> **版本**: 4.0 (字段隔离版)  
> **维护负责人**: 周瑜  
> **最后更新**: 2026-03-17 18:19  
> **脚本位置**: `/root/.openclaw/workspace/scripts/nano-banana-agent.py`

---

## 🚀 核心特性

### ✅ 字段隔离逻辑

**原则**：严格二选一，不拼接、不合并修改前后内容

```python
def get_character_desc(fields):
    """获取角色描述 - 严格使用修改后或修改前"""
    modified = fields.get('修改后角色', '').strip()
    original = fields.get('主要角色', '').strip()
    
    if modified:
        return modified, "修改后角色"
    elif original:
        return original, "主要角色"
    else:
        return "", ""

def get_scene_desc(fields):
    """获取场景描述 - 严格使用修改后或修改前"""
    modified = fields.get('修改后场景', '').strip()
    original = fields.get('场景设定', '').strip()
    
    if modified:
        return modified, "修改后场景"
    elif original:
        return original, "场景设定"
    else:
        return "", ""
```

**优先级**：
1. 优先使用**修改后**字段
2. 修改后为空时回退到**修改前**字段
3. **不拼接、不合并**两个字段内容

---

## 📋 提示词结构（最终版）

### 角色设定图

```
{固定前缀} + {角色描述} + {质量词}
```

**固定前缀**：
```
Character design sheet, three views (front view, side view, back view), close-up portrait, pure white background, no text, no watermark, clean background.
```

**示例**：
```
Character design sheet, three views (front view, side view, back view), close-up portrait, pure white background, no text, no watermark, clean background. 妈妈：女，28 岁，长相温和甜美，身高 165cm，性格稳重，穿着居家休闲睡衣，BanG Dream! It's MyGO!!!!!动画画风，3d 渲染 2d，3D，动画截图，大师级构图
```

---

### 场景设定图

```
{固定前缀} + {场景描述} + {质量词}
```

**固定前缀**：
```
Background scene, environment design, no characters, no people, pure environment only.
```

**示例**：
```
Background scene, environment design, no characters, no people, pure environment only. 客厅：普通民居的客厅，摆放着沙发和茶几，光线明亮，氛围日常，BanG Dream! It's MyGO!!!!!动画画风，3d 渲染 2d，3D，动画截图，大师级构图
```

---

## ⚙️ 默认配置（周瑜配置）

| 参数 | 值 | 说明 |
|------|-----|------|
| **模型** | `nano-banana-2` | 默认模型 |
| **比例** | `16:9` | 所有图片统一横版 |
| **批次** | `x2` | 每个角色/场景生成 2 张 |
| **尺寸** | `1K` | 标准质量 |
| **风格** | `日式 3D 渲染 2D` | 默认画风 |
| **质量词** | `BanG Dream! It's MyGO!!!!!动画画风，3d 渲染 2d，3D，动画截图，大师级构图` | 默认质量词 |

---

## 🎯 完整流程

### 步骤 1: 读取表格字段

```python
# 字段隔离 - 严格二选一
char_desc, char_source = get_character_desc(fields)
scene_desc, scene_source = get_scene_desc(fields)

# 日志记录来源
log(f"📋 角色描述来源：{char_source} ({len(char_desc)}字)")
log(f"📋 场景描述来源：{scene_source} ({len(scene_desc)}字)")
```

### 步骤 2: 构建提示词

```python
# 角色图提示词
prompt = build_prompt_with_template(char_desc, '日式 3D 渲染 2D', 'character')

# 场景图提示词
prompt = build_prompt_with_template(scene_desc, '日式 3D 渲染 2D', 'scene')
```

### 步骤 3: 批量生成（循环调用 API）

```python
# 每个角色/场景生成 2 张
for i in range(GENERATE_BATCH):  # GENERATE_BATCH = 2
    image_url = call_nano_banana_api(prompt, aspect_ratio="16:9")
    generated_urls.append((type_label, image_url, i+1))
```

**注意**：不使用 API 的 `n` 参数，而是循环调用 API 实现批量。

### 步骤 4: 轮询进度

```python
# 最多轮询 8 次，每次间隔 20 秒
for round in range(8):
    result = poll_task_result(task_id)
    if result['status'] == 'succeeded':
        return result['url']
    sleep(20)
```

### 步骤 5: 失败重试

```python
# 失败任务自动重试一次
if status == 'failed':
    retry_task_id = submit_retry_task(prompt)
    poll_task_result(retry_task_id)
```

### 步骤 6: 更新表格

```python
# 更新状态为"图片已完成"
update_record_status(record_key, '已完成', generated_urls[0][1])
```

---

## 📊 字段隔离测试

测试脚本：`/root/.openclaw/workspace/scripts/test_field_isolation.py`

### 测试用例

1. ✅ **修改后字段有值** - 正确使用修改后内容
2. ✅ **修改后字段为空** - 正确回退到修改前
3. ✅ **部分字段有值** - 分别正确处理
4. ✅ **真实表格数据** - 未混入修改前内容（如"两部手机"、"私密事情"）

### 测试结果

```
✅ 测试 1 通过：修改后字段有值时，正确使用修改后内容
✅ 测试 2 通过：修改后字段为空时，正确回退到修改前
✅ 测试 3 通过：部分字段有值时，分别正确处理
✅ 测试 4 通过：真实表格数据，正确使用修改后内容，未混入修改前内容
```

---

## ⚠️ 常见错误避免

### ❌ 错误：拼接两个字段

```python
# 错误示例
desc = fields.get('修改后场景', '') + fields.get('场景设定', '')
# 结果："客厅：... + 道具：两部手机。妈妈要..."
```

### ✅ 正确：严格二选一

```python
# 正确示例
modified = fields.get('修改后场景', '').strip()
if modified:
    desc = modified  # 只用修改后
else:
    desc = fields.get('场景设定', '').strip()  # 回退到修改前
```

---

## 📝 提示词模板库

### 日式 3D 渲染 2D（默认风格）

```python
'日式 3D 渲染 2D': {
    'prefix': '角色设定图',  # 已移除，不使用
    'quality': "BanG Dream! It's MyGO!!!!!动画画风，3d 渲染 2d，3D，动画截图，大师级构图",
    'suffix': '日式 3D 品质'  # 已移除，不使用
}
```

**实际使用的部分**：只有 `quality` 字段

---

## 🔗 相关文件

| 文件 | 路径 | 说明 |
|------|------|------|
| **主脚本** | `/root/.openclaw/workspace/scripts/nano-banana-agent.py` | 画语 BOT 主程序 |
| **测试脚本** | `/root/.openclaw/workspace/scripts/test_field_isolation.py` | 字段隔离逻辑测试 |
| **流程文档** | `/root/.openclaw/workspace/memory/image-generation-final-flow.md` | 本文档 |
| **提示词模板** | `/root/.openclaw/workspace/memory/prompts/image-generation.md` | 完整模板库 |

---

## 📈 更新日志

| 日期 | 版本 | 更新内容 | 维护人 |
|------|------|----------|--------|
| 2026-03-17 | 4.0 | 字段隔离逻辑，严格使用修改后内容 | 周瑜 |
| 2026-03-17 | 3.0 | 移除类型和后缀，简化提示词结构 | 周瑜 |
| 2026-03-16 | 2.0 | 添加批量生成 x2 逻辑 | 周瑜 |
| 2026-03-16 | 1.0 | 初始版本 | 周瑜 |

---

*维护负责人：周瑜 | 最后更新：2026-03-17 18:19*
