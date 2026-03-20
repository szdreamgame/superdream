#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
译文 AGENT - 飞书事件监听器

通过 HTTP 服务器接收飞书推送的事件，然后调用 yiwen-agent.py 处理
"""

import os
import sys
import json
import time
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

# 配置
LISTEN_PORT = 8080  # 监听端口
FEISHU_APP_ID = "cli_a92e8b3399b85cd6"
FEISHU_APP_SECRET = "tMiX2hL0wTf7ujPSK2pqnf3d3aeg8AGa"
TARGET_CHAT_ID = "oc_95a9882e1aca9546c1930b2d27660a6a"  # 漫剧 - 文案评审群

# 日志
def log(message, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

# 飞书 Token 缓存
feishu_token = None
token_expire_at = 0

def get_feishu_tenant_token():
    """获取飞书 tenant_access_token"""
    global feishu_token, token_expire_at
    
    now = time.time()
    if feishu_token and now < token_expire_at:
        return feishu_token
    
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET}
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        result = response.json()
        
        if result.get("code") == 0:
            feishu_token = result.get("tenant_access_token")
            token_expire_at = now + 7200
            log("✅ 飞书 Token 获取成功")
            return feishu_token
        
        log(f"❌ 获取飞书 Token 失败：{result.get('msg')}", "ERROR")
        return None
        
    except Exception as e:
        log(f"❌ 获取飞书 Token 异常：{e}", "ERROR")
        return None


def get_message_content(message_id):
    """通过 API 获取消息详情"""
    token = get_feishu_tenant_token()
    if not token:
        return None
    
    url = f"https://open.feishu.cn/open-apis/im/v1/messages/{message_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        result = response.json()
        
        if result.get("code") == 0:
            return result.get("data")
        return None
        
    except Exception as e:
        log(f"❌ 获取消息详情异常：{e}", "ERROR")
        return None


class FeishuEventHandler(BaseHTTPRequestHandler):
    """飞书事件处理器"""
    
    def do_POST(self):
        """处理 POST 请求"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            event = json.loads(post_data.decode('utf-8'))
            log(f"📨 收到飞书事件：{event.get('type', 'unknown')}")
            
            # 处理 url_verification 事件（飞书验证）
            if event.get('type') == 'url_verification':
                challenge = event.get('challenge', '')
                log(f"✅ URL 验证：{challenge}")
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(challenge.encode())
                return
            
            # 处理消息事件
            if event.get('type') == 'im.message.receive_v1':
                self.handle_message_event(event)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode())
            
        except Exception as e:
            log(f"❌ 处理事件异常：{e}", "ERROR")
            self.send_response(500)
            self.end_headers()
    
    def handle_message_event(self, event):
        """处理消息事件"""
        message = event.get('message', {})
        chat_id = message.get('chat_id', '')
        message_id = message.get('message_id', '')
        message_type = message.get('message_type', '')
        
        log(f"   群聊 ID: {chat_id}")
        log(f"   消息 ID: {message_id}")
        log(f"   消息类型：{message_type}")
        
        # 检查是否是目标群
        if chat_id != TARGET_CHAT_ID:
            log("   ⏭️ 非目标群，跳过")
            return
        
        # 检查是否是视频消息
        if message_type != 'video':
            log("   ⏭️ 非视频消息，跳过")
            return
        
        # 检查是否@了 Bot
        mentions = message.get('mentions', [])
        is_mentioned = False
        for mention in mentions:
            name = mention.get('name', '')
            if name in ['译文', 'feishubot']:
                is_mentioned = True
                break
        
        if not is_mentioned:
            log("   ⏭️ 未@Bot，跳过")
            return
        
        log("   ✅ 匹配成功，开始处理视频")
        
        # 获取消息详情（包含附件信息）
        message_detail = get_message_content(message_id)
        if not message_detail:
            log("   ❌ 获取消息详情失败")
            return
        
        # 调用译文 AGENT 处理
        self.call_yiwen_agent(message_detail)
    
    def call_yiwen_agent(self, message_detail):
        """调用译文 AGENT 处理视频"""
        log("   🚀 调用译文 AGENT...")
        
        # 这里可以直接导入 yiwen_agent 模块处理
        # 或者通过 subprocess 调用
        # 简化实现：打印日志，实际处理需要集成
        
        log("   ⚠️  需要集成 yiwen_agent 处理逻辑")
        
        # TODO: 集成实际处理逻辑
        # from yiwen_agent import process_video_message
        # process_video_message({'message': message_detail, 'chat_id': message_detail.get('chat_id')})
    
    def log_message(self, format, *args):
        """禁用默认 HTTP 日志"""
        pass


def main():
    """主函数"""
    log("="*60)
    log("🚀 译文 AGENT - 飞书事件监听器")
    log(f"📍 监听端口：{LISTEN_PORT}")
    log(f"🎯 目标群：{TARGET_CHAT_ID}")
    log("="*60)
    
    log("\n📖 配置飞书事件订阅：")
    log("1. 打开飞书开发者后台")
    log("2. 进入应用 → 事件订阅")
    log(f"3. 配置事件 URL: http://<服务器 IP>:{LISTEN_PORT}/")
    log("4. 订阅事件：im.message.receive_v1")
    log("="*60)
    
    try:
        server = HTTPServer(('0.0.0.0', LISTEN_PORT), FeishuEventHandler)
        log(f"\n✅ 服务器已启动，监听 0.0.0.0:{LISTEN_PORT}")
        log("⏳ 等待飞书事件...\n")
        server.serve_forever()
        
    except KeyboardInterrupt:
        log("\n👋 服务已停止")
    except Exception as e:
        log(f"❌ 服务器异常：{e}", "ERROR")


if __name__ == "__main__":
    main()
