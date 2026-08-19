---
authors:
  - name: Charles Cao
    email: author@example.com
date: 2026-08-19
updated: 2026-08-19
tags:
  - Architecture
  - Deployment
  - GitHub Pages
  - Cloud Run
---

# System Component & Deployment Architecture

## 學習目標

完成本章節後，你將能夠：

- [ ] 辨識 DCKA 網站的 Client、Delivery、Runtime 與 Data 元件。
- [ ] 說明 GitHub Pages、Cloud Run、Gemini 與 Firestore 的部署位置。
- [ ] 區分 Runtime Data Flow 與 Build／Deploy Control Flow。

![System Component & Deployment Architecture](../assets/images/architecture/system-component-deployment.svg){ loading=lazy }

!!! tip "閱讀方式"
    實線代表使用者操作時的 Runtime Data Flow；虛線代表建置、部署、密鑰注入與版本發布等 Control Flow。

---

## 主要元件與責任

| 區域 | 元件 | 主要責任 |
|---|---|---|
| Client & Developer | VS Code、Git、uv、Browser | 編輯內容、執行建置及使用網站 |
| GitHub Control Plane | `main`、GitHub Actions、Pages Artifact | 保存原始碼、執行前後端部署、保存靜態網站產物 |
| Static Delivery | GitHub Pages | 提供 HTML、CSS、JavaScript、圖片與 `content.json` |
| Serverless Runtime | Cloud Run、FastAPI、Uvicorn | 驗證 Request、保管 API Key、呼叫 Gemini、記錄問答 |
| External AI | Gemini API | 根據文件上下文與對話內容產生回答 |
| Persistent Data | Cloud Firestore | 保存匿名問答、模型、延遲、狀態與時間戳 |

## Frontend Runtime Flow

1. 使用者從 GitHub Pages 取得靜態網站資源。
2. `chatbot.js` 載入 `content.json`，將網站文章保存在 Browser Memory。
3. Browser 使用 `sessionStorage` 保存 Chat History 與匿名 `session_id`。
4. 使用者送出問題時，Browser 以 HTTPS 呼叫 Cloud Run 的 `/api/chat`。

## Backend Runtime Flow

1. Cloud Run HTTPS Ingress 將 Request 交給 FastAPI，CORS 只接受 GitHub Pages 與 localhost Origin。
2. Backend 套用 1 MiB body、Pydantic 欄位與每來源 20 次／分鐘的 instance-local rate limit。
3. 同步 FastAPI endpoint 在 worker thread 呼叫鎖定版本的 `google-genai` SDK，不阻塞 event loop。
4. Backend 先回傳回答或一般化錯誤，再由 `BackgroundTasks` 遮罩並寫入 Firestore。

## State Ownership

| State | 保存位置 | 生命週期 |
|---|---|---|
| `session_id`、Chat History | Browser `sessionStorage` | 同一個 Browser 分頁工作階段 |
| 教材上下文 | Browser Memory | 頁面重新載入前 |
| API Runtime | Cloud Run Instance | Stateless，不保證 Instance 持續存在 |
| 問答紀錄 | Firestore `chat_logs` | Persistent；預設 90 天並由 `expires_at` TTL 管理 |

!!! note "Current-state Security Boundary"
    `/api/chat` 仍是匿名公開入口，沒有登入或 API Authentication；現已具備 exact-origin CORS、輸入上限、instance-local rate limiting、一般化錯誤與 `ACTIVE` 的 Firestore 90 天 TTL。後端部署以 GitHub OIDC／WIF 取得短效憑證，Cloud Run 則以專用 Runtime Service Account 寫入 Firestore。若要跨 Cloud Run instances 套用全域配額，仍需 Cloud Armor、API Gateway 或集中式 rate-limit store。

## 延伸閱讀

- [AI Assistant Runtime Interaction Architecture](ai-assistant-runtime.md)
- [Frontend & Backend Delivery Architecture](frontend-backend-delivery.md)
