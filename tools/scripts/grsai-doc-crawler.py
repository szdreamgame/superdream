#!/usr/bin/env python3
"""
GRS AI 文档爬虫工具
将 https://grsai.ai/zh/dashboard/documents 的文档爬取并转换为 Markdown 格式
"""

import os
import re
import json
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime

# 配置
BASE_URL = "https://grsai.ai"
DOCUMENTS_URL = "https://grsai.ai/zh/dashboard/documents"
OUTPUT_DIR = "/root/.openclaw/workspace/memory/grsai-docs"

# 已知文档列表（根据实际文档调整）
KNOWN_DOCUMENTS = [
    "nano-banana",
    "nano-banana-api",
    "image-generator",
    "character-design",
    "scene-design",
]

# 请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

class GRSAIDocCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.visited_urls = set()
        self.documents = []
        
    def fetch_page(self, url):
        """获取网页内容"""
        try:
            print(f"📥 正在获取：{url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"❌ 获取失败 {url}: {e}")
            return None
    
    def extract_document_links(self, html, base_url):
        """从文档列表页提取文档链接"""
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        
        # 查找所有文档链接（根据实际情况调整选择器）
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            full_url = urljoin(base_url, href)
            
            # 过滤文档页面
            if '/documents/' in full_url and full_url not in self.visited_urls:
                # 排除列表页本身
                if not full_url.endswith('/documents'):
                    links.append(full_url)
                    self.visited_urls.add(full_url)
        
        return links
    
    def html_to_markdown(self, html, url):
        """将 HTML 转换为 Markdown"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # 提取标题
        title = soup.find('h1')
        title_text = title.get_text().strip() if title else "无标题"
        
        # 提取主要内容
        main_content = soup.find('article') or soup.find('main') or soup.find('div', class_='content') or soup.body
        
        if not main_content:
            return f"# {title_text}\n\n无法提取内容"
        
        # 转换为 Markdown
        markdown = self.convert_element_to_markdown(main_content)
        
        # 添加元数据
        frontmatter = f"""---
title: {title_text}
source_url: {url}
crawled_date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
---

"""
        return frontmatter + f"# {title_text}\n\n" + markdown
    
    def convert_element_to_markdown(self, element, depth=0):
        """递归转换 HTML 元素为 Markdown"""
        if not element:
            return ""
        
        markdown = ""
        
        # 处理文本节点
        if isinstance(element, str):
            return element.strip() + "\n"
        
        # 标签映射
        tag_handlers = {
            'h1': lambda e: f"\n{'#'*1} {e.get_text().strip()}\n\n",
            'h2': lambda e: f"\n{'#'*2} {e.get_text().strip()}\n\n",
            'h3': lambda e: f"\n{'#'*3} {e.get_text().strip()}\n\n",
            'h4': lambda e: f"\n{'#'*4} {e.get_text().strip()}\n\n",
            'h5': lambda e: f"\n{'#'*5} {e.get_text().strip()}\n\n",
            'h6': lambda e: f"\n{'#'*6} {e.get_text().strip()}\n\n",
            'p': lambda e: f"{e.get_text().strip()}\n\n",
            'br': lambda e: "\n",
            'hr': lambda e: "\n---\n\n",
            'strong': lambda e: f"**{e.get_text().strip()}**",
            'b': lambda e: f"**{e.get_text().strip()}**",
            'em': lambda e: f"*{e.get_text().strip()}*",
            'i': lambda e: f"*{e.get_text().strip()}*",
            'code': lambda e: f"`{e.get_text().strip()}`",
            'pre': lambda e: f"\n```\n{e.get_text().strip()}\n```\n\n",
            'blockquote': lambda e: f"\n> {e.get_text().strip()}\n\n",
            'ul': lambda e: self.convert_list(e, 'bullet'),
            'ol': lambda e: self.convert_list(e, 'numbered'),
            'li': lambda e: f"- {e.get_text().strip()}\n",
            'a': lambda e: f"[{e.get_text().strip()}]({e.get('href', '#')})",
            'img': lambda e: f"![{e.get('alt', '')}]({e.get('src', '')})\n",
            'table': lambda e: self.convert_table(e),
        }
        
        # 处理子元素
        if hasattr(element, 'children'):
            for child in element.children:
                if isinstance(child, str):
                    text = child.strip()
                    if text:
                        markdown += text + " "
                elif hasattr(child, 'name'):
                    handler = tag_handlers.get(child.name, lambda e: self.convert_element_to_markdown(e, depth+1))
                    try:
                        markdown += handler(child)
                    except:
                        markdown += child.get_text().strip() + "\n"
        
        return markdown
    
    def convert_list(self, element, list_type='bullet'):
        """转换列表"""
        items = []
        for i, li in enumerate(element.find_all('li', recursive=False)):
            text = li.get_text().strip()
            if list_type == 'bullet':
                items.append(f"- {text}")
            else:
                items.append(f"{i+1}. {text}")
        return "\n".join(items) + "\n\n"
    
    def convert_table(self, table):
        """转换表格"""
        rows = []
        for tr in table.find_all('tr'):
            cells = [td.get_text().strip() for td in tr.find_all(['td', 'th'])]
            if cells:
                rows.append("| " + " | ".join(cells) + " |")
                if len(rows) == 1:  # 添加分隔符
                    rows.append("| " + " | ".join(["---"] * len(cells)) + " |")
        return "\n".join(rows) + "\n\n" if rows else ""
    
    def save_markdown(self, content, filename):
        """保存 Markdown 文件"""
        filepath = os.path.join(OUTPUT_DIR, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 已保存：{filepath}")
        return filepath
    
    def crawl_document(self, url):
        """爬取单个文档"""
        html = self.fetch_page(url)
        if not html:
            return None
        
        markdown = self.html_to_markdown(html, url)
        
        # 生成文件名
        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')
        filename = path_parts[-1] if path_parts else "document"
        filename = re.sub(r'[^\w\-]', '', filename) + ".md"
        
        # 保存
        filepath = self.save_markdown(markdown, filename)
        
        # 记录文档信息
        doc_info = {
            "title": filename.replace(".md", ""),
            "url": url,
            "filepath": filepath,
            "crawled_date": datetime.now().isoformat()
        }
        
        self.documents.append(doc_info)
        return doc_info
    
    def crawl_all(self, start_url=DOCUMENTS_URL):
        """爬取所有文档"""
        print(f"🚀 开始爬取文档库：{DOCUMENTS_URL}")
        print(f"📁 输出目录：{OUTPUT_DIR}\n")
        
        # 创建输出目录
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # 构建文档 URL 列表
        doc_links = []
        
        # 尝试从列表页提取
        html = self.fetch_page(start_url)
        if html:
            doc_links = self.extract_document_links(html, start_url)
        
        # 如果列表页失败，使用已知文档列表
        if not doc_links:
            print("⚠️ 无法从列表页提取，使用已知文档列表...")
            doc_links = [f"{DOCUMENTS_URL}/{doc_id}" for doc_id in KNOWN_DOCUMENTS]
        
        print(f"📋 找到 {len(doc_links)} 个文档链接\n")
        
        # 爬取每个文档
        for i, url in enumerate(doc_links, 1):
            print(f"\n[{i}/{len(doc_links)}] 处理文档...")
            self.crawl_document(url)
            time.sleep(1)  # 避免请求过快
        
        # 生成索引
        self.generate_index()
        
        print(f"\n🎉 爬取完成！共处理 {len(self.documents)} 个文档")
        print(f"📂 保存位置：{OUTPUT_DIR}")
    
    def generate_index(self):
        """生成索引导航"""
        index_content = f"""# GRS AI 文档库索引

**爬取时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**文档总数**: {len(self.documents)}  
**源地址**: {DOCUMENTS_URL}

---

## 文档列表

| 序号 | 文档名称 | 源 URL | 本地文件 |
|------|----------|--------|----------|
"""
        
        for i, doc in enumerate(self.documents, 1):
            filename = os.path.basename(doc['filepath'])
            index_content += f"| {i} | [{doc['title']}]({filename}) | [源链接]({doc['url']}) | `{filename}` |\n"
        
        index_content += f"""

---

## 使用说明

1. **查看单个文档**: 直接打开对应的 `.md` 文件
2. **搜索内容**: 使用 `grep` 或文本编辑器的搜索功能
3. **更新文档**: 重新运行爬虫脚本

## 目录结构

```
{OUTPUT_DIR}/
├── INDEX.md              # 本索引文件
├── nano-banana.md        # Nano Banana 文档
├── other-doc.md          # 其他文档
└── ...
```

---

*自动生成 by GRS AI Doc Crawler*
"""
        
        # 保存索引
        index_path = os.path.join(OUTPUT_DIR, "INDEX.md")
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_content)
        
        print(f"📑 已生成索引：{index_path}")
        
        # 保存 JSON 索引
        json_path = os.path.join(OUTPUT_DIR, "documents.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                "crawled_date": datetime.now().isoformat(),
                "total": len(self.documents),
                "source": DOCUMENTS_URL,
                "documents": self.documents
            }, f, ensure_ascii=False, indent=2)
        
        print(f"📊 已生成 JSON 索引：{json_path}")


if __name__ == "__main__":
    crawler = GRSAIDocCrawler()
    crawler.crawl_all()
