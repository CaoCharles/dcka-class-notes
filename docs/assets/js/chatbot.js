// ====== DCKA 課程 AI 聊天機器人 ======
// 版本：2.0 - 全站文件預載 + Anchor 連結支援

// ====== 全域狀態 ======
let chatContainer, chatMessages, chatInput, sendChatBtn;
let openChatBtn, closeChatBtn, toggleFullscreenBtn, clearHistoryBtn;

let allDocsContent = null;
let isContentLoading = false;
let chatHistory = [];

// ====== 設定 ======
// Cloud Run 後端 URL
window.BACKEND_API_URL = window.BACKEND_API_URL || "https://dcka-chatbot-backend-978572634545.asia-east1.run.app";
// 全站文件 JSON URL (自動判斷環境)
const isGitHubPages = window.location.hostname.includes('github.io');
const repoName = '/dcka-class-notes'; // GitHub Repo 名稱
const basePath = isGitHubPages ? repoName : '';
window.ALL_CONTENT_URL = window.ALL_CONTENT_URL || `${basePath}/content.json`;
// 聊天機器人名稱
window.CHATBOT_NAME = window.CHATBOT_NAME || "學習筆記小幫手";
// 聊天機器人吉祥物圖示
window.CHATBOT_MASCOT_URL = window.CHATBOT_MASCOT_URL || `${basePath}/assets/images/chatbot-mascot.png`;
// 初始歡迎訊息
window.INITIAL_PROMPT = `嗨！我是 ${window.CHATBOT_NAME} 🕶️\n\n我可以幫你解答 Docker 與 Kubernetes 的問題，並提供相關文章連結。\n\n試試問我：\n- 如何安裝 Docker？\n- 什麼是 Kubernetes？\n- 如何建立 Private Registry？`;

// ====== 小工具：把 history 畫回畫面 ======
function rebuildChatFromHistory() {
    if (!chatMessages) return;
    chatMessages.innerHTML = "";
    chatHistory.forEach((turn) => {
        const sender = turn.role === "user" ? "user" : "bot";
        addMessage(sender, turn.parts[0].text, false);
    });
}

// 把歷史存到 sessionStorage
function saveHistory() {
    sessionStorage.setItem("geminiChatHistory", JSON.stringify(chatHistory));
}

// ====== UI：加上複製 code 按鈕 ======
function addCopyButtons(parentElement) {
    const codeBlocks = parentElement.querySelectorAll("pre");
    codeBlocks.forEach((block) => {
        const button = document.createElement("button");
        button.className = "copy-code-btn";
        button.textContent = "Copy";

        button.addEventListener("click", () => {
            const code = block.querySelector("code");
            if (navigator.clipboard && code) {
                navigator.clipboard.writeText(code.innerText).then(() => {
                    button.textContent = "Copied!";
                    setTimeout(() => {
                        button.textContent = "Copy";
                    }, 2000);
                });
            }
        });
        block.appendChild(button);
    });
}

// ====== 修正 AI 回應中的連結 ======
// 確保所有連結都有正確的 base URL
const BASE_URL = "https://caocharles.github.io/dcka-class-notes";

function fixBrokenLinks(text) {
    // 修正 Markdown 連結格式: [text](url)
    // 匹配所有 Markdown 連結
    return text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (match, linkText, url) => {
        // 如果已經是完整 URL，不處理
        if (url.startsWith('http://') || url.startsWith('https://')) {
            // 檢查是否是 github.io 但缺少 /dcka-class-notes/
            if (url.includes('github.io') && !url.includes('/dcka-class-notes/')) {
                // 修正: caocharles.github.io/lab05 -> caocharles.github.io/dcka-class-notes/lab05
                url = url.replace(/(caocharles\.github\.io)(\/)/i, '$1/dcka-class-notes/');
            }
            return `[${linkText}](${url})`;
        }

        // 如果是相對路徑（以 / 開頭但不是 /dcka-class-notes/）
        if (url.startsWith('/') && !url.startsWith('/dcka-class-notes/')) {
            return `[${linkText}](${BASE_URL}${url})`;
        }

        // 如果是不以 / 開頭的相對路徑
        if (!url.startsWith('/') && !url.startsWith('#')) {
            return `[${linkText}](${BASE_URL}/${url})`;
        }

        return match;
    });
}

// ====== 思考中動畫 ======
function showTyping() {
    if (!chatMessages || document.getElementById("typing-indicator")) return;
    const indicator = document.createElement("div");
    indicator.id = "typing-indicator";
    indicator.className = "typing-indicator";
    indicator.innerHTML = "<span></span><span></span><span></span>";
    chatMessages.appendChild(indicator);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function hideTyping() {
    document.getElementById("typing-indicator")?.remove();
}

// ====== 加一則訊息到畫面 & 歷史 ======
function addMessage(sender, text, addToHistory = true) {
    if (!chatMessages) return;

    const message = document.createElement("div");
    message.classList.add(sender === "user" ? "user-message" : "bot-message");

    // 機器人訊息用 marked 把 Markdown 轉成 HTML
    if (sender === "bot") {
        // 修正可能不完整的連結
        const fixedText = fixBrokenLinks(text);
        const html = window.marked ? marked.parse(fixedText) : fixedText;
        message.innerHTML = html;
        addCopyButtons(message);
    } else {
        message.textContent = text;
    }

    if (addToHistory) {
        chatHistory.push({
            role: sender === "user" ? "user" : "model",
            parts: [{ text }],
        });
        saveHistory();
    }

    chatMessages.appendChild(message);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// ====== 載入 content.json，組成 DOCUMENTATION 字串 ======
async function loadContent() {
    if (allDocsContent || isContentLoading) return;
    isContentLoading = true;

    const savedHistory = sessionStorage.getItem("geminiChatHistory");
    if (!savedHistory) {
        addMessage("bot", "正在載入教學文件，請稍候…", false);
    }

    try {
        const res = await fetch(window.ALL_CONTENT_URL);
        if (!res.ok) throw new Error("讀取 documentation 失敗");
        const data = await res.json();

        // 每頁 => Page / URL / Content
        allDocsContent = data
            .map(
                (doc) =>
                    `Page: ${doc.title}\nURL: ${doc.url}\nContent:\n${doc.content}`
            )
            .join("\n\n---\n\n");

        // 移除「正在載入」那行
        const loadingMessage = Array.from(chatMessages.children).find((child) =>
            child.textContent.includes("正在載入教學文件")
        );
        if (loadingMessage) loadingMessage.remove();

        if (!savedHistory && window.INITIAL_PROMPT) {
            addMessage("bot", window.INITIAL_PROMPT);
        }
    } catch (err) {
        console.error(err);
        addMessage("bot", "抱歉，讀取教學文件失敗，稍後再試看看。");
    } finally {
        isContentLoading = false;
    }
}

// ====== 清除歷史 ======
function clearHistory() {
    chatHistory = [];
    sessionStorage.removeItem("geminiChatHistory");
    chatMessages.innerHTML = "";
    if (window.INITIAL_PROMPT) {
        addMessage("bot", window.INITIAL_PROMPT);
    }
}

// ====== 核心：送出訊息，呼叫 FastAPI 後端 ======
async function sendMessage() {
    const messageText = chatInput.value.trim();
    if (messageText === "" || isContentLoading) return;

    addMessage("user", messageText);
    chatInput.value = "";

    if (!allDocsContent) {
        addMessage("bot", "教學文件還在載入中，請稍後再問一次。");
        return;
    }

    try {
        // System Instruction - 包含全站文件與回答規則
        const systemInstruction = `你是 DCKA 課程（Docker Containers 與 Kubernetes 系統管理）的 AI 助教。

## 回答規則
1. **語言**：使用繁體中文回答
2. **連結**：當提到相關主題時，**必須使用文件中的完整 URL**（不要自己組合路徑）
3. **格式**：使用清晰的 Markdown 格式（標題、列點、程式碼區塊）
4. **精準**：優先使用文件內容回答，如果沒有相關內容才用一般知識
5. **程式碼**：提供可執行的命令範例時，使用 \`\`\`bash 格式
6. **忽略特殊語法**：文件中的 icon 語法如 :octicons-arrow-right-24:、:fontawesome-brands-docker:、:material-kubernetes: 等請忽略，不要在回答中輸出這些語法

## 連結格式（重要）
每個文件都有 URL 欄位，請直接使用該 URL：
- 正確範例：[LAB 02 安裝 Docker](https://caocharles.github.io/dcka-class-notes/lab02_docker_install/)
- 正確範例：[疑難排解](https://caocharles.github.io/dcka-class-notes/appendix/troubleshooting/)
- 錯誤範例：[LAB 02](/lab02_docker_install/) ← 不要這樣寫
- 錯誤範例：:octicons-arrow-right-24: 開始學習 ← 不要輸出 icon 語法

## 課程文件
以下是完整的課程文件內容，請根據這些內容回答：

---
${allDocsContent}
---`;


        // 呼叫 FastAPI 後端
        showTyping();
        const response = await fetch(`${window.BACKEND_API_URL}/api/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                history: chatHistory.slice(0, -1), // 排除剛加入的使用者訊息
                message: messageText,
                system_instruction: systemInstruction,
            }),
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(`API 錯誤: ${errorData.detail || response.status}`);
        }

        const data = await response.json();
        const botResponse = data.text;
        addMessage("bot", botResponse);
    } catch (error) {
        console.error("API 呼叫錯誤:", error);
        addMessage("bot", `抱歉，發生錯誤：${error.message}\n\n請確認後端服務是否正常運作。`);
    } finally {
        hideTyping();
    }
}

// ====== 注入 HTML ======
function injectChatbotHTML() {
    if (document.getElementById('gemini-chatbot')) return;

    const chatbotHTML = `
    <button id="open-chat" aria-label="開啟 AI 助教聊天視窗">
      <img src="${window.CHATBOT_MASCOT_URL}" alt="">
    </button>
    <div id="gemini-chatbot">
      <div id="chat-header">
        <span class="chat-header-title">
          <span class="chat-avatar"><img src="${window.CHATBOT_MASCOT_URL}" alt=""></span>
          <span class="chat-title-text">
            <strong>${window.CHATBOT_NAME}</strong>
            <small>線上為你解答</small>
          </span>
        </span>
        <div class="header-buttons">
          <button id="clear-history-btn" title="清除歷史">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
              <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
            </svg>
          </button>
          <button id="toggle-fullscreen-btn" title="全螢幕">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
              <path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/>
            </svg>
          </button>
          <button id="close-chat" title="關閉">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
              <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
            </svg>
          </button>
        </div>
      </div>
      <div id="chat-messages"></div>
      <div id="chat-input-container">
        <input type="text" id="chat-input" placeholder="輸入問題..." autocomplete="off">
        <button id="send-chat">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
            <path fill="currentColor" d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
          </svg>
        </button>
      </div>
    </div>
  `;
    document.body.insertAdjacentHTML('beforeend', chatbotHTML);
}

// ====== 初始化：綁定 DOM & 事件 ======
function initChatbot() {
    // 注入 HTML
    injectChatbotHTML();

    // 取得 DOM 元素
    chatContainer = document.getElementById("gemini-chatbot");
    chatMessages = document.getElementById("chat-messages");
    chatInput = document.getElementById("chat-input");
    sendChatBtn = document.getElementById("send-chat");
    openChatBtn = document.getElementById("open-chat");
    closeChatBtn = document.getElementById("close-chat");
    toggleFullscreenBtn = document.getElementById("toggle-fullscreen-btn");
    clearHistoryBtn = document.getElementById("clear-history-btn");

    if (!chatContainer || !openChatBtn) {
        console.warn("找不到聊天元件 DOM 元素");
        return;
    }

    // 打開聊天室
    openChatBtn.addEventListener("click", () => {
        chatContainer.style.display = "flex";
        openChatBtn.style.display = "none";

        const savedHistory = sessionStorage.getItem("geminiChatHistory");
        if (savedHistory) {
            chatHistory = JSON.parse(savedHistory);
            rebuildChatFromHistory();
        }

        if (!allDocsContent) {
            loadContent();
        } else if (!savedHistory && window.INITIAL_PROMPT) {
            addMessage("bot", window.INITIAL_PROMPT);
        }
    });

    // 關閉聊天室
    if (closeChatBtn) {
        closeChatBtn.addEventListener("click", () => {
            chatContainer.style.display = "none";
            openChatBtn.style.display = "block";
        });
    }

    // 全螢幕
    if (toggleFullscreenBtn) {
        toggleFullscreenBtn.addEventListener("click", () => {
            chatContainer.classList.toggle("fullscreen");
        });
    }

    // 清除歷史
    if (clearHistoryBtn) {
        clearHistoryBtn.addEventListener("click", clearHistory);
    }

    // 送出訊息（按鈕）
    if (sendChatBtn) {
        sendChatBtn.addEventListener("click", sendMessage);
    }

    // 送出訊息（Enter）
    if (chatInput) {
        chatInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }

    // 確保按鈕可見
    if (openChatBtn) openChatBtn.style.display = 'block';
}

// ====== 啟動 ======
// Material for MkDocs 有 instant loading 時，用 document$
if (window.document$) {
    document$.subscribe(initChatbot);
} else if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initChatbot);
} else {
    initChatbot();
}
