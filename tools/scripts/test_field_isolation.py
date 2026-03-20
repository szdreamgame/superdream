#!/usr/bin/env python3
"""
字段隔离逻辑测试脚本
验证严格使用修改后内容，避免混淆修改前内容
"""

# ==================== 字段隔离函数 ====================

def get_character_desc(fields):
    """
    获取角色描述 - 严格使用修改后或修改前，避免混淆
    
    Returns:
        tuple: (描述内容，来源字段名)
    """
    modified = fields.get('修改后角色', '').strip()
    original = fields.get('主要角色', '').strip()
    
    # 优先使用修改后，只有修改后为空时才使用修改前
    if modified:
        return modified, "修改后角色"
    elif original:
        return original, "主要角色"
    else:
        return "", ""


def get_scene_desc(fields):
    """
    获取场景描述 - 严格使用修改后或修改前，避免混淆
    
    Returns:
        tuple: (描述内容，来源字段名)
    """
    modified = fields.get('修改后场景', '').strip()
    original = fields.get('场景设定', '').strip()
    
    # 优先使用修改后，只有修改后为空时才使用修改前
    if modified:
        return modified, "修改后场景"
    elif original:
        return original, "场景设定"
    else:
        return "", ""


# ==================== 测试用例 ====================

def test_case_1():
    """测试：修改后字段有值，应使用修改后"""
    fields = {
        '修改后角色': '妈妈：女，28 岁，长相温和甜美，身高 165cm，穿着居家休闲睡衣',
        '主要角色': '妈妈：28 岁，漂亮女性，穿睡衣，有威严',
        '修改后场景': '客厅：普通民居的客厅，摆放着沙发和茶几，光线明亮',
        '场景设定': '家庭室内（客厅/起居室），白天，光线充足，温馨的家庭氛围。道具：两部手机。'
    }
    
    char_desc, char_source = get_character_desc(fields)
    scene_desc, scene_source = get_scene_desc(fields)
    
    assert char_source == "修改后角色", f"期望'修改后角色'，实际'{char_source}'"
    assert scene_source == "修改后场景", f"期望'修改后场景'，实际'{scene_source}'"
    assert "两部手机" not in scene_desc, "场景描述不应包含修改前的'两部手机'"
    
    print("✅ 测试 1 通过：修改后字段有值时，正确使用修改后内容")
    print(f"   角色：{char_source} - {char_desc[:30]}...")
    print(f"   场景：{scene_source} - {scene_desc[:30]}...")


def test_case_2():
    """测试：修改后字段为空，应回退到修改前"""
    fields = {
        '修改后角色': '',
        '主要角色': '妈妈：28 岁，漂亮女性，穿睡衣',
        '修改后场景': '   ',  # 只有空白
        '场景设定': '家庭室内（客厅/起居室），白天，光线充足'
    }
    
    char_desc, char_source = get_character_desc(fields)
    scene_desc, scene_source = get_scene_desc(fields)
    
    assert char_source == "主要角色", f"期望'主要角色'，实际'{char_source}'"
    assert scene_source == "场景设定", f"期望'场景设定'，实际'{scene_source}'"
    
    print("✅ 测试 2 通过：修改后字段为空时，正确回退到修改前")
    print(f"   角色：{char_source} - {char_desc[:30]}...")
    print(f"   场景：{scene_source} - {scene_desc[:30]}...")


def test_case_3():
    """测试：修改后字段有部分值（如只有角色，场景为空）"""
    fields = {
        '修改后角色': '妈妈：女，28 岁，长相温和甜美',
        '主要角色': '妈妈：28 岁，漂亮女性',
        '修改后场景': '',  # 空
        '场景设定': '家庭室内（客厅/起居室），白天'
    }
    
    char_desc, char_source = get_character_desc(fields)
    scene_desc, scene_source = get_scene_desc(fields)
    
    assert char_source == "修改后角色", f"期望'修改后角色'，实际'{char_source}'"
    assert scene_source == "场景设定", f"期望'场景设定'，实际'{scene_source}'"
    
    print("✅ 测试 3 通过：部分字段有值时，分别正确处理")
    print(f"   角色：{char_source} - {char_desc[:30]}...")
    print(f"   场景：{scene_source} - {scene_desc[:30]}...")


def test_case_4():
    """测试：真实表格数据（recve5E3TyZmSL 记录）"""
    fields = {
        '修改后角色': '妈妈：女，28 岁，长相温和甜美，身高 165cm，性格稳重，穿着居家休闲睡衣 | 哥哥：男，12 岁，小学生，正太，身材偏瘦，性格沉稳懂事，穿着圆领 T 恤运动短裤。/弟弟：男，8 岁，小学生，正太，圆脸蛋，留齐刘海，性格好奇活泼，穿着卡通印花短袖牛仔中裤',
        '主要角色': '妈妈：28 岁，漂亮女性，穿睡衣，有威严，注重隐私，对孩子有明确规则 | 哥哥：约 8-12 岁，懂事，有经验，会照顾弟弟/妹妹 | 弟弟/妹妹：约 5-8 岁，好奇，天真',
        '修改后场景': '客厅：普通民居的客厅，摆放着沙发和茶几，光线明亮，氛围日常',
        '场景设定': '家庭室内（客厅/起居室），白天，光线充足，温馨的家庭氛围。道具：两部手机。妈妈要和爸爸进房间谈私密事情，孩子们被安排在客厅玩手机。'
    }
    
    char_desc, char_source = get_character_desc(fields)
    scene_desc, scene_source = get_scene_desc(fields)
    
    assert char_source == "修改后角色", f"期望'修改后角色'，实际'{char_source}'"
    assert scene_source == "修改后场景", f"期望'修改后场景'，实际'{scene_source}'"
    assert "两部手机" not in scene_desc, "场景描述不应包含修改前的'两部手机'"
    assert "私密事情" not in scene_desc, "场景描述不应包含修改前的'私密事情'"
    
    print("✅ 测试 4 通过：真实表格数据，正确使用修改后内容，未混入修改前内容")
    print(f"   角色：{char_source} - {len(char_desc)}字")
    print(f"   场景：{scene_source} - {scene_desc}")


# ==================== 运行测试 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("字段隔离逻辑测试")
    print("=" * 60)
    print()
    
    test_case_1()
    print()
    
    test_case_2()
    print()
    
    test_case_3()
    print()
    
    test_case_4()
    print()
    
    print("=" * 60)
    print("✅ 所有测试通过！字段隔离逻辑正常工作")
    print("=" * 60)
