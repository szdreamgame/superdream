#!/usr/bin/env python3
"""
AI 图片生成工作室 - 专属 AGENT
Nano Banana 2 图片生成专属机器人

功能：
- 监听专属群消息
- 响应图片生成指令
- 自动处理表格任务
- 群内进度通知
"""

import os
import re
import sys
import time
import json
import requests
from datetime import datetime

# ==================== 配置区域 ====================

# 专属群配置
TARGET_CHAT_ID = "oc_f22ffe36d557729c0d77f8b11c74e0bd"  # AI 图片生成工作室
TARGET_CHAT_NAME = "AI 图片生成工作室"
BOT_NAME = "画语"  # 专属 BOT 名称

# GRS AI API 配置
GRS_API_HOST = "https://grsai.dakka.com.cn"
GRS_API_KEY = os.environ.get("GRS_API_KEY", "sk-10eee66de80245e78277514e88a67401")

# 默认生成参数（周瑜配置）
DEFAULT_MODEL = "nano-banana-2"  # 默认模型
DEFAULT_ASPECT_RATIO = "16:9"    # 默认比例（所有图片）
DEFAULT_BATCH_SIZE = 2           # 默认生成批次 x2
DEFAULT_IMAGE_SIZE = "1K"        # 默认尺寸

# 画面描述固定前缀（周瑜配置）
CHARACTER_PREFIX = "Character design sheet, three views (front view, side view, back view), close-up portrait, pure white background, no text, no watermark, clean background"  # 角色设定图前缀（英文提示词更有效）
SCENE_PREFIX = "Background scene, environment design, no characters, no people, pure environment only"  # 场景设定图前缀（英文提示词更有效）

# 批量生成配置
GENERATE_BATCH = 2  # 每个角色/场景生成 2 张供选择

# ==================== 字段隔离函数（周瑜配置） ====================
# 核心原则：严格二选一，不拼接、不合并修改前后内容

def get_character_desc(fields):
    """
    获取角色描述 - 严格使用修改后或修改前，避免混淆
    
    Args:
        fields: 表格字段字典
    
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
    
    Args:
        fields: 表格字段字典
    
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


# 飞书配置
BITABLE_APP_TOKEN = "GHrubiTjnayG4fsWP2IcJIotnfc"
BITABLE_TABLE_ID = "tbl8ik4qLltAlXvp"
FEISHU_APP_ID = os.environ.get("FEISHU_APP_ID", "cli_a92e8b3399b85cd6")
FEISHU_APP_SECRET = os.environ.get("FEISHU_APP_SECRET", "tMiX2hL0wTf7ujPSK2pqnf3d3aeg8AGa")

# 提示词模板库 v2 (48 种风格完整版)
# 维护负责人：周瑜
PROMPT_TEMPLATES = {
    # ========== 2D 风格 (32 种) ==========
    '2D Q 版': {
        'prefix': '角色设定图，二次元 Q 版风格',
        'quality': '2D 卡通风格，平面 Q 版人物，Q 版，线条感',
        'suffix': '大师级构图，高清'
    },
    '2D 粗线条': {
        'prefix': '角色设定图',
        'quality': '飞天小女警画风，吊带袜天使画风，线条硬朗，夸张，杰作，简约线条',
        'suffix': '大师级构图'
    },
    '2D 电影': {
        'prefix': '角色设定图',
        'quality': '参考新海诚动画作品，新海诚画风，2D 动画，大师级构图，氛围感，叙事感，高清，画面精致',
        'suffix': '工作室品质'
    },
    '2D 动画': {
        'prefix': '角色设定图',
        'quality': '参考京都动画作品，参考石立太一动画作品，2d 动画，2D 日式动画',
        'suffix': '动画品质，高清'
    },
    '2D 哆小啦': {
        'prefix': '角色设定图',
        'quality': '哆啦 A 梦动画画风，藤子 F 不二雄画风，日式动画，2D，大师级构图',
        'suffix': '动画品质'
    },
    '2D 复古动画': {
        'prefix': '角色设定图',
        'quality': '参考渡边信一郎作品风格，参考神山健治作品，90 年代日本复古动漫风格，上世纪九十年代日漫风格的动漫，层次感，线条清晰，迷人氛围',
        'suffix': '复古品质'
    },
    '2D 复古少女': {
        'prefix': '角色设定图',
        'quality': 'The Rose of Versailles 动画画风，怪盗圣少女动画画风，2D 动画，日式动画',
        'suffix': '少女漫画风格'
    },
    '2D 工笔风': {
        'prefix': '角色设定图',
        'quality': '工笔风、线条细腻，参考传统工笔画（线条设计 + 色彩晕染），数字插画平涂、轻微晕染质感、弱化线条，超平滑，温暖怀旧、古典雅致',
        'suffix': '古典品质'
    },
    '2D 诡异惊悚': {
        'prefix': '角色设定图',
        'quality': '惊悚诡异风、线条锐利，参考伊藤润二动画（线条设计 + 色彩搭配 + 氛围营造），数字漫画笔触、轻微颗粒感、哑光质感，惊悚压抑、悬疑感',
        'suffix': '惊悚氛围'
    },
    '2D 韩式动画': {
        'prefix': '角色设定图',
        'quality': '金亨泰作品风格，NIKKE: The Goddess of Victory 画风，2D，游戏插画，线条流畅细腻圆润',
        'suffix': '游戏品质'
    },
    '2D 吉卜力动画': {
        'prefix': '角色设定图',
        'quality': '参考宫崎骏动画电影作品，吉卜力动画风格，宫崎骏，动画截图，动画电影，大师级构图，2d 动画画风，高清，画面精致',
        'suffix': '动画电影品质'
    },
    '2D 简笔画': {
        'prefix': '角色设定图',
        'quality': '手绘，简约线条艺术，简笔画，卡通，简洁，干净，大师杰作',
        'suffix': '简约风格'
    },
    '2D 简单线条': {
        'prefix': '角色设定图',
        'quality': '罗小黑战记动画风格，简单线条，2D 动画，flash 动画',
        'suffix': '简洁风格'
    },
    '2D 篮球高手': {
        'prefix': '角色设定图',
        'quality': '灌篮高手画风，日式动画画风，2D，动画截图',
        'suffix': '动画品质'
    },
    '2D 灵怪都市': {
        'prefix': '角色设定图',
        'quality': '咒术回战画风，2D 动画，日式动画，大师级构图，精致细节',
        'suffix': '都市奇幻风格'
    },
    '2D 美式动画': {
        'prefix': '角色设定图',
        'quality': '参考 90 年代迪士尼 2d 动画，美式动画风格，2D 动画，高清，大师构图，极致细节',
        'suffix': '迪士尼品质'
    },
    '2D 美式漫画': {
        'prefix': '角色设定图',
        'quality': '美式漫画风格，2D 手绘，线条感，大师级构图',
        'suffix': '漫画风格'
    },
    '2D 鸟山明': {
        'prefix': '角色设定图',
        'quality': '鸟山明动画作品风格，日式 2D 动画，动画截图，动画质感，弱化线条，大师级构图',
        'suffix': '龙珠风格'
    },
    '2D 奇幻动画': {
        'prefix': '角色设定图',
        'quality': '葬送的芙莉莲动画风格，动画截图，动画质感，弱化线条，极致细节，高清，大师级构图',
        'suffix': '奇幻风格'
    },
    '2D 乔乔风': {
        'prefix': '角色设定图',
        'quality': '乔乔的奇妙冒险动画画风，参考荒木飞吕彦动画画风，2D 动画，日式动画，大师级构图，极致细节，杰作',
        'suffix': 'JOJO 风格'
    },
    '2D 热血动画': {
        'prefix': '角色设定图',
        'quality': 'TRIGGER 动画作品画风，普罗米亚动画画风，斩服少女动画画风，2D 动画，大师级构图',
        'suffix': '热血风格'
    },
    '2D 日式侦探': {
        'prefix': '角色设定图',
        'quality': '名侦探柯南画风，2d 动画风格，日式动画风格，2D，动漫，高清细节，大师级构图',
        'suffix': '侦探风格'
    },
    '2D 少女漫画': {
        'prefix': '角色设定图',
        'quality': '二次元插画风、线条柔和，参考日式少女动画（线条设计 + 色彩搭配），数字插画平涂、轻微光泽质感、治愈松弛、温暖感，氛围感',
        'suffix': '少女风格'
    },
    '2D 手冢治虫': {
        'prefix': '角色设定图',
        'quality': '手冢治虫动画画风，2D，日式动画，动画截图，2D 动画，大师级构图，彩色',
        'suffix': '手冢风格'
    },
    '2D 水彩': {
        'prefix': '角色设定图',
        'quality': '水彩风格，氛围感，故事感，大师级构图，杰作，高清，极致细节',
        'suffix': '水彩画品质'
    },
    '2D 死亡之神': {
        'prefix': '角色设定图',
        'quality': 'bleach 动画画风，BURN THE WITCH 动画画风，久保带人动画作品风格，动画截图，线条流畅细腻圆润，大师级构图',
        'suffix': '死神风格'
    },
    '2D 藤本树': {
        'prefix': '角色设定图',
        'quality': '藤本树动画风格，日式动画质感，2d 动画，2D，大师级构图，叙事感',
        'suffix': '藤本风格'
    },
    '2D 像素': {
        'prefix': '角色设定图',
        'quality': '像素艺术风格，低分辨率马赛克，低分辨率纹理，8-bit',
        'suffix': '像素风格'
    },
    '2D 橡皮管动画': {
        'prefix': '角色设定图',
        'quality': '1930 年代复古橡皮管动画风格，复古平面，线条感，复古动画，抽象丰富',
        'suffix': '复古风格'
    },
    
    # ========== 3D 风格 (11 种) ==========
    '3D Q 版': {
        'prefix': '角色设定图',
        'quality': '3D 卡通，3D 风格，Q 版，精致，大师级构图，高清，杰作',
        'suffix': '3D 品质'
    },
    '3D 方块世界': {
        'prefix': '场景设定图',
        'quality': '参考我的世界大电影画面风格，我的世界游戏风格，3D 渲染，3D 方块，立体感，极致细节',
        'suffix': '游戏品质'
    },
    '3D 块面': {
        'prefix': '角色设定图',
        'quality': '凹凸世界作品风格，动画截图，3D 渲染，3D 动画，立体感，块面感，虚幻引擎渲染',
        'suffix': '3D 动画品质'
    },
    '3D 美式': {
        'prefix': '角色设定图',
        'quality': '参考梦工厂作品，参考皮克斯作品，皮克斯风格，3d 动画风格，3d 渲染，高清，大师级构图',
        'suffix': '皮克斯品质'
    },
    '3D 手游': {
        'prefix': '角色设定图',
        'quality': 'Genshin Impact 风格，Honkai: Star Rail 风格，3d，3d 渲染，二次元，虚幻引擎，弱化线条，极致细节',
        'suffix': '游戏品质'
    },
    '3D 写实': {
        'prefix': '场景设定图',
        'quality': '参考美国末日游戏风格，参考使命召唤游戏风格，参考巫师 3 游戏风格，参考荒野大镖客 2 游戏风格，写实 3D 风格，超写实，3D，3D 建模，虚幻引擎渲染，极致光影，极致细节',
        'suffix': '3A 游戏品质'
    },
    '3D 玄幻': {
        'prefix': '角色设定图',
        'quality': '武动乾坤动画画风，三体动画画风，凡人修仙传动画画风，3D，3D 建模，动画截图，无线条',
        'suffix': '玄幻动画品质'
    },
    '3D 渲染 2D': {
        'prefix': '角色设定图',
        'quality': '双城之战动画风格，3D，3D 建模，CG，3D 渲染 2D 风格，大师级构图，高清细节，极致细节',
        'suffix': '双城之战品质'
    },
    '日式 3D 渲染 2D': {
        'prefix': '角色设定图',
        'quality': "BanG Dream! It's MyGO!!!!!动画画风，3d 渲染 2d，3D，动画截图，大师级构图",
        'suffix': '日式 3D 品质'
    },
    
    # ========== 定格动画 (6 种) ==========
    '定格动画': {
        'prefix': '角色设定图',
        'quality': '鬼妈妈定格动画风格，定格动画，诡异，氛围感，故事感',
        'suffix': '定格动画品质'
    },
    '积木定格动画': {
        'prefix': '场景设定图',
        'quality': '粘土风格，定格动画，真实光影，大师级构图',
        'suffix': '粘土动画品质'
    },
    '毛绒定格动画': {
        'prefix': '角色设定图',
        'quality': '毛绒玩具风格，定格动画，真实光影，极致细节，氛围感，故事感，大师级构图',
        'suffix': '毛绒玩具品质'
    },
    '手办定格动画': {
        'prefix': '角色设定图',
        'quality': '手办风格，二次元手办风格，定格动画，真实光影，故事感，氛围感，大师级构图，极致细节',
        'suffix': '手办品质'
    },
    '粘土定格动画': {
        'prefix': '角色设定图',
        'quality': '粘土风格，定格动画，真实光影，大师级构图',
        'suffix': '粘土品质'
    },
    
    # ========== 真人风格 (5 种) ==========
    '真人电影': {
        'prefix': '角色设定图',
        'quality': '参考院线电影，真人电影风格，影视大片，真实透视比例，真实皮肤质感，细节清晰不过度锐化',
        'suffix': '电影品质'
    },
    '真人复古港片': {
        'prefix': '角色设定图',
        'quality': '90 年代香港电视剧风格，80 年代香港电影风格，氛围感，故事感',
        'suffix': '港片风格'
    },
    '真人复古武侠': {
        'prefix': '角色设定图',
        'quality': '参考港式武侠电视剧风格，邵氏电影风格，电影感',
        'suffix': '武侠风格'
    },
    '真人古装': {
        'prefix': '角色设定图',
        'quality': '电视剧风格，参考甄嬛传电视剧风格，参考狂飙电视剧风格，大宅门电视剧风格，庆余年电视剧风格，非精心打光，极致细节，实拍感',
        'suffix': '古装剧品质'
    },
    '真实光晕': {
        'prefix': '场景设定图',
        'quality': '参考院线电影，真人电影风格，影视大片，大师级构图，高级感，氛围感，极致细节，强烈视觉叙事，空气感颗粒，HDR 光影美学',
        'suffix': '电影级光晕效果'
    },
    
    # ========== 默认 ==========
    '默认': {
        'prefix': '角色设定图，高质量',
        'quality': '细节丰富，专业设计',
        'suffix': '工作室品质'
    }
}

# 轮询间隔
POLL_INTERVAL = 60  # 秒（监听表格状态变化）

# 自动生图配置
AUTO_GENERATE_ENABLED = True  # 启用自动生图
AUTO_GENERATE_STATUS = "待生成图片"  # 触发生成的状态值

# ==================== 日志函数 ====================

def log(message, level="INFO"):
    """日志输出"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")
    sys.stdout.flush()

# ==================== 消息处理函数 ====================

def should_process_message(event):
    """
    判断是否应该处理该消息
    """
    # 只处理专属群
    if TARGET_CHAT_ID and event.get('chat_id') != TARGET_CHAT_ID:
        return False
    
    # 获取消息内容
    message = event.get('message', {})
    content = message.get('content', '')
    
    # 检测关键词
    keywords = ['生成图片', '生成角色', '生成场景', '/generate', '@译文']
    
    # 检测是否@BOT
    mentions = message.get('mentions', [])
    is_mentioned = any(m.get('name') == '译文' for m in mentions)
    
    # 满足任一条件即处理
    return is_mentioned or any(kw in content for kw in keywords)


def parse_generation_command(message_text):
    """
    解析生成指令
    
    Returns:
        dict: {
            'record_id': str,
            'style': str,
            'type': 'character' | 'scene' | 'both',
            'custom_prompt': str
        }
    """
    # 提取记录 ID
    record_match = re.search(r'记录 ID[:\s]*([a-zA-Z0-9]+)', message_text)
    record_id = record_match.group(1) if record_match else None
    
    # 提取风格
    style_match = re.search(r'风格[:\s]*(\S+)', message_text)
    style = style_match.group(1) if style_match else '默认'
    
    # 判断类型
    if '角色' in message_text:
        gen_type = 'character'
    elif '场景' in message_text:
        gen_type = 'scene'
    else:
        gen_type = 'both'
    
    return {
        'record_id': record_id,
        'style': style,
        'type': gen_type,
        'custom_prompt': None
    }


def build_prompt_with_template(base_desc, style_name='默认', gen_type='character'):
    """
    使用模板构建提示词（周瑜配置 - 最终版）
    
    提示词结构：{固定前缀} + {描述} + {质量词}
    已移除：类型标识（角色设定图/场景设定图）和后缀
    
    Args:
        base_desc: 基础描述（角色/场景）
        style_name: 风格名称
        gen_type: 生成类型 ('character' 或 'scene')
    
    Returns:
        str: 完整的提示词
    """
    template = PROMPT_TEMPLATES.get(style_name, PROMPT_TEMPLATES['日式 3D 渲染 2D'])
    
    parts = []
    
    # 1. 添加固定前缀（根据生成类型）- 英文提示词更有效
    if gen_type == 'character':
        parts.append(CHARACTER_PREFIX)
    elif gen_type == 'scene':
        parts.append(SCENE_PREFIX)
    
    # 2. 添加描述（修改后角色/场景描述，严格按字段隔离）
    parts.append(base_desc)
    
    # 3. 添加质量词（风格模板中的 quality 字段）
    parts.append(template['quality'])
    
    # 注意：已移除 prefix 和 suffix，避免冗余
    
    return ", ".join(parts)

# ==================== 飞书 API 函数 ====================

_feishu_token_cache = {"token": None, "expire_at": 0}


def get_feishu_tenant_access_token():
    """获取飞书 Token（带缓存）"""
    global _feishu_token_cache
    
    if _feishu_token_cache["token"] and time.time() < _feishu_token_cache["expire_at"]:
        return _feishu_token_cache["token"]
    
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {
        "app_id": FEISHU_APP_ID,
        "app_secret": FEISHU_APP_SECRET
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        result = response.json()
        
        if result.get('code') == 0:
            token = result.get('tenant_access_token')
            _feishu_token_cache["token"] = token
            _feishu_token_cache["expire_at"] = time.time() + 6600
            return token
        return None
    except:
        return None


def send_chat_message(chat_id, text):
    """发送群消息"""
    token = get_feishu_tenant_access_token()
    if not token:
        return False
    
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "receive_id": chat_id,
        "msg_type": "text",
        "content": json.dumps({"text": text})
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        return response.status_code == 200
    except:
        return False


def fetch_pending_records(record_id=None):
    """获取待生成记录"""
    token = get_feishu_tenant_access_token()
    if not token:
        return []
    
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_APP_TOKEN}/tables/{BITABLE_TABLE_ID}/records"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        if record_id:
            # 获取指定记录
            url += f"/{record_id}"
            response = requests.get(url, headers=headers, timeout=30)
            result = response.json()
            if result.get('code') == 0:
                return [result.get('data', {})]
        else:
            # 获取所有记录（不使用筛选，避免 API 兼容性问题）
            response = requests.get(url, headers=headers, timeout=30)
            result = response.json()
            if result.get('code') == 0:
                all_records = result.get('data', {}).get('items', [])
                # 手动筛选状态为"待生成图片"的记录
                pending_records = [r for r in all_records if r.get('fields', {}).get('状态') == '待生成图片']
                log(f"📊 找到 {len(pending_records)}/{len(all_records)} 条待生成记录")
                return pending_records
        
        return []
    except Exception as e:
        log(f"❌ 获取记录失败：{e}", "ERROR")
        return []


def update_record_status(record_id, status, image_url=None):
    """更新记录状态"""
    token = get_feishu_tenant_access_token()
    if not token:
        log(f"❌ 获取 Token 失败，无法更新状态", "ERROR")
        return False
    
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_APP_TOKEN}/tables/{BITABLE_TABLE_ID}/records/{record_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 状态映射（飞书表格中的状态选项）
    status_map = {
        '生成中': '待评审',  # 飞书表格没有"生成中"，用"待评审"代替
        '已完成': '待评审',  # 飞书表格没有"已完成"，用"待评审"代替
        '失败': '待评审'
    }
    
    # 更新状态字段
    feishu_status = status_map.get(status, '待评审')
    fields = {'状态': feishu_status}
    
    if image_url:
        fields['角色设定图'] = image_url
    
    # 使用"完成时间"字段记录完成时间
    if status == '已完成':
        fields['完成时间'] = datetime.now().strftime('%Y/%m/%d')
    
    payload = {'fields': fields}
    
    log(f"📝 更新记录 {record_id} 状态为：{feishu_status}")
    
    try:
        response = requests.put(url, headers=headers, json=payload, timeout=30)
        result = response.json()
        
        if response.status_code == 200:
            log(f"✅ 记录状态更新成功")
            return True
        else:
            log(f"❌ 记录状态更新失败：{result}", "ERROR")
            return False
    except Exception as e:
        log(f"❌ 更新状态异常：{e}", "ERROR")
        return False

# ==================== GRS AI API 函数 ====================

def call_nano_banana_api(prompt, aspect_ratio="3:4", image_size="1K"):
    """调用 Nano Banana API"""
    url = f"{GRS_API_HOST}/v1/draw/nano-banana"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GRS_API_KEY}"
    }
    
    payload = {
        "model": "nano-banana-2",
        "prompt": prompt,
        "aspectRatio": aspect_ratio,
        "imageSize": image_size,
        "webHook": "-1"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        result = response.json()
        
        if result.get('code') == 0 and 'data' in result:
            task_id = result['data'].get('id')
            return poll_task_result(task_id, headers)
        return None
    except:
        return None


def poll_task_result(task_id, headers, max_retries=60):
    """轮询任务结果"""
    url = f"{GRS_API_HOST}/v1/draw/result"
    payload = {"id": task_id}
    
    for i in range(max_retries):
        time.sleep(5)
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            result = response.json()
            
            if result.get('code') != 0:
                continue
            
            data = result.get('data', {})
            status = data.get('status', 'running')
            progress = data.get('progress', 0)
            
            if status == 'succeeded':
                results = data.get('results', [])
                if results and 'url' in results[0]:
                    return results[0]['url']
            elif status == 'failed':
                return None
                
        except:
            continue
    
    return None

# ==================== 自动生图流程 ====================

def auto_check_pending_records():
    """
    自动检查待生成的记录（轮询表格状态）
    """
    if not AUTO_GENERATE_ENABLED:
        return
    
    log("🔄 开始自动检测待生成记录...")
    
    # 获取所有状态为"待生成图片"的记录
    records = fetch_pending_records()
    
    if not records:
        log("💤 未找到待生成记录")
        return
    
    log(f"📊 找到 {len(records)} 条待生成记录")
    
    # 处理每条待生成记录
    for record in records:
        record_key = record.get('record_id')
        fields = record.get('fields', {})
        
        # 检查是否已经在生成中或已完成（避免重复处理）
        current_status = fields.get('状态', '')
        completion_time = fields.get('完成时间', '')
        
        # 如果已有完成时间，说明已生成过，跳过
        if completion_time:
            log(f"⏭️ 记录 {record_key} 已有完成时间 ({completion_time})，跳过")
            continue
        
        # 如果状态不是"待生成图片"，跳过
        if current_status != '待生成图片':
            log(f"⏭️ 记录 {record_key} 状态为 {current_status}，跳过")
            continue
        
        # 获取描述（严格字段隔离）
        char_desc, char_source = get_character_desc(fields)
        scene_desc, scene_source = get_scene_desc(fields)
        
        # 日志记录使用的字段来源
        log(f"📋 角色描述来源：{char_source} ({len(char_desc)}字)")
        log(f"📋 场景描述来源：{scene_source} ({len(scene_desc)}字)")
        
        # 从剧本中提取多个角色
        script = fields.get('完整剧本', '')
        characters = []  # 存储多个角色 [(角色名，描述), ...]
        
        if script:
            # 提取角色名（格式：【角色名】）
            import re
            role_matches = re.findall(r'【([^】]+)】', script)
            if role_matches:
                # 去重
                unique_roles = list(dict.fromkeys(role_matches))
                for role_name in unique_roles:
                    # 根据角色名从主要角色字段获取详细描述
                    main_chars = fields.get('主要角色', '')
                    if role_name in main_chars:
                        # 提取该角色的描述
                        char_detail = f"{role_name}，{main_chars}"
                        characters.append((role_name, char_detail))
                    else:
                        # 如果没有详细描述，使用角色名
                        characters.append((role_name, role_name))
        
        if not char_desc and not scene_desc and not characters:
            log(f"⚠️ 记录 {record_key} 缺少描述，跳过", "WARN")
            continue
        
        # 获取风格（默认：日式 3D 渲染 2D）
        style = fields.get('生成参数 - 风格', '日式 3D 渲染 2D')
        if not style or style == '默认':
            style = '日式 3D 渲染 2D'
        
        # 确定生成类型
        if char_desc or characters:
            if scene_desc:
                gen_type = 'both'
            else:
                gen_type = 'character'
        else:
            gen_type = 'scene'
        
        # 在群内通知
        chat_id = TARGET_CHAT_ID
        record_name = fields.get('文本', '未命名记录')
        
        start_msg = f"🔄 自动检测到待生成任务\n📊 记录：{record_name}\n🎨 风格：{style}\n📝 类型：{'角色 + 场景' if gen_type == 'both' else '角色' if gen_type == 'character' else '场景'}\n⏱️ 预计耗时：3-5 分钟\n\n开始处理..."
        send_chat_message(chat_id, start_msg)
        
        # 更新状态
        update_record_status(record_key, '生成中')
        
        # 生成图片（批量生成，每个角色/场景生成 2 张）
        generated_urls = []
        total_to_generate = 0
        generated_count = 0
        
        # 计算需要生成的总数
        if characters:
            total_to_generate += len(characters) * GENERATE_BATCH
        elif char_desc:
            total_to_generate += GENERATE_BATCH
        if scene_desc:
            total_to_generate += GENERATE_BATCH
        
        log(f"📊 计划生成 {total_to_generate} 张图片...")
        
        # 生成多个角色（从剧本提取）
        if characters and gen_type in ['character', 'both']:
            for role_idx, (role_name, role_desc) in enumerate(characters, 1):
                log(f"📸 生成角色 {role_idx}: {role_name}")
                for i in range(GENERATE_BATCH):
                    prompt = build_prompt_with_template(role_desc, style, 'character')
                    log(f"  {i+1}/{GENERATE_BATCH}: {prompt[:60]}...")
                    
                    image_url = call_nano_banana_api(prompt, aspect_ratio="16:9")
                    if image_url:
                        generated_urls.append((f'角色{role_idx}: {role_name}', image_url, i+1))
                        generated_count += 1
                        log(f"✅ 角色{role_idx} ({i+1}/{GENERATE_BATCH}): {image_url}")
                        log(f"📊 进度：{generated_count}/{total_to_generate}")
                    else:
                        log(f"❌ 角色{role_idx} ({i+1}/{GENERATE_BATCH}) 失败")
        
        # 生成单个角色描述（如果没有从剧本提取角色）
        elif char_desc and gen_type in ['character', 'both']:
            log(f"📸 生成角色")
            for i in range(GENERATE_BATCH):
                prompt = build_prompt_with_template(char_desc, style, 'character')
                log(f"  {i+1}/{GENERATE_BATCH}: {prompt[:60]}...")
                
                image_url = call_nano_banana_api(prompt, aspect_ratio="16:9")
                if image_url:
                    generated_urls.append(('角色设定图', image_url, i+1))
                    generated_count += 1
                    log(f"✅ 角色 ({i+1}/{GENERATE_BATCH}) 完成 ({generated_count}/{total_to_generate})")
                else:
                    log(f"❌ 角色 ({i+1}/{GENERATE_BATCH}) 失败")
        
        # 生成场景图
        if scene_desc and gen_type in ['scene', 'both']:
            log(f"🏞️ 生成场景")
            for i in range(GENERATE_BATCH):
                prompt = build_prompt_with_template(scene_desc, style, 'scene')
                log(f"  {i+1}/{GENERATE_BATCH}: {prompt[:60]}...")
                
                image_url = call_nano_banana_api(prompt, aspect_ratio="16:9")
                if image_url:
                    generated_urls.append(('场景设定图', image_url, i+1))
                    generated_count += 1
                    log(f"✅ 场景 ({i+1}/{GENERATE_BATCH}): {image_url}")
                    log(f"📊 进度：{generated_count}/{total_to_generate}")
                else:
                    log(f"❌ 场景 ({i+1}/{GENERATE_BATCH}) 失败")
        
        log(f"📊 生成完成：{generated_count}/{total_to_generate}")
        
        # 发送完成通知
        if generated_urls:
            completion_msg = "✅ 生成完成！\n\n"
            
            # 按角色/场景分组显示
            current_type = None
            for img_data in generated_urls:
                img_type = img_data[0]
                img_url = img_data[1]
                img_batch = img_data[2] if len(img_data) > 2 else 1
                
                if img_type != current_type:
                    completion_msg += f"\n📎 {img_type} (共{GENERATE_BATCH}张):\n"
                    current_type = img_type
                
                # 明确标记批次序号
                completion_msg += f"  【第{img_batch}张/共{GENERATE_BATCH}张】{img_url}\n"
            
            completion_msg += "\n⚠️ 图片 URL 有效期 2 小时，请及时保存"
            
            # 发送群通知
            send_success = send_chat_message(chat_id, completion_msg)
            if send_success:
                log(f"✅ 群通知发送成功")
            else:
                log(f"❌ 群通知发送失败", "ERROR")
            
            # 保存第一张图片 URL 到表格
            update_record_status(record_key, '已完成', generated_urls[0][1])
            
            # 记录所有 URL 到日志
            log(f"📋 所有生成的图片 URL:")
            for img_type, img_url, img_batch in generated_urls:
                log(f"  {img_type} [{img_batch}/{GENERATE_BATCH}]: {img_url}")
        else:
            send_chat_message(chat_id, "❌ 生成失败\n请稍后重试")
            update_record_status(record_key, '失败')
        
        log(f"✅ 记录 {record_key} 自动处理完成")

# ==================== 主处理流程 ====================

def process_generation_request(event, command_params):
    """处理生成请求"""
    chat_id = event.get('chat_id')
    
    # 获取记录
    record_id = command_params.get('record_id')
    records = fetch_pending_records(record_id)
    
    if not records:
        send_chat_message(chat_id, "❌ 未找到待生成的记录\n请检查记录 ID 或表格状态")
        return
    
    record = records[0]
    record_key = record.get('record_id')
    fields = record.get('fields', {})
    
    # 获取描述（严格字段隔离）
    char_desc, char_source = get_character_desc(fields)
    scene_desc, scene_source = get_scene_desc(fields)
    
    # 日志记录使用的字段来源
    log(f"📋 角色描述来源：{char_source} ({len(char_desc)}字)")
    log(f"📋 场景描述来源：{scene_source} ({len(scene_desc)}字)")
    
    if not char_desc and not scene_desc:
        send_chat_message(chat_id, "❌ 记录缺少角色或场景描述\n请先填写表格")
        return
    
    # 发送开始通知
    # 默认风格：日式 3D 渲染 2D（周瑜配置）
    style = command_params.get('style', '日式 3D 渲染 2D')
    record_name = fields.get('文本', '未命名记录')
    
    start_msg = f"✅ 已接收任务\n📊 记录：{record_name}\n🎨 风格：{style}\n⏱️ 预计耗时：3-5 分钟\n\n开始处理..."
    send_chat_message(chat_id, start_msg)
    
    # 更新状态
    update_record_status(record_key, '生成中')
    
    # 生成图片（批量生成，每个角色/场景生成 2 张）
    generated_urls = []
    
    if char_desc and command_params.get('type') in ['character', 'both']:
        # 批量生成角色图（2 张）- 使用角色名作为标识
        for i in range(GENERATE_BATCH):
            prompt = build_prompt_with_template(char_desc, style, 'character')
            log(f"生成角色图 {i+1}/{GENERATE_BATCH}: {prompt[:50]}...")
            
            image_url = call_nano_banana_api(prompt, aspect_ratio="16:9")
            if image_url:
                # 使用更具体的角色标识
                role_label = f"角色 1: 车主" if '车主' in char_desc else f"角色：{char_desc[:10]}"
                generated_urls.append((role_label, image_url, i+1))
    
    if scene_desc and command_params.get('type') in ['scene', 'both']:
        # 批量生成场景图（2 张）
        for i in range(GENERATE_BATCH):
            prompt = build_prompt_with_template(scene_desc, style, 'scene')
            log(f"生成场景图 {i+1}/{GENERATE_BATCH}: {prompt[:50]}...")
            
            image_url = call_nano_banana_api(prompt, aspect_ratio="16:9")
            if image_url:
                generated_urls.append(('场景：城市街头', image_url, i+1))
    
    # 发送完成通知
    if generated_urls:
        completion_msg = "✅ 生成完成！\n\n"
        
        # 按类型分组显示
        current_type = None
        for img_data in generated_urls:
            img_type = img_data[0]
            img_url = img_data[1]
            img_batch = img_data[2] if len(img_data) > 2 else 1
            
            if img_type != current_type:
                completion_msg += f"\n📎 {img_type} (共{GENERATE_BATCH}张):\n"
                current_type = img_type
            
            # 明确标记批次序号
            completion_msg += f"  【第{img_batch}张/共{GENERATE_BATCH}张】{img_url}\n"
        
        completion_msg += "\n⚠️ 图片 URL 有效期 2 小时，请及时保存"
        
        send_chat_message(chat_id, completion_msg)
        update_record_status(record_key, '已完成', generated_urls[0][1])
    else:
        send_chat_message(chat_id, "❌ 生成失败\n请稍后重试")
        update_record_status(record_key, '失败')


def handle_message(event):
    """处理消息"""
    if not should_process_message(event):
        return
    
    log(f"处理消息：{event.get('message', {}).get('content', '')[:50]}...")
    
    # 解析指令
    content = event.get('message', {}).get('content', '')
    command_params = parse_generation_command(content)
    
    # 处理生成请求
    process_generation_request(event, command_params)

# ==================== 主循环 ====================

def main():
    """主循环"""
    log("🚀 AI 图片生成工作室 AGENT 已启动")
    log(f"📍 专属群：{TARGET_CHAT_NAME}")
    log(f"🎨 使用模型：nano-banana-2")
    log(f"🔄 自动生图：{'✅ 已启用' if AUTO_GENERATE_ENABLED else '❌ 已禁用'}")
    log(f"⏱️ 轮询间隔：{POLL_INTERVAL}秒")
    
    if not TARGET_CHAT_ID:
        log("⚠️ 警告：TARGET_CHAT_ID 未设置，将处理所有群消息", "WARN")
    
    while True:
        try:
            # 自动检查待生成记录
            if AUTO_GENERATE_ENABLED:
                auto_check_pending_records()
            
            # 等待下一次轮询
            time.sleep(POLL_INTERVAL)
            
        except KeyboardInterrupt:
            log("👋 服务已停止")
            break
        except Exception as e:
            log(f"❌ 错误：{e}", "ERROR")
            time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
