---
name: 專案初始化
description: 從零開始建立 MkDocs + AI Chatbot 網站的完整流程指南
---

# 專案初始化 Skill

## 概述

本 Skill 引導從零開始建立一個完整的課程網站，只需複製範本檔案即可快速啟動。

## 觸發條件

當使用者提到以下關鍵字時啟用：
- 新專案、從零開始、初始化
- 建立網站、建立課程網站

---

## 🚀 快速啟動（5 分鐘）

### 步驟 1：建立專案並複製範本

```bash
# 建立專案
mkdir my-course-site && cd my-course-site
git init

# 建立目錄結構
mkdir -p docs/assets/css docs/assets/js docs/assets/images hooks backend

# 設定 Python
uv python pin 3.12
```

### 步驟 2：從 Skills 複製範本

從 `.agent/skills/` 複製以下範本到專案：

| 來源 | 目標 |
|------|------|
| `mkdocs-setup/assets/pyproject.toml` | `./pyproject.toml` |
| `mkdocs-setup/assets/mkdocs.yml` | `./mkdocs.yml` |
| `mkdocs-setup/assets/index.md` | `./docs/index.md` |
| `mkdocs-setup/assets/extra.css` | `./docs/assets/css/extra.css` |
| `chatbot-setup/assets/chatbot.js` | `./docs/assets/js/chatbot.js` |
| `chatbot-setup/assets/chatbot.css` | `./docs/assets/css/chatbot.css` |
| `chatbot-setup/assets/generate_content.py` | `./hooks/generate_content.py` |
| `railway-deploy/assets/*` | `./backend/` |

### 步驟 3：修改設定（搜尋 TODO）

**mkdocs.yml**
```yaml
site_name: 你的網站名稱
site_url: https://YOUR-USERNAME.github.io/YOUR-REPO-NAME/
repo_name: YOUR-USERNAME/YOUR-REPO-NAME
```

**docs/assets/js/chatbot.js**
```javascript
window.BACKEND_API_URL = "https://YOUR-APP.up.railway.app";
const repoName = '/YOUR-REPO-NAME';
const BASE_URL = "https://YOUR-USERNAME.github.io/YOUR-REPO-NAME";
```

### 步驟 4：安裝依賴並測試

```bash
uv sync
uv run mkdocs serve
```

瀏覽器開啟 http://127.0.0.1:8000 確認網站正常

---

## 📁 完整專案結構

```
my-course-site/
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
└── backend/
    ├── .python-version
    ├── pyproject.toml
    ├── chat_server.py
    └── Dockerfile
```

---

## 🔧 範本清單

### mkdocs-setup (4 個範本)
- `mkdocs.yml` - MkDocs 設定，含 hooks、chatbot、Mermaid
- `pyproject.toml` - UV 專案設定
- `index.md` - 首頁範本
- `extra.css` - 深紫色主題樣式

### chatbot-setup (3 個範本)
- `chatbot.js` - 前端邏輯，含 TODO 標記
- `chatbot.css` - 聊天室樣式
- `generate_content.py` - MkDocs hook

### railway-deploy (4 個範本)
- `chat_server.py` - FastAPI + Gemini
- `pyproject.toml` - 後端依賴
- `Dockerfile` - 使用 UV
- `.python-version` - Python 3.12

---

## 📋 部署清單

### GitHub Pages（前端）
```bash
git add .
git commit -m "Initial commit"
git push -u origin main
uv run mkdocs gh-deploy --force
```

### Railway（後端）
1. 前往 [Railway](https://railway.app/)
2. Deploy from GitHub repo
3. 設定 Root Directory: `backend`
4. 設定環境變數: `GEMINI_API_KEY`

---

## ✅ 驗證清單

- [ ] `uv run mkdocs serve` 正常啟動
- [ ] 網站可在 http://127.0.0.1:8000 存取
- [ ] 右下角出現聊天圖示
- [ ] 點擊圖示可開啟聊天視窗
- [ ] 輸入問題可得到 AI 回覆
- [ ] GitHub Pages 部署成功
- [ ] Railway 後端部署成功

---

## 🔗 相關 Skills

| Skill | 用途 |
|-------|------|
| **mkdocs-setup** | MkDocs + UV 環境詳細設定 |
| **chatbot-setup** | AI Chatbot 前後端設定 |
| **railway-deploy** | Railway 部署詳細步驟 |
| **mkdocs-deploy** | GitHub Pages 部署流程 |
