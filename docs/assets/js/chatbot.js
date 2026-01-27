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

        const systemInstruction = `You are a helpful teaching assistant for a Docker and Kubernetes course.
        
CURRENT PAGE CONTEXT:
${pageContext}

Answer the user's question based on the context if possible. If not, use your general knowledge but mention you are going beyond the page context.`;

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

