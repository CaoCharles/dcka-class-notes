"""
MkDocs Hook: 在 build 完成後自動生成 content.json
這個檔案會被 MkDocs 自動載入並執行
"""

import json
from pathlib import Path


def on_post_build(config, **kwargs):
    """
    在 MkDocs build 完成後執行
    生成 content.json 供 chatbot 使用
    
    Args:
        config: MkDocs 的設定檔內容
        **kwargs: 其他參數
    """
    
    # 取得目錄路徑
    site_dir = Path(config['site_dir'])      # 輸出目錄 (預設是 site/)
    docs_dir = Path(config['docs_dir'])      # 原始文檔目錄 (預設是 docs/)
    
    print("=" * 50)
    print("Generating content.json...")
    print(f"Docs dir: {docs_dir}")
    print(f"Output dir: {site_dir}")
    
    content = []
    
    # 遍歷所有 markdown 檔案
    for md_file in sorted(docs_dir.rglob('*.md')):
        try:
            # 讀取檔案內容
            with open(md_file, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # 從 mkdocs.yml 讀取 site_url 作為 base
            site_url = config.get('site_url', '').rstrip('/')
            
            # 計算這個檔案對應的 URL 路徑
            # 例如: docs/java/basics.md → /dcka-class-notes/java/basics/
            rel_path = md_file.relative_to(docs_dir)
            url_path = '/' + str(rel_path).replace('\\', '/').replace('.md', '/')
            
            # 特殊處理: index.md 對應到目錄根路徑
            if url_path.endswith('index/'):
                url_path = url_path[:-6]  # 移除 'index/'
            
            # 如果是根目錄的 index.md，URL 就是 '/'
            if url_path == '/index/':
                url_path = '/'
            
            # 組合完整 URL
            full_url = site_url + url_path
            
            # 提取標題
            # 優先使用第一個 # 開頭的標題
            title = md_file.stem.replace('-', ' ').replace('_', ' ').title()
            
            lines = text.split('\n')
            for line in lines:
                if line.strip().startswith('# '):
                    title = line.strip()[2:].strip()
                    break
            
            # 加入到內容列表
            content.append({
                'title': title,
                'url': full_url,
                'content': text
            })
            
            print(f"  [OK] {md_file.name} -> {full_url}")
            
        except Exception as e:
            print(f"  [ERROR] {md_file}: {e}")
    
    # 寫入 content.json
    output_file = site_dir / 'content.json'
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
        
        print("=" * 50)
        print(f"[SUCCESS] Generated {output_file}")
        print(f"[SUCCESS] Processed {len(content)} pages")
        print("=" * 50)
        
    except Exception as e:
        print(f"[ERROR] Failed to write content.json: {e}")
