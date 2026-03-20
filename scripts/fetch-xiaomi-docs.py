#!/usr/bin/env python3
"""
抓取小米 MiMo 文档并转换为 Markdown
"""

import requests
from bs4 import BeautifulSoup
import os
import json
from datetime import datetime

BASE_URL = "https://platform.xiaomimimo.com"
DOCS_URL = "https://platform.xiaomimimo.com/#/docs/welcome"
OUTPUT_DIR = "/root/.openclaw/workspace/knowledge/xiaomi-mimo"

def fetch_page(url):
    """抓取网页内容"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def html_to_markdown(html, title=""):
    """简单的 HTML 转 Markdown"""
    soup = BeautifulSoup(html, 'html.parser')
    
    # 提取主要内容
    content = []
    content.append(f"# {title}\n")
    content.append(f"*抓取时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
    content.append(f"*来源：{DOCS_URL}*\n\n")
    content.append("---\n\n")
    
    # 提取所有文本内容
    for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'li', 'pre', 'code']):
        if tag.name in ['h1', 'h2', 'h3', 'h4']:
            prefix = '#' * int(tag.name[1])
            content.append(f"{prefix} {tag.get_text().strip()}\n\n")
        elif tag.name == 'p':
            text = tag.get_text().strip()
            if text:
                content.append(f"{text}\n\n")
        elif tag.name == 'li':
            content.append(f"- {tag.get_text().strip()}\n")
        elif tag.name in ['pre', 'code']:
            code = tag.get_text().strip()
            if code:
                content.append(f"```{code}```\n\n")
    
    return ''.join(content)

def main():
    print("开始抓取小米 MiMo 文档...")
    
    # 创建输出目录
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 抓取主页面
    print(f"抓取：{DOCS_URL}")
    html = fetch_page(DOCS_URL)
    
    if html:
        # 转换为 Markdown
        markdown = html_to_markdown(html, "小米 MiMo 文档 - 欢迎")
        
        # 保存
        output_file = os.path.join(OUTPUT_DIR, "00-welcome.md")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown)
        print(f"已保存：{output_file}")
    
    # 创建索引文件
    index_content = f"""# 小米 MiMo 文档知识库

**创建时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**来源**: https://platform.xiaomimimo.com
**API 文档**: https://platform.xiaomimimo.com/#/docs/welcome

## 文件列表

| 文件 | 描述 |
|------|------|
| 00-welcome.md | 欢迎页面 |

## 模型信息

- **MiMo-V2-Pro**: 多模态理解模型
- **MiMo-V2-Omni**: 全能多模态模型

## API 信息

- **Base URL**: https://api.xiaomimimo.com/v1
- **认证**: Bearer Token (API Key)
- **接口类型**: OpenAI 兼容

## 更新日志

- {datetime.now().strftime('%Y-%m-%d')}: 初始版本
"""
    
    index_file = os.path.join(OUTPUT_DIR, "README.md")
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(index_content)
    print(f"已保存索引：{index_file}")
    
    print("\n抓取完成！")

if __name__ == "__main__":
    main()
