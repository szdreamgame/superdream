#!/usr/bin/env python3
"""
提取 GRS AI 文档 HTML 为 Markdown
"""

import re
from bs4 import BeautifulSoup

def extract_api_docs(html_content, doc_name):
    """从 HTML 中提取 API 文档内容"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 提取标题
    title = soup.find('h1')
    title_text = title.get_text().strip() if title else doc_name
    
    # 提取所有 API 接口信息
    api_sections = []
    
    # 查找所有接口卡片
    for card in soup.find_all('div', class_='border border-gray-200 rounded-lg'):
        h3 = card.find('h3')
        if h3:
            api_name = h3.get_text().strip()
            
            # 提取请求方法和路径
            method_tag = card.find('span', class_='px-2 py-0.5')
            path_tag = card.find('code', class_='bg-gray-100')
            
            method = method_tag.get_text().strip() if method_tag else ''
            path = path_tag.get_text().strip() if path_tag else ''
            
            api_sections.append({
                'name': api_name,
                'method': method,
                'path': path
            })
    
    # 提取 Host 信息
    hosts = []
    for input_tag in soup.find_all('input', class_='flex h-10 w-full'):
        value = input_tag.get('value', '')
        if value and value.startswith('http'):
            hosts.append(value)
    
    return {
        'title': title_text,
        'apis': api_sections,
        'hosts': hosts
    }

# 处理 GPT Image 文档
with open('/tmp/gpt-image.html', 'r', encoding='utf-8') as f:
    gpt_data = extract_api_docs(f.read(), 'GPT Image')

# 处理 Other 文档  
with open('/tmp/other.html', 'r', encoding='utf-8') as f:
    other_data = extract_api_docs(f.read(), 'Other')

print("=== GPT Image API ===")
print(f"标题：{gpt_data['title']}")
print(f"Hosts: {gpt_data['hosts']}")
print(f"API 数量：{len(gpt_data['apis'])}")
for api in gpt_data['apis']:
    print(f"  - {api['method']} {api['path']}: {api['name']}")

print("\n=== Other API ===")
print(f"标题：{other_data['title']}")
print(f"Hosts: {other_data['hosts']}")
print(f"API 数量：{len(other_data['apis'])}")
for api in other_data['apis']:
    print(f"  - {api['method']} {api['path']}: {api['name']}")
