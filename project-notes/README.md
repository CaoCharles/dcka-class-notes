# DCKA 學習筆記：網站與 AI 助教技術紀錄

這個目錄是個人技術紀錄與同事分享材料，不屬於 MkDocs 的 `docs/` 內容，因此不會出現在正式課程網站，也不會被 `content.json` 收進 AI 助教的文件上下文。

## 閱讀順序

1. [System Component & Deployment Architecture](architecture.md)
2. [Frontend & Backend Delivery Architecture](github-pages-deployment.md)
3. [AI Assistant Runtime Interaction Architecture](ai-chatbot-integration.md)
4. [Word 技術分享文件（安全強化版）](word/DCKA_網站與AI助教技術架構_安全強化版.docx)

## 可編輯架構圖

- [Draw.io 原始檔（三個分頁）](assets/diagrams/dcka-system-architecture.drawio)
- [System Component & Deployment Architecture SVG](assets/images/overall-architecture.svg)
- [Frontend & Backend Delivery Architecture SVG](assets/images/github-pages-deployment.svg)
- [AI Assistant Runtime Interaction Architecture SVG](assets/images/ai-chatbot-integration.svg)

## 專案定位

DCKA 學習筆記把 Docker 與 Kubernetes 課程內容寫成 Markdown，再由 MkDocs Material 建置成 GitHub Pages 靜態網站。網站中的「學習筆記小幫手」會載入全站教材，透過 Cloud Run 上的 FastAPI Proxy 呼叫 Gemini 3.5 Flash，讓 API Key 不必出現在瀏覽器中。

## 2026-08-19 驗證結果

- GitHub Pages 正常提供網站與新版 `chatbot.js`。
- Cloud Run 健康檢查回傳 HTTP 200。
- `/api/chat` 從 `https://caocharles.github.io` 呼叫成功，CORS 正常。
- WIF 後端部署成功，Cloud Run revision `dcka-chatbot-backend-00006-drd` 使用專用 `dcka-chatbot-runtime` 並承接 100% 流量。
- 簡短部署驗證問題約 1.73 秒回覆。
- 實際 Chatbot 問答成功並能提供課程文章連結。
- Firestore 已寫入驗證紀錄，`chat_logs.expires_at` TTL policy 為 `ACTIVE`。
- 安全強化與 Backend-owned Prompt 已通過 13 項後端自動測試及 MkDocs strict build；既有 GitHub Pages 與 Cloud Run WIF 部署回歸驗證亦正常。

> 分享注意：這個 GitHub repository 若為 Public，`project-notes/` 也會公開。請勿放入 API Key、Service Account JSON、密碼或公司內部機密。
