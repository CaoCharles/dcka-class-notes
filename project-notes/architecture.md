# System Component & Deployment Architecture

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
- MkDocs build 是前端 artifact 的產生點；建置後的 HTML、CSS、JavaScript、圖片及 `content.json` 會由 Actions 上傳為 GitHub Pages Artifact。
- Browser runtime 負責 Chatbot UI、全站教材記憶體快取、Markdown rendering 與對話 Session。

### GitHub Control／Delivery Plane

- `main` 是 application source of truth。
- GitHub Pages Artifact 是前端 deployable artifact，不是主要開發分支。
- GitHub Actions 以兩條 workflow 分別處理 MkDocs Pages 與 Cloud Run 後端部署。
- GitHub Actions 使用 OIDC／Workload Identity Federation 取得 `github-actions-deployer` 的短效憑證；`GCP_PROJECT_ID`、WIF Provider 與 deployer/build/runtime Service Account 使用 GitHub Variables，只有 `GEMINI_API_KEY` 使用 GitHub Secret。

### Google Cloud Runtime

- Cloud Build 以專用 `dcka-cloud-build`（`roles/run.builder`）依照 `backend/Dockerfile` 建置 image，Artifact Registry 保存 managed image artifact。
- Cloud Run revision 執行 FastAPI／Uvicorn 與 `google-genai` SDK。
- Cloud Run 對外提供 public HTTPS ingress，服務本身是 stateless。
- `GEMINI_API_KEY` 以 runtime environment variable 注入，不會送到 GitHub Pages 或瀏覽器。
- Cloud Firestore 使用 Native mode，`chat_logs` collection 保存匿名問答紀錄。
- Cloud Run 使用專用 `dcka-chatbot-runtime` service account，透過 `roles/datastore.user` 存取 Firestore；Browser 不直接連線資料庫。
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
- Pages Artifact：保存 Actions 建置完成的靜態網站 bundle。
- GitHub Pages：由 `actions/deploy-pages` 將 Artifact 發布為公開網站。
- GitHub Actions：當 `backend/**` 變更並推到 `main` 時，自動部署 Cloud Run。

### Cloud Run 與 FastAPI

- 對外提供 `GET /` 健康檢查。
- 對外提供 `POST /api/chat` 問答端點。
- 只接受 GitHub Pages 與 localhost Origin，並限制 body、訊息、History 與請求速率。
- 從環境變數取得 `GEMINI_API_KEY`。
- 使用鎖定的 `google-genai==2.18.1` SDK 呼叫 `gemini-3.5-flash`。
- 將 System Instruction 與對話內容分開傳入模型。
- 先回傳一般化成功／錯誤 response，再由 `BackgroundTasks` 寫入遮罩後的 Firestore Log。

### 瀏覽器

- 顯示 MkDocs 教材。
- 載入 `content.json` 全站文件。
- 組合回答規則與文件上下文。
- 將 Chatbot 對話歷史保存在 `sessionStorage`。
- 使用 `marked.js` 將模型回應轉成 HTML。

## 目前部署方式

- 前端：push `main` 後，由 `.github/workflows/deploy-pages.yml` 建置並發布 GitHub Pages。
- 後端：push `main` 後，由 `.github/workflows/deploy-backend.yml` 自動部署到 Cloud Run。

兩條 pipeline 均已自動化，Repository Pages Source 已設定為 GitHub Actions。本機 `mkdocs gh-deploy` 只有在 Source 暫時切回 branch-based deployment 時才可作為緊急 fallback。

## Current-state 架構限制

- `/api/chat` 允許匿名存取，沒有 Login 或 API authentication；現有 rate limiter 是單一 Cloud Run instance 記憶體內計數，不是跨 instance 全域配額。
- CORS 已收斂為正式 GitHub Pages 與 localhost exact-origin allowlist。
- Firestore 已提供持久化問答紀錄，但沒有登入身分；`session_id` 只能用來關聯同一個分頁的匿名對話，不能當成身份或授權依據。
- Cloud Run 仍是 stateless compute；persistent state 位於 Firestore。
- 所謂 RAG 目前是 Browser 將完整 `content.json` 放進每次請求的 `system_instruction`，不是 embedding／top-k retrieval 架構。
- `log_chat()` 仍使用同步 Firestore client，但已移到 response 後的 `BackgroundTasks`；寫入內容會遮罩並帶有 90 天 `expires_at`。
- GitHub Actions 已改用 Workload Identity Federation；Provider 只信任 `CaoCharles/dcka-class-notes` 的 `main` 分支，部署過程不保存長效 Service Account JSON。

## 維護建議

### 已完成

- 正式環境 CORS exact-origin allowlist。
- `/api/chat` rate limiting、訊息／History／request body 大小限制。
- 使用者只收到一般化錯誤，詳細 stack trace 留在 Cloud Logging。
- Firestore 90 天 `expires_at`、敏感資訊遮罩與管理者唯讀權限原則。
- 同步 FastAPI endpoint 避免 event loop 被同步 Gemini 呼叫阻塞。
- Firestore logging 移至 response 後的受控 `BackgroundTasks`。
- `google-genai==2.18.1` 與 `backend/uv.lock`。
- GitHub Pages frontend workflow。
- GitHub Actions Workload Identity Federation 與專用 deployer/build/runtime service accounts；線上部署已驗證成功。
- Firestore `chat_logs.expires_at` TTL policy 已確認為 `ACTIVE`。

### 中期改善

- 文件量增加後，將「每次傳送全站文件」升級成向量檢索式 RAG，降低 token、延遲與成本。
- 若需嚴格全域 rate limit，改接 Cloud Armor／API Gateway 或集中式計數儲存。
- 將 `GEMINI_API_KEY` 改由 Secret Manager 注入，並逐步移除預設 Compute Service Account 的 Project Editor 權限。

### 文件同步

- `backend/README.md` 已改為全站 `content.json` 的 full-context RAG 流程。
- `backend/Dockerfile` 已改成 Cloud Run 註解，並使用 `uv.lock` 安裝依賴。
