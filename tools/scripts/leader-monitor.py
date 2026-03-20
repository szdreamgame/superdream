#!/usr/bin/env python3
"""
LEADER AGENT - 画语 BOT 监控脚本
功能：每 60 秒检查画语 BOT 日志，发现生成完成后主动汇报
"""

import os
import time
import re
from datetime import datetime

# 配置
HUAYU_BOT_LOG = "/tmp/huayu-bot.log"
REPORTED_LINES = 0  # 已汇报的行数
LAST_CHECK_TIME = time.time()

def check_huayu_bot():
    """检查画语 BOT 日志"""
    global REPORTED_LINES
    
    if not os.path.exists(HUAYU_BOT_LOG):
        return None
    
    with open(HUAYU_BOT_LOG, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 查找新的"生成完成"记录
    completion_found = False
    completion_info = {
        'timestamp': None,
        'urls': [],
        'record_id': None
    }
    
    for i, line in enumerate(lines[REPORTED_LINES:], start=REPORTED_LINES):
        # 检测生成完成
        if '📊 生成完成' in line:
            completion_found = True
            # 提取时间戳
            timestamp_match = re.search(r'\[(.*?)\]', line)
            if timestamp_match:
                completion_info['timestamp'] = timestamp_match.group(1)
        
        # 提取 URL
        if '✅ 角色' in line or '✅ 场景' in line:
            url_match = re.search(r'https://file[^\s]+', line)
            if url_match:
                completion_info['urls'].append(url_match.group())
        
        # 提取记录 ID
        if '记录 recljJN0oH 自动处理完成' in line:
            completion_info['record_id'] = 'recljJN0oH'
    
    # 更新已读行数
    REPORTED_LINES = len(lines)
    
    # 如果找到完成记录且有 URL，返回结果
    if completion_found and completion_info['urls']:
        return completion_info
    
    return None

def send_report_to_user(completion_info):
    """发送汇报给潘泽霖"""
    if not completion_info:
        return
    
    # 构建汇报消息
    report_msg = f"""🎨 **画语 BOT 生成完成汇报**

**完成时间**: {completion_info['timestamp']}

**生成结果**:
"""
    
    # 分类 URL
    role1_urls = []
    role2_urls = []
    scene_urls = []
    
    for url in completion_info['urls']:
        if '角色 1' in url or len(role1_urls) < 2:
            role1_urls.append(url)
        elif '角色 2' in url or len(role2_urls) < 2:
            role2_urls.append(url)
        else:
            scene_urls.append(url)
    
    report_msg += f"""
**角色 1: 车主 (共{len(role1_urls)}张)**
"""
    for i, url in enumerate(role1_urls, 1):
        report_msg += f"- 【第{i}张】{url}\n"
    
    report_msg += f"""
**角色 2: 街头摄影师 (共{len(role2_urls)}张)**
"""
    for i, url in enumerate(role2_urls, 1):
        report_msg += f"- 【第{i}张】{url}\n"
    
    report_msg += f"""
**场景：城市街头 (共{len(scene_urls)}张)**
"""
    for i, url in enumerate(scene_urls, 1):
        report_msg += f"- 【第{i}张】{url}\n"
    
    report_msg += "\n⚠️ **图片 URL 有效期 2 小时，请及时保存！**"
    
    # 这里应该调用飞书 API 发送私聊消息
    # 暂时先打印日志
    print(f"\n{'='*60}")
    print("📤 发送汇报给潘泽霖:")
    print(report_msg)
    print(f"{'='*60}\n")
    
    return report_msg

def main():
    """主循环"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚀 LEADER AGENT 监控已启动")
    print(f"📍 监控目标：画语 BOT ({HUAYU_BOT_LOG})")
    print(f"⏱️ 检查间隔：60 秒")
    print()
    
    while True:
        try:
            # 检查画语 BOT
            result = check_huayu_bot()
            
            if result:
                # 发送汇报
                send_report_to_user(result)
            
            # 等待 60 秒
            time.sleep(60)
            
        except KeyboardInterrupt:
            print("\n👋 监控已停止")
            break
        except Exception as e:
            print(f"❌ 错误：{e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
