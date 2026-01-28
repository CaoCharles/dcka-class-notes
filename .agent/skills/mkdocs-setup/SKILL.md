---
name: MkDocs 環境設定
description: UV + Python 3.12 + MkDocs Material 的完整環境設定
---

# MkDocs 環境設定 Skill

## 概述

本 Skill 定義如何使用 UV 建立 MkDocs Material 開發環境，包含完整的範本檔案。

## 觸發條件

當使用者提到以下關鍵字時啟用：
- UV 設定、Python 環境
- MkDocs 安裝、Material 主題
- pyproject.toml、新專案

---

## 範本檔案

本 Skill 包含以下範本（位於 `templates/` 目錄）：

| 檔案 | 說明 |
|------|------|
| `mkdocs.yml` | MkDocs 主設定檔，含 hooks 和 chatbot 設定 |
| `pyproject.toml` | UV 專案設定，含所有必要依賴 |
| `index.md` | 首頁範本，含 grid cards 和表格 |
| `extra.css` | 深紫色主題樣式 |

---

## 快速設定

```bash
# 1. 建立專案目錄
mkdir my-course-site
cd my-course-site

# 2. 設定 Python 版本
uv python pin 3.12

# 3. 初始化專案
uv init

# 4. 安裝套件
uv add mkdocs-material mkdocs-glightbox mkdocs-git-revision-date-localized-plugin mkdocs-git-authors-plugin

# 5. 建立目錄結構
mkdir -p docs/assets/css docs/assets/js docs/assets/images hooks

# 6. 複製範本
# (從 .agent/skills/mkdocs-setup/templates/ 複製)

# 7. 測試
uv run mkdocs serve
```

---

## 目錄結構

```
project/
├── .python-version          # 3.12
├── pyproject.toml           # UV 專案設定
├── uv.lock                  # 依賴鎖定
├── mkdocs.yml               # MkDocs 設定
├── docs/
│   ├── index.md             # 首頁
│   └── assets/
│       ├── css/
│       │   ├── extra.css    # 網站樣式
│       │   └── chatbot.css  # Chatbot 樣式
│       ├── js/
│       │   └── chatbot.js   # Chatbot 邏輯
│       └── images/
│           └── favicon.png
├── hooks/
│   └── generate_content.py  # 自動生成 content.json
└── backend/                 # AI 後端（可選）
    ├── chat_server.py
    ├── Dockerfile
    └── requirements.txt
```

---

## pyproject.toml 設定

```toml
[project]
name = "my-course-site"
version = "0.1.0"
description = "課程文件網站"
requires-python = ">=3.12"
dependencies = [
    "mkdocs-material>=9.5.0",
    "mkdocs-glightbox>=0.4.0",
    "mkdocs-git-revision-date-localized-plugin>=1.2.0",
    "mkdocs-git-authors-plugin>=0.7.0",
]
```

---

## mkdocs.yml 關鍵設定

### 基本資訊
```yaml
site_name: 我的課程網站
site_url: https://username.github.io/repo-name/
```

### Hooks（自動生成 content.json）
```yaml
hooks:
  - hooks/generate_content.py
```

### Chatbot 載入
```yaml
extra_javascript:
  - https://cdn.jsdelivr.net/npm/marked/marked.min.js
  - assets/js/chatbot.js

extra_css:
  - assets/css/extra.css
  - assets/css/chatbot.css
```

### Mermaid 圖表
```yaml
markdown_extensions:
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
```

---

## 常用指令

| 指令 | 說明 |
|------|------|
| `uv run mkdocs serve` | 本地預覽 (http://127.0.0.1:8000) |
| `uv run mkdocs build` | 建置靜態網站 |
| `uv run mkdocs gh-deploy --force` | 部署到 GitHub Pages |
| `uv add <package>` | 新增套件 |
| `uv sync` | 同步依賴 |

---

## 故障排除

### UV 未安裝
```powershell
# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Python 3.12 未安裝
```bash
uv python install 3.12
uv python pin 3.12
```

### MkDocs 指令找不到
```bash
uv sync  # 重新同步依賴
```

### 中文搜尋問題
確認 `mkdocs.yml` 有設定：
```yaml
plugins:
  - search:
      lang: zh
```

---

## 相關 Skills

- **chatbot-setup** - AI Chatbot 前後端設定
- **mkdocs-deploy** - GitHub Pages 部署流程
- **project-init** - 完整專案初始化流程
