#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
飞书视频处理 Webhook
接收飞书事件，调用 Coze 工作流，返回结果
"""

import json
import sys
import os

# 添加工作区路径
sys.path.insert(0, '/root/.openclaw/workspace')

from agents.message_handler import process_message

def handle_feishu_event(event_data):
    """处理飞书事件"""
    print("收到飞书事件")
    print(json.dumps(event_data, ensure_ascii=False, indent=2))
    
    # 调用消息处理器
    result = process_message(event_data)
    
    if result:
        print(f"处理结果：{json.dumps(result, ensure_ascii=False, indent=2)}")
        return result
    
    return {"text": "⚠️ 处理失败"}

if __name__ == "__main__":
    # 测试模式
    if len(sys.argv) > 1:
        # 从文件读取测试数据
        with open(sys.argv[1], 'r') as f:
            event_data = json.load(f)
        result = handle_feishu_event(event_data)
        print(f"\n最终结果：{json.dumps(result, ensure_ascii=False, indent=2)}")
    else:
        print("用法：python3 webhooks/feishu_coze.py <event.json>")
        print("\nWebhook 已就绪！")
        print("回调 URL: https://47.102.199.115:15427/feishu/coze-webhook")
