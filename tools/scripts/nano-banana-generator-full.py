#!/usr/bin/env python3
"""
Nano Banana 2 图片生成工具 - 完整版
集成飞书多维表格 + GRS AI API

功能：
1. 轮询飞书表格，检测"待生成图片"的记录
2. 读取角色/场景描述
3. 调用 Nano Banana API 生成图片
4. 下载图片并上传到飞书云文档
5. 回写图片链接到表格
6. 更新状态为"图片已完成"
"""

import os
import sys
import time
import json
import requests
from datetime import datetime
from pathlib import Path

# ==================== 配置区域 ====================

# GRS AI API 配置
GRS_API_HOST = "https://grsai.dakka.com.cn"
GRS_API_KEY = os.environ.get("GRS_API_KEY", "sk-10eee66de80245e78277514e88a67401")

# Nano Banana 模型配置
NANO_BANANA_MODEL = "nano-banana-2"
DEFAULT_ASPECT_RATIO = "16:9"
DEFAULT_IMAGE_SIZE = "1K"

# 飞书配置
BITABLE_APP_TOKEN = "GHrubiTjnayG4fsWP2IcJIotnfc"
BITABLE_TABLE_ID = "tbl8ik4qLltAlXvp"
FEISHU_APP_ID = os.environ.get("FEISHU_APP_ID", "cli_a92e8b3399b85cd6")
FEISHU_APP_SECRET = os.environ.get("FEISHU_APP_SECRET", "tMiX2hL0wTf7ujPSK2pqnf3d3aeg8AGa")

# 轮询间隔（秒）
POLL_INTERVAL = 60

# 飞书 API 基础 URL
FEISHU_API_BASE = "https://open.feishu.cn/open-apis"

# ==================== 日志函数 ====================

def log(message, level="INFO"):
    """日志输出"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")
    sys.stdout.flush()

# ==================== GRS AI API 函数 ====================

def call_nano_banana_api(prompt, aspect_ratio="16:9", image_size="1K"):
    """
    调用 Nano Banana API 生成图片
    """
    if not GRS_API_KEY:
        log("❌ 未设置 GRS_API_KEY", "ERROR")
        return None
    
    url = f"{GRS_API_HOST}/v1/draw/nano-banana"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GRS_API_KEY}"
    }
    
    payload = {
        "model": NANO_BANANA_MODEL,
        "prompt": prompt,
        "aspectRatio": aspect_ratio,
        "imageSize": image_size,
        "webHook": "-1"
    }
    
    log(f"🎨 正在生成图片：{prompt[:50]}...")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        if 'data' not in result or 'id' not in result['data']:
            log(f"❌ API 返回错误：{result}", "ERROR")
            return None
        
        task_id = result['data']['id']
        log(f"✅ 任务已提交：{task_id}")
        
        return poll_task_result(task_id, headers)
        
    except Exception as e:
        log(f"❌ API 调用失败：{e}", "ERROR")
        return None


def poll_task_result(task_id, headers, max_retries=30, retry_interval=5):
    """
    轮询任务结果
    """
    url = f"{GRS_API_HOST}/v1/draw/result"
    payload = {"id": task_id}
    
    for i in range(max_retries):
        try:
            time.sleep(retry_interval)
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('code') != 0:
                log(f"❌ 查询失败：{result}", "ERROR")
                return None
            
            data = result.get('data', {})
            status = data.get('status', 'running')
            progress = data.get('progress', 0)
            
            log(f"⏳ 进度：{progress}% - 状态：{status}")
            
            if status == 'succeeded':
                results = data.get('results', [])
                if results and 'url' in results[0]:
                    image_url = results[0]['url']
                    log(f"✅ 图片生成成功：{image_url}")
                    return {
                        'task_id': task_id,
                        'image_url': image_url,
                        'content': results[0].get('content', '')
                    }
                else:
                    log("❌ 结果中没有图片 URL", "ERROR")
                    return None
            
            elif status == 'failed':
                error_reason = data.get('failure_reason', 'unknown')
                error_detail = data.get('error', '')
                log(f"❌ 生成失败：{error_reason} - {error_detail}", "ERROR")
                return None
            
        except Exception as e:
            log(f"❌ 轮询失败：{e}", "ERROR")
        
        if i < max_retries - 1:
            log(f"⏳ 等待 {retry_interval} 秒后重试...")
    
    log(f"❌ 轮询超时（{max_retries} 次）", "ERROR")
    return None


def download_image(image_url, save_path):
    """
    下载图片到本地
    """
    try:
        log(f"📥 正在下载图片：{image_url}")
        
        response = requests.get(image_url, timeout=60)
        response.raise_for_status()
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        with open(save_path, 'wb') as f:
            f.write(response.content)
        
        log(f"✅ 图片已保存：{save_path}")
        return save_path
        
    except Exception as e:
        log(f"❌ 下载失败：{e}", "ERROR")
        return None

# ==================== 飞书 API 函数 ====================

# 飞书 Token 缓存
_feishu_token_cache = {"token": None, "expire_at": 0}


def get_feishu_tenant_access_token():
    """
    获取飞书 Tenant Access Token（带缓存）
    """
    global _feishu_token_cache
    
    # 检查缓存
    if _feishu_token_cache["token"] and time.time() < _feishu_token_cache["expire_at"]:
        return _feishu_token_cache["token"]
    
    if not FEISHU_APP_ID or not FEISHU_APP_SECRET:
        log("⚠️ 未配置 FEISHU_APP_ID 或 FEISHU_APP_SECRET", "WARN")
        return None
    
    url = f"{FEISHU_API_BASE}/auth/v3/tenant_access_token/internal"
    
    payload = {
        "app_id": FEISHU_APP_ID,
        "app_secret": FEISHU_APP_SECRET
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        if result.get('code') == 0:
            token = result.get('tenant_access_token')
            # Token 有效期 2 小时，提前 10 分钟刷新
            _feishu_token_cache["token"] = token
            _feishu_token_cache["expire_at"] = time.time() + 6600
            log("✅ 获取飞书 Token 成功")
            return token
        else:
            log(f"❌ 获取 Token 失败：{result}", "ERROR")
            return None
            
    except Exception as e:
        log(f"❌ 请求失败：{e}", "ERROR")
        return None


def fetch_pending_records():
    """
    获取待生成图片的记录（状态 = "待生成图片"）
    """
    token = get_feishu_tenant_access_token()
    if not token:
        return []
    
    url = f"{FEISHU_API_BASE}/bitable/v1/apps/{BITABLE_APP_TOKEN}/tables/{BITABLE_TABLE_ID}/records"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 筛选条件：状态 = "待生成图片"
    params = {
        "filter": {
            "conjunction": "and",
            "conditions": [
                {
                    "field_name": "状态",
                    "operator": "equals",
                    "value": "待生成图片"
                }
            ]
        }
    }
    
    try:
        log("📋 正在获取待处理记录...")
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        if result.get('code') == 0:
            records = result.get('data', {}).get('items', [])
            log(f"✅ 找到 {len(records)} 条待处理记录")
            return records
        else:
            log(f"❌ 获取记录失败：{result}", "ERROR")
            return []
            
    except Exception as e:
        log(f"❌ 请求失败：{e}", "ERROR")
        return []


def upload_to_feishu(file_path, file_name=""):
    """
    上传图片到飞书云文档
    """
    token = get_feishu_tenant_access_token()
    if not token:
        log("⚠️ 无法获取 Token，返回本地路径", "WARN")
        return file_path
    
    if not file_name:
        file_name = os.path.basename(file_path)
    
    url = f"{FEISHU_API_BASE}/drive/v1/medias/upload"
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # 飞书文件上传需要分步：先上传到临时存储，再创建文件
    # 简化版本：直接上传
    try:
        log(f"📤 正在上传到飞书：{file_name}")
        
        with open(file_path, 'rb') as f:
            files = {'file': (file_name, f)}
            response = requests.post(url, headers=headers, files=files, timeout=60)
        
        response.raise_for_status()
        result = response.json()
        
        if result.get('code') == 0:
            file_token = result.get('data', {}).get('file_token')
            file_url = f"https://szdreamgame.feishu.cn/drive/file/{file_token}"
            log(f"✅ 上传成功：{file_url}")
            return file_url
        else:
            log(f"❌ 上传失败：{result}", "ERROR")
            return file_path
            
    except Exception as e:
        log(f"❌ 上传失败：{e}", "ERROR")
        return file_path


def update_bitable_record(record_id, fields):
    """
    更新飞书表格记录
    """
    token = get_feishu_tenant_access_token()
    if not token:
        log("⚠️ 无法获取 Token，跳过更新", "WARN")
        return False
    
    url = f"{FEISHU_API_BASE}/bitable/v1/apps/{BITABLE_APP_TOKEN}/tables/{BITABLE_TABLE_ID}/records/{record_id}"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "fields": fields
    }
    
    try:
        log(f"✏️ 正在更新记录 {record_id}")
        response = requests.put(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        if result.get('code') == 0:
            log(f"✅ 记录更新成功")
            return True
        else:
            log(f"❌ 更新失败：{result}", "ERROR")
            return False
            
    except Exception as e:
        log(f"❌ 请求失败：{e}", "ERROR")
        return False

# ==================== 主流程 ====================

def build_prompt(base_desc, prefix="", suffix="", quality_words="", custom_quality=""):
    """
    构建最终提示词
    
    Args:
        base_desc: 基础描述（角色/场景）
        prefix: 提示词前缀
        suffix: 提示词后缀
        quality_words: 质量词
        custom_quality: 自定义质量词
    
    Returns:
        str: 最终提示词
    """
    parts = []
    
    # 添加前缀
    if prefix:
        parts.append(prefix)
    
    # 添加基础描述
    if base_desc:
        parts.append(base_desc)
    
    # 添加质量词
    if quality_words:
        parts.append(quality_words)
    
    # 添加自定义质量词
    if custom_quality:
        parts.append(custom_quality)
    
    # 添加后缀
    if suffix:
        parts.append(suffix)
    else:
        # 默认后缀
        parts.append("高质量，细节丰富，专业设计")
    
    return ", ".join(parts)


def process_record(record):
    """
    处理单条记录
    """
    record_id = record.get('id')
    record_key = record.get('record_id')
    fields = record.get('fields', {})
    
    log(f"🔍 处理记录：{record_id}")
    
    # 读取角色和场景描述
    character_desc = fields.get('修改后角色', '')
    scene_desc = fields.get('修改后场景', '')
    
    # 读取提示词参数
    prefix = fields.get('生成参数 - 提示词前缀', '')
    suffix = fields.get('生成参数 - 提示词后缀', '')
    quality_words = fields.get('生成参数 - 自定义质量词', '')
    
    if not character_desc and not scene_desc:
        log(f"⚠️ 记录 {record_id} 没有角色或场景描述", "WARN")
        update_bitable_record(record_key, {
            '图片生成状态': '失败'
        })
        return
    
    generated_images = []
    
    # 生成角色设定图
    if character_desc:
        log(f"🎨 开始生成角色设定图...")
        
        # 构建提示词
        character_prompt = build_prompt(
            base_desc=character_desc,
            prefix=prefix or "角色设定图，真实照片质感",
            suffix=suffix or "工作室品质，商业级人像摄影",
            quality_words=quality_words or "8K 分辨率，超细节，电影级光照，专业摄影",
            custom_quality=""
        )
        
        log(f"📝 提示词：{character_prompt[:100]}...")
        
        character_result = call_nano_banana_api(
            character_prompt,
            aspect_ratio="3:4",  # 角色图用竖版
            image_size="1K"
        )
        
        if character_result:
            # 下载图片
            char_filename = f"/tmp/character_{record_id}_{int(time.time())}.png"
            char_path = download_image(character_result['image_url'], char_filename)
            
            if char_path:
                # 上传到飞书
                feishu_char_url = upload_to_feishu(char_path, f"character_{record_id}.png")
                generated_images.append(feishu_char_url)
                
                log(f"✅ 角色图已生成：{feishu_char_url}")
    
    # 生成场景设定图
    if scene_desc:
        log(f"🏞️ 开始生成场景设定图...")
        
        scene_prompt = f"场景设定图，{scene_desc}，高质量，细节丰富，专业场景设计"
        scene_result = call_nano_banana_api(
            scene_prompt,
            aspect_ratio="16:9",  # 场景图用横版
            image_size="1K"
        )
        
        if scene_result:
            # 下载图片
            scene_filename = f"/tmp/scene_{record_id}_{int(time.time())}.png"
            scene_path = download_image(scene_result['image_url'], scene_filename)
            
            if scene_path:
                # 上传到飞书
                feishu_scene_url = upload_to_feishu(scene_path, f"scene_{record_id}.png")
                generated_images.append(feishu_scene_url)
                
                log(f"✅ 场景图已生成：{feishu_scene_url}")
    
    # 更新表格
    if generated_images:
        update_fields = {
            '图片生成状态': '已完成',
            '图片生成时间': datetime.now().isoformat()
        }
        
        if len(generated_images) >= 1:
            update_fields['角色设定图'] = generated_images[0]
        if len(generated_images) >= 2:
            update_fields['场景设定图'] = generated_images[1]
        
        update_bitable_record(record_key, update_fields)
        log(f"✅ 记录 {record_id} 处理完成")
    else:
        update_bitable_record(record_key, {
            '图片生成状态': '失败'
        })
        log(f"❌ 记录 {record_id} 生成失败", "ERROR")


def main_loop():
    """主循环"""
    log("🚀 Nano Banana 2 图片生成服务已启动")
    log(f"📊 监控表格：https://szdreamgame.feishu.cn/base/{BITABLE_APP_TOKEN}")
    log(f"🎨 使用模型：{NANO_BANANA_MODEL}")
    log(f"⏱️ 轮询间隔：{POLL_INTERVAL}秒\n")
    
    while True:
        try:
            # 获取待处理记录
            pending_records = fetch_pending_records()
            
            if pending_records:
                log(f"📋 发现 {len(pending_records)} 条待处理记录")
                
                for record in pending_records:
                    process_record(record)
            else:
                log("💤 暂无待处理记录")
            
            # 等待下一次轮询
            time.sleep(POLL_INTERVAL)
            
        except KeyboardInterrupt:
            log("👋 服务已停止")
            break
        except Exception as e:
            log(f"❌ 主循环错误：{e}", "ERROR")
            time.sleep(POLL_INTERVAL)

# ==================== 测试函数 ====================

def test_api():
    """测试 API 调用"""
    log("🧪 开始测试 Nano Banana API...")
    
    test_prompt = "一只可爱的猫咪在草地上玩耍，阳光明媚，高质量"
    
    result = call_nano_banana_api(test_prompt, aspect_ratio="1:1")
    
    if result:
        log(f"✅ 测试成功！图片 URL: {result['image_url']}")
        
        # 下载测试
        test_path = "/tmp/nano_banana_test.png"
        download_image(result['image_url'], test_path)
        log(f"✅ 图片已保存到：{test_path}")
    else:
        log("❌ 测试失败", "ERROR")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_api()
    else:
        main_loop()
