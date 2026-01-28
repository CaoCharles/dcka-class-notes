"""
MkDocs Hook: 在 build 完成後自動生成 content.json
複製此檔案到專案的 hooks/ 目錄
"""

import json
from pathlib import Path


def on_post_build(config, **kwargs):
    """
    在 MkDocs build 完成後執行
    生成 content.json 供 chatbot 使用
    """
    
    site_dir = Path(config['site_dir'])
    docs_dir = Path(config['docs_dir'])
    
    print("=" * 50)
    print("Generating content.json...")
    
    content = []
    
    for md_file in sorted(docs_dir.rglob('*.md')):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                text = f.read()
            
            site_url = config.get('site_url', '').rstrip('/')
            rel_path = md_file.relative_to(docs_dir)
            url_path = '/' + str(rel_path).replace('\\', '/').replace('.md', '/')
            
            if url_path.endswith('index/'):
                url_path = url_path[:-6]
            if url_path == '/index/':
                url_path = '/'
            
            full_url = site_url + url_path
            
            # 提取標題
            title = md_file.stem.replace('-', ' ').replace('_', ' ').title()
            lines = text.split('\n')
            for line in lines:
                if line.strip().startswith('# '):
                    title = line.strip()[2:].strip()
                    break
            
            content.append({
                'title': title,
                'url': full_url,
                'content': text
            })
            
            print(f"  [OK] {md_file.name} -> {full_url}")
            
        except Exception as e:
            print(f"  [ERROR] {md_file}: {e}")
    
    output_file = site_dir / 'content.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=2)
    
    print("=" * 50)
    print(f"[SUCCESS] Generated {output_file}")
    print(f"[SUCCESS] Processed {len(content)} pages")
