const initChatbot = () => {
    // Prevent double initialization
    if (document.getElementById('gemini-chatbot')) return;

    const chatbotHTML = `
        <button id="open-chat">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="30" height="30"><path fill="currentColor" d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/></svg>
        </button>
        <div id="gemini-chatbot">
            <div id="chat-header">
                <span>AI Assistant</span>
                <div class="header-buttons">
                    <button id="clear-history-btn" title="Clear History">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M19.36 2.72l1.42 1.42-5.72 5.72 5.72 5.72-1.42 1.42-5.72-5.72-5.72 5.72-1.42-1.42 5.72-5.72-5.72-5.72 1.42-1.42 5.72 5.72 5.72-5.72z"/></svg>
                    </button>
                    <button id="toggle-fullscreen-btn" title="Toggle Fullscreen">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/></svg>
                    </button>
                    <button id="close-chat" title="Close">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
                    </button>
                </div>
            </div>
            <div id="chat-messages"></div>
            <div id="chat-input-container">
                <input type="text" id="chat-input" placeholder="Ask a question..." autocomplete="off">
                <button id="send-chat">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"><path fill="currentColor" d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
                </button>
            </div>
        </div>
        `;
    document.body.insertAdjacentHTML('beforeend', chatbotHTML);

    const chatbot = document.getElementById('gemini-chatbot');
    const openChatBtn = document.getElementById('open-chat');
    const closeChatBtn = document.getElementById('close-chat');
    const sendBtn = document.getElementById('send-chat');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');
    const fullscreenBtn = document.getElementById('toggle-fullscreen-btn');
    const clearHistoryBtn = document.getElementById('clear-history-btn');

    // Configuration
    // Railway production URL
    window.BACKEND_API_URL = window.BACKEND_API_URL || "https://dcka-class-notes-production.up.railway.app";
    window.INITIAL_PROMPT = "Hi! I'm your class AI assistant. Ask me anything about Docker or Kubernetes!";
    // In a real scenario, we might want to generate this JSON during build time or fetch sitemap.xml
    // For now, we assume search_index.json is available or we scan the page.
    // However, the original code fetched a custom JSON. Let's try to use MkDocs search index if possible or just page content?
    // The original code tried 'window.ALL_CONTENT_URL'.

    let allDocsContent = null;
    let isContentLoading = false;
    let chatHistory = [];

    function rebuildChatFromHistory() {
        chatMessages.innerHTML = '';
        chatHistory.forEach(turn => {
            const sender = turn.role === 'user' ? 'user' : 'bot';
            // Ensure compatibility with history format
            const text = turn.parts[0].text;
            addMessage(sender, text, false);
        });
    }

    function saveHistory() {
        sessionStorage.setItem('geminiChatHistory', JSON.stringify(chatHistory));
    }

    clearHistoryBtn.addEventListener('click', () => {
        chatHistory = [];
        sessionStorage.removeItem('geminiChatHistory');
        chatMessages.innerHTML = '';
        addMessage('bot', window.INITIAL_PROMPT);
    });

    fullscreenBtn.addEventListener('click', () => {
        chatbot.classList.toggle('fullscreen');
    });

    function addCopyButtons(parentElement) {
        const codeBlocks = parentElement.querySelectorAll('pre');
        codeBlocks.forEach(block => {
            const button = document.createElement('button');
            button.className = 'copy-code-btn';
            button.textContent = 'Copy';

            button.addEventListener('click', () => {
                const code = block.querySelector('code');
                if (navigator.clipboard && code) {
                    navigator.clipboard.writeText(code.innerText).then(() => {
                        button.textContent = 'Copied!';
                        setTimeout(() => { button.textContent = 'Copy'; }, 2000);
                    });
                }
            });
            block.appendChild(button);
        });
    }

    function addMessage(sender, text, addToHistory = true) {
        const message = document.createElement('div');
        message.classList.add(sender === 'user' ? 'user-message' : 'bot-message');

        // Use marked.js if available, otherwise just text
        // Note: You need to include marked.js in mkdocs.yml extra_javascript if you want markdown rendering
        const processedText = (sender === 'bot' && typeof marked !== 'undefined') ? marked.parse(text) : text;

        if (sender === 'bot') {
            message.innerHTML = processedText;
            addCopyButtons(message);
        } else {
            message.textContent = text;
        }

        if (addToHistory) {
            chatHistory.push({ role: (sender === 'user' ? 'user' : 'model'), parts: [{ text: text }] });
            saveHistory();
        }

        chatMessages.appendChild(message);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Function to scrape current page content for basic context if full docs not loaded
    function getPageContent() {
        const mainContent = document.querySelector('.md-content');
        return mainContent ? mainContent.innerText : '';
    }

    openChatBtn.addEventListener('click', () => {
        chatbot.style.display = 'flex';
        openChatBtn.style.display = 'none';

        const savedHistory = sessionStorage.getItem('geminiChatHistory');
        if (savedHistory) {
            chatHistory = JSON.parse(savedHistory);
            rebuildChatFromHistory();
        } else {
            // Only show initial prompt if empty
            if (chatMessages.children.length === 0) {
                addMessage('bot', window.INITIAL_PROMPT);
            }
        }
    });

    closeChatBtn.addEventListener('click', () => {
        chatbot.style.display = 'none';
        openChatBtn.style.display = 'block';
    });

    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });


    async function sendMessage() {
        const messageText = chatInput.value.trim();
        if (messageText === '' || isContentLoading) return;

        chatInput.value = ''; // Clear early
        addMessage('user', messageText);

        // Basic RAG Context Construction (Client-side)
        // We grab the text of the current page to give some context.
        // For full site search, we'd need a more complex solution (e.g. vector DB on backend or loading search_index.json)
        const pageContext = getPageContent();
        const currentUrl = window.location.href;
        const baseUrl = 'https://caocharles.github.io/dcka-class-notes/';

        const systemInstruction = `你是 Docker 與 Kubernetes 課程的助教。請用繁體中文回答。

## 課程文章連結
當使用者詢問相關主題時，請推薦適合的文章連結：

### Docker 基礎 (LAB 01-08)
- [LAB 01 環境初始化](${baseUrl}lab01_environment_setup/) - VMware 安裝、虛擬機設定
- [LAB 02 安裝 Docker](${baseUrl}lab02_docker_install/) - Docker CE 安裝步驟
- [LAB 03 安裝 Podman](${baseUrl}lab03_podman/) - Podman 替代方案
- [LAB 04 Docker Hub Rate Limit](${baseUrl}lab04_docker_hub_rate_limit/) - 下載限制說明
- [LAB 05 Private Registry](${baseUrl}lab05_private_registry/) - 私有倉庫建置
- [LAB 06 Docker 基本操作](${baseUrl}lab06_docker_basics/) - 容器操作指令
- [LAB 07 Persistent Storage](${baseUrl}lab07_persistent_storage/) - 資料持久化
- [LAB 08 WordPress](${baseUrl}lab08_wordpress/) - WordPress 部署

### Docker 進階 (LAB 09-10)
- [LAB 09 Docker Commit](${baseUrl}lab09_commit/) - 客製化映像檔
- [LAB 10 Dockerfile](${baseUrl}lab10_dockerfile/) - Dockerfile 撰寫

### Kubernetes 基礎 (LAB 11-15)
- [LAB 11 Standalone K8s](${baseUrl}lab11_standalone_k8s/) - 單節點 K8s 安裝
- [LAB 12 K8s 叢集安裝](${baseUrl}lab12_k8s_install/) - 多節點叢集建置
- [LAB 13 K8s 常用指令](${baseUrl}lab13_k8s_commands/) - kubectl 指令
- [LAB 14 Namespace 與 Rolling Update](${baseUrl}lab14_namespace_rolling/) - 命名空間與滾動更新
- [LAB 15 Service](${baseUrl}lab15_service/) - 服務負載均衡

### Kubernetes 進階 (LAB 16-20)
- [LAB 16 PV/PVC](${baseUrl}lab16_pv_pvc/) - 儲存管理
- [LAB 17 Secret](${baseUrl}lab17_secret/) - 密鑰管理
- [LAB 18 RBAC](${baseUrl}lab18_rbac_event_log/) - 權限控制
- [LAB 19 K8s WordPress](${baseUrl}lab19_k8s_wordpress_mysql/) - K8s 部署 WordPress
- [LAB 20 Dashboard](${baseUrl}lab20_dashboard/) - K8s 圖形介面

### 附錄
- [Docker 指令速查](${baseUrl}appendix/docker_cheatsheet/) - Docker 常用指令
- [K8s 指令速查](${baseUrl}appendix/k8s_cheatsheet/) - kubectl 常用指令
- [疑難排解](${baseUrl}appendix/troubleshooting/) - 常見問題解決

## 當前頁面
使用者目前在：${currentUrl}

## 當前頁面內容
${pageContext}

## 回答規則
1. 使用繁體中文回答
2. 當提到相關主題時，提供上述文章的 Markdown 連結
3. 如果問題與當前頁面相關，優先使用頁面內容回答
4. 使用清晰的格式：標題、列點、程式碼區塊等
5. 回答結尾可以推薦 1-2 篇相關文章供延伸閱讀`;

        try {
            // Call our Backend Proxy
            const response = await fetch(`${window.BACKEND_API_URL}/api/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    history: chatHistory, // Send full history
                    message: messageText,
                    system_instruction: systemInstruction
                }),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: response.statusText }));
                throw new Error(`Server error: ${errorData.detail}`);
            }

            const data = await response.json();
            const botResponse = data.text;
            addMessage('bot', botResponse);

        } catch (error) {
            console.error('Error fetching from Backend:', error);
            addMessage('bot', `Sorry, I encountered an error connecting to the server: ${error.message}. Please check if the backend is running.`);
        }
    }

    // Ensure button is visible
    if (openChatBtn) openChatBtn.style.display = 'block';
};


// Robust loading
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initChatbot);
} else {
    initChatbot();
}

