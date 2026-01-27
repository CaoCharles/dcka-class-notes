---
name: MkDocs 部署流程
description: DCKA 文件網站的本地預覽與 GitHub Pages 部署流程
---

# MkDocs 部署流程 Skill

## 概述

本 Skill 定義 DCKA 課程網站的部署流程，包含本地預覽、GitHub 提交、和 GitHub Pages 部署。

## 觸發條件

當使用者提到以下關鍵字時啟用：
- 部署、deploy、發布
- 預覽、serve、本地測試
- 推送、push、上傳

---

## 快速命令

### 本地預覽
```bash
uv run mkdocs serve
```
瀏覽器開啟：http://127.0.0.1:8000/

### 提交並推送
```bash
git add .
git commit -m "更新說明"
git push
```

### 部署到 GitHub Pages
```bash
uv run mkdocs gh-deploy --force
```

---

## 完整部署流程

```mermaid
graph LR
    A[修改檔案] --> B[git add .]
    B --> C[git commit]
    C --> D[git push]
    D --> E[mkdocs gh-deploy]
    E --> F[GitHub Pages 更新]
```

### 步驟 1：本地預覽確認
```bash
uv run mkdocs serve
```
- 檢查頁面排版
- 確認 Mermaid 圖表正常
- 測試連結是否正確

### 步驟 2：提交變更
```bash
git add .
git commit -m "描述你的變更"
git push
```

### 步驟 3：部署到 GitHub Pages
```bash
uv run mkdocs gh-deploy --force
```

**預期輸出**：
```
INFO    -  Your documentation should shortly be available at: https://CaoCharles.github.io/dcka-class-notes/
```

---

## 專案特殊設定

### 自動生成 content.json

本專案使用 MkDocs Hook 在建置時自動生成 `content.json`：

**設定位置**: `mkdocs.yml`
```yaml
hooks:
  - hooks/generate_content.py
```

**Hook 腳本**: `hooks/generate_content.py`
- 讀取所有 `.md` 檔案
- 生成 `site/content.json` 供 AI Chatbot 使用

### 使用的外掛

| 外掛 | 用途 |
|------|------|
| `glightbox` | 圖片放大檢視 |
| `git-revision-date-localized` | 顯示最後更新時間 |
| `git-authors` | 顯示作者資訊 |

---

## 故障排除

### 問題：部署後頁面沒更新
**解決**：清除瀏覽器快取，或等待 1-2 分鐘

### 問題：Mermaid 圖表不顯示
**解決**：確認 `mkdocs.yml` 有正確設定：
```yaml
markdown_extensions:
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
```

### 問題：content.json 沒有生成
**解決**：確認 `hooks/generate_content.py` 存在且 `mkdocs.yml` 有設定 hooks

---

## 相關檔案

| 檔案 | 說明 |
|------|------|
| `mkdocs.yml` | MkDocs 主設定檔 |
| `hooks/generate_content.py` | 自動生成 content.json |
| `docs/assets/stylesheets/extra.css` | 客製 CSS 樣式 |
| `docs/assets/js/chatbot.js` | AI Chatbot 前端 |
