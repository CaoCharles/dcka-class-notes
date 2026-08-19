# 系統元件與部署拓撲

![DCKA 整體系統架構](assets/images/overall-architecture.svg)

## 如何閱讀這張圖

這張圖是目前實作的 **C4 Container／Deployment View**，用來回答架構師通常會先問的四件事：系統有哪些可部署元件、部署在哪個平台、資料跨越哪些信任邊界，以及哪一段是建置控制流、哪一段是執行期資料流。

- 實線：使用者執行期的 HTTP／HTTPS 資料流。
- 虛線：Git、Build、Deploy 與 Secret 注入等控制流。
- 藍色：本機或瀏覽器端元件。
- 紫色：GitHub 的原始碼、CI/CD 與靜態託管。
- 綠色：Google Cloud 的建置與 Cloud Run runtime。
- 紅色：Secret 或需要優先處理的安全邊界。

圖中的 Cloud Build 與 Artifact Registry 是 `gcloud run deploy --source backend` 所委派的 Google Cloud managed services；不是 repository 中另外撰寫的應用元件。

## 架構概念

系統分為兩條相互配合的流程：

1. **教材網站**：Markdown 經 MkDocs 建置後部署到 GitHub Pages。
2. **AI 助教**：瀏覽器把教材上下文與問題送到 Cloud Run，FastAPI 再呼叫 Gemini API。

前端是純靜態網站，閱讀教材不需要應用伺服器；只有使用 AI 助教時才會呼叫 Cloud Run。Cloud Run 不保存可供下一個 request 使用的應用 Session；瀏覽器以 `sessionStorage` 保存畫面上的對話狀態，後端則把每次問答的稽核紀錄持久化到 Firestore。

## 部署單元與信任邊界

### Client & Developer Zone

- 開發者在本機維護 `docs/`、`mkdocs.yml`、`hooks/` 與 `backend/`。
- MkDocs build 是前端 artifact 的產生點；建置後的 HTML、CSS、JavaScript、圖片及 `content.json` 才會送到 `gh-pages`。
- Browser runtime 負責 Chatbot UI、全站教材記憶體快取、Markdown rendering 與對話 Session。

### GitHub Control／Delivery Plane

- `main` 是 application source of truth。
- `gh-pages` 是前端 deployable artifact，不是主要開發分支。
- GitHub Actions 只在 `backend/**` 或 workflow 本身變更時觸發後端部署。
- `GCP_SA_KEY`、`GCP_PROJECT_ID`、`GEMINI_API_KEY` 由 GitHub Secrets 提供。

### Google Cloud Runtime

- Cloud Build 依照 `backend/Dockerfile` 建置 image，Artifact Registry 保存 managed image artifact。
- Cloud Run revision 執行 FastAPI／Uvicorn 與 `google-genai` SDK。
- Cloud Run 對外提供 public HTTPS ingress，服務本身是 stateless。
- `GEMINI_API_KEY` 以 runtime environment variable 注入，不會送到 GitHub Pages 或瀏覽器。
- Cloud Firestore 使用 Native mode，`chat_logs` collection 保存匿名問答紀錄。
- Cloud Run service account 透過 `roles/datastore.user` 存取 Firestore；Browser 不直接連線資料庫。
- 每筆紀錄包含 `session_id`、問題、回答、模型、延遲、成功／失敗狀態、錯誤與 server timestamp。

### External AI Boundary

- Cloud Run 透過 Google API 呼叫 `gemini-3.5-flash`。
- Browser 不直接持有或呼叫 Gemini API Key。

## 元件責任

### Markdown 與 MkDocs

- `docs/`：課程文章、圖片、PDF 與音檔。
- `mkdocs.yml`：網站名稱、導覽、主題、Markdown extensions 與 plugins。
- `hooks/generate_content.py`：建置完成後掃描 `docs/**/*.md`，產生 `site/content.json`。

### GitHub

- `main`：保存 Markdown、前端、後端與設定。
- `gh-pages`：保存 MkDocs 建置後的靜態網站。
- GitHub Pages：將 `gh-pages` 內容發布為公開網站。
- GitHub Actions：當 `backend/**` 變更並推到 `main` 時，自動部署 Cloud Run。

### Cloud Run 與 FastAPI

- 對外提供 `GET /` 健康檢查。
- 對外提供 `POST /api/chat` 問答端點。
- 從環境變數取得 `GEMINI_API_KEY`。
- 使用 `google-genai` SDK 呼叫 `gemini-3.5-flash`。
- 將 System Instruction 與對話內容分開傳入模型。

### 瀏覽器

- 顯示 MkDocs 教材。
- 載入 `content.json` 全站文件。
- 組合回答規則與文件上下文。
- 將 Chatbot 對話歷史保存在 `sessionStorage`。
- 使用 `marked.js` 將模型回應轉成 HTML。

## 目前部署方式

- 前端：本機執行 `uv run mkdocs gh-deploy --force`。
- 後端：push `main` 後，由 `.github/workflows/deploy-backend.yml` 自動部署到 Cloud Run。

因此「前端手動、後端自動」是目前實際狀態。

## Current-state 架構限制

- `/api/chat` 允許匿名存取，沒有 Login、API authentication 或 rate limiting。
- CORS 目前是 `*`，尚未收斂為正式網站與 localhost allowlist。
- Firestore 已提供持久化問答紀錄，但沒有登入身分；`session_id` 只能用來關聯同一個分頁的匿名對話，不能當成身份或授權依據。
- Cloud Run 仍是 stateless compute；persistent state 位於 Firestore。
- 所謂 RAG 目前是 Browser 將完整 `content.json` 放進每次請求的 `system_instruction`，不是 embedding／top-k retrieval 架構。
- `log_chat()` 使用同步 Firestore client 且在 HTTP response 前呼叫；`try/except` 可隔離寫入失敗，但寫入時間仍可能增加 request latency。
- GitHub Actions 使用長效 Service Account JSON；後續可改成 Workload Identity Federation，降低長效憑證風險。

## 維護建議

### 優先處理

- 將正式環境 CORS 從 `*` 改成明確來源白名單。
- 為公開 `/api/chat` 加入速率限制、訊息長度與 History 大小限制。
- 不要把完整例外訊息直接回傳給使用者，避免暴露後端細節。
- 為 Firestore 問答內容訂定資料保留期限、敏感資訊遮罩與管理者查閱權限。

### 中期改善

- `async def` endpoint 目前呼叫同步 Gemini client；可改用 async client，或把 endpoint 改成同步 `def`，避免高併發時阻塞 event loop。
- Firestore logging 可改成 async client、thread offload 或受控背景工作，降低寫入對聊天回應時間的影響。
- Backend 建置應鎖定可重現的 `google-genai` 版本；目前只有 `>=1.0.0`，但程式使用較新的 thinking 設定。
- 文件量增加後，將「每次傳送全站文件」升級成向量檢索式 RAG，降低 token、延遲與成本。

### 文件同步

- `backend/README.md` 的 RAG 開頭與 sequence diagram 仍有「擷取目前頁面」的舊描述，實際已是載入全站 `content.json`。
- `backend/Dockerfile` 的註解仍提到 Railway，實際部署平台已是 Cloud Run。
