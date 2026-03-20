#!/usr/bin/env python3
"""
Nano Banana 2 图片生成工具
基于 GRS AI API 实现角色和场景设定图生成

功能：
1. 监听飞书多维表格状态
2. 当状态为"待生成图片"时，读取角色/场景描述
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
GRS_API_HOST = "https://grsai.dakka.com.cn"  # 国内直连
GRS_API_KEY = os.environ.get("GRS_API_KEY", "sk-10eee66de80245e78277514e88a67401")  # 从环境变量获取 API Key

# Nano Banana 模型配置
NANO_BANANA_MODEL = "nano-banana-2"  # 使用 nano-banana-2 模型
DEFAULT_ASPECT_RATIO = "16:9"  # 默认比例
DEFAULT_IMAGE_SIZE = "1K"  # 默认尺寸

# 飞书表格配置
BITABLE_APP_TOKEN = "GHrubiTjnayG4fsWP2IcJIotnfc"
BITABLE_TABLE_ID = "tbl8ik4qLltAlXvp"
BITABLE_URL = f"https://szdreamgame.feishu.cn/base/{BITABLE_APP_TOKEN}"

# 轮询间隔（秒）
POLL_INTERVAL = 60

# ==================== 工具函数 ====================

def log(message, level="INFO"):
    """日志输出"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")


def call_nano_banana_api(prompt, aspect_ratio=DEFAULT_ASPECT_RATIO, image_size=DEFAULT_IMAGE_SIZE):
    """
    调用 Nano Banana API 生成图片
    
    Args:
        prompt: 提示词
        aspect_ratio: 图片比例
        image_size: 图片尺寸
    
    Returns:
        dict: 包含图片 URL 的响应数据
    """
    if not GRS_API_KEY:
        log("❌ 未设置 GRS_API_KEY 环境变量", "ERROR")
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
        "webHook": "-1"  # 立即返回任务 ID
    }
    
    log(f"🎨 正在生成图片：{prompt[:50]}...")
    
    try:
        # 提交任务
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        if 'id' not in result:
            log(f"❌ API 返回错误：{result}", "ERROR")
            return None
        
        task_id = result['id']
        log(f"✅ 任务已提交：{task_id}")
        
        # 轮询获取结果
        return poll_task_result(task_id, headers)
        
    except Exception as e:
        log(f"❌ API 调用失败：{e}", "ERROR")
        return None


def poll_task_result(task_id, headers, max_retries=30, retry_interval=5):
    """
    轮询任务结果
    
    Args:
        task_id: 任务 ID
        headers: 请求头
        max_retries: 最大重试次数
        retry_interval: 重试间隔（秒）
    
    Returns:
        dict: 包含图片 URL 的结果
    """
    url = f"{GRS_API_HOST}/v1/draw/result"
    
    payload = {"id": task_id}
    
    for i in range(max_retries):
        try:
            time.sleep(retry_interval)
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            status = result.get('status', 'running')
            progress = result.get('progress', 0)
            
            log(f"⏳ 进度：{progress}% - 状态：{status}")
            
            if status == 'succeeded':
                results = result.get('results', [])
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
                error_reason = result.get('failure_reason', 'unknown')
                error_detail = result.get('error', '')
                log(f"❌ 生成失败：{error_reason} - {error_detail}", "ERROR")
                
                # 如果是错误，尝试重试
                if error_reason == 'error' and i < max_retries - 1:
                    log("🔄 尝试重新提交任务...")
                    return None  # 返回 None 让上层重试
                    
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
    
    Args:
        image_url: 图片 URL
        save_path: 保存路径
    
    Returns:
        str: 保存的文件路径
    """
    try:
        log(f"📥 正在下载图片：{image_url}")
        
        response = requests.get(image_url, timeout=60)
        response.raise_for_status()
        
        # 确保目录存在
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        with open(save_path, 'wb') as f:
            f.write(response.content)
        
        log(f"✅ 图片已保存：{save_path}")
        return save_path
        
    except Exception as e:
        log(f"❌ 下载失败：{e}", "ERROR")
        return None


def upload_to_feishu(file_path, folder_token=""):
    """
    上传图片到飞书云文档
    
    Args:
        file_path: 本地文件路径
        folder_token: 文件夹 token（可选）
    
    Returns:
        str: 飞书文件链接
    """
    # 这里需要飞书 API 权限
    # 暂时返回本地路径，实际使用时需要实现飞书上传
    log(f"📤 上传到飞书（待实现）：{file_path}")
    return file_path


def update_bitable_record(record_id, fields):
    """
    更新飞书表格记录
    
    Args:
        record_id: 记录 ID
        fields: 要更新的字段
    """
    # 这里需要飞书 API
    log(f"✏️ 更新表格记录 {record_id}: {fields}")
    # TODO: 实现飞书 API 调用


def fetch_pending_records():
    """
    获取待生成图片的记录
    
    Returns:
        list: 待处理的记录列表
    """
    # 这里需要飞书 API
    log("📋 获取待处理记录（待实现）")
    return []


# ==================== 主流程 ====================

def process_record(record):
    """
    处理单条记录
    
    Args:
        record: 表格记录
    """
    record_id = record.get('id')
    fields = record.get('fields', {})
    
    # 读取角色和场景描述
    character_desc = fields.get('修改后角色', '')
    scene_desc = fields.get('修改后场景', '')
    
    if not character_desc and not scene_desc:
        log(f"⚠️ 记录 {record_id} 没有角色或场景描述", "WARN")
        return
    
    # 生成角色设定图
    if character_desc:
        log(f"🎨 开始生成角色设定图...")
        
        character_prompt = f"角色设定图，{character_desc}，高质量，细节丰富，专业角色设计"
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
                feishu_char_url = upload_to_feishu(char_path)
                
                # 更新表格
                update_bitable_record(record_id, {
                    '角色设定图': feishu_char_url,
                    '图片生成状态': '生成中'
                })
    
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
                feishu_scene_url = upload_to_feishu(scene_path)
                
                # 更新表格
                update_bitable_record(record_id, {
                    '场景设定图': feishu_scene_url,
                    '图片生成状态': '已完成',
                    '图片生成时间': datetime.now().isoformat()
                })
    
    log(f"✅ 记录 {record_id} 处理完成")


def main_loop():
    """主循环"""
    log("🚀 Nano Banana 2 图片生成服务已启动")
    log(f"📊 监控表格：{BITABLE_URL}")
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
    
    result = call_nano_banana_api(test_prompt)
    
    if result:
        log(f"✅ 测试成功！图片 URL: {result['image_url']}")
        
        # 下载测试
        test_path = "/tmp/nano_banana_test.png"
        download_image(result['image_url'], test_path)
    else:
        log("❌ 测试失败", "ERROR")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_api()
    else:
        main_loop()
