# DCKA 學習筆記：網站與 AI 助教技術紀錄

這個目錄是個人技術紀錄與同事分享材料，不屬於 MkDocs 的 `docs/` 內容，因此不會出現在正式課程網站，也不會被 `content.json` 收進 AI 助教的文件上下文。

## 閱讀順序

1. [系統元件與部署拓撲](architecture.md)
2. [Frontend／Backend Delivery Architecture](github-pages-deployment.md)
3. [AI 助教技術泳道與 Firestore 紀錄](ai-chatbot-integration.md)
4. [Word 技術分享文件](word/DCKA_網站與AI助教技術架構.docx)

## 可編輯架構圖

- [Draw.io 原始檔（三個分頁）](assets/diagrams/dcka-system-architecture.drawio)
- [C4 Container／Deployment View SVG](assets/images/overall-architecture.svg)
- [Frontend／Backend Delivery View SVG](assets/images/github-pages-deployment.svg)
- [AI 技術泳道／Firestore Data Flow SVG](assets/images/ai-chatbot-integration.svg)

## 專案定位

DCKA 學習筆記把 Docker 與 Kubernetes 課程內容寫成 Markdown，再由 MkDocs Material 建置成 GitHub Pages 靜態網站。網站中的「學習筆記小幫手」會載入全站教材，透過 Cloud Run 上的 FastAPI Proxy 呼叫 Gemini 3.5 Flash，讓 API Key 不必出現在瀏覽器中。

## 2026-08-19 驗證結果

- GitHub Pages 正常提供網站與新版 `chatbot.js`。
- Cloud Run 健康檢查回傳 HTTP 200。
- `/api/chat` 從 `https://caocharles.github.io` 呼叫成功，CORS 正常。
- 簡短測試問題約 3.70 秒回覆。
- 實際 Chatbot 問答成功並能提供課程文章連結。

> 分享注意：這個 GitHub repository 若為 Public，`project-notes/` 也會公開。請勿放入 API Key、Service Account JSON、密碼或公司內部機密。
