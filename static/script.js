
document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const chatContainer = document.getElementById('chat-container');
    const promptInput = document.querySelector('input[name="prompt"]');
    const logoutButton = document.querySelector('a[href="/logout"]');

    const username = document.body.dataset.username;
    const CACHE_KEY = `chatHistory_${username}`;

    const getChatHistoryFromCache = () => {
        const cachedData = localStorage.getItem(CACHE_KEY);
        if (cachedData) {
            const { chatHistory } = JSON.parse(cachedData);
            return chatHistory;
        }
        return null;
    };

    const saveChatHistoryToCache = (chatHistory) => {
        const dataToCache = {
            timestamp: Date.now(),
            chatHistory: chatHistory,
        };
        localStorage.setItem(CACHE_KEY, JSON.stringify(dataToCache));
    };

    const clearChatHistoryFromCache = () => {
        localStorage.removeItem(CACHE_KEY);
    };

    const appendMessage = (content, role) => {
        const messageDiv = document.createElement('div');
        if (role === 'user') {
            messageDiv.className = 'max-w-[70%] ml-auto px-5 py-3 leading-6 bg-inputDark rounded-2xl mb-4 border border-inputBorder shadow-md text-textLight';
            messageDiv.textContent = content;
        } else {
            messageDiv.className = 'px-5 py-3 leading-6 mb-4 bg-gradient-to-r from-primary/10 to-secondary/10 rounded-2xl border border-inputBorder shadow text-textLight';
            messageDiv.innerHTML = content;
        }
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;

        const chatHistory = getChatHistoryFromCache() || [];
        chatHistory.push({ role, content });
        saveChatHistoryToCache(chatHistory);
    };

    const loadChatHistory = async () => {
        const cachedHistory = getChatHistoryFromCache();
        if (cachedHistory) {
            console.log('Loading chat history from cache');
            cachedHistory.forEach(chat => {
                const messageDiv = document.createElement('div');
                if (chat.role === 'user') {
                    messageDiv.className = 'max-w-[70%] ml-auto px-5 py-3 leading-6 bg-inputDark rounded-2xl mb-4 border border-inputBorder shadow-md text-textLight';
                    messageDiv.textContent = chat.content;
                } else {
                    messageDiv.className = 'px-5 py-3 leading-6 mb-4 bg-gradient-to-r from-primary/10 to-secondary/10 rounded-2xl border border-inputBorder shadow text-textLight';
                    messageDiv.innerHTML = chat.content;
                }
                chatContainer.appendChild(messageDiv);
            });
            chatContainer.scrollTop = chatContainer.scrollHeight;
        } else {
            console.log('Fetching chat history from server');
            try {
                const response = await fetch('/get_chat_history');
                if (response.ok) {
                    const chatHistory = await response.json();
                    chatHistory.forEach(chat => {
                        appendMessage(chat.content, chat.role);
                    });
                    saveChatHistoryToCache(chatHistory);
                }
            } catch (error) {
                console.error('Error fetching chat history:', error);
            }
        }
    };

    function getExactResponse(userInput) {
        const chatHistory = getChatHistoryFromCache();
        console.log("type of chatHistory: ",typeof chatHistory);
        console.log("chatHistory: ",chatHistory);
        if (!chatHistory) return null;
        for (let i = 0; i < chatHistory.length; i++) {
            if (chatHistory[i].role === 'user' ) {
                if (chatHistory[i].content.toLowerCase().trim() === userInput.toLowerCase().trim()) {
                    if (i + 1 < chatHistory.length && chatHistory[i + 1].role === 'bot') {
                        return chatHistory[i + 1].content;
                    }
                }
            }
        }
        return null;
    }
    loadChatHistory();

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(chatForm);
        const userMessage = formData.get('prompt');
        const file = formData.get('file');
        console.log("file: ",file);
        if(file.name!=""){
            appendMessage(`${userMessage}. file: ${file.name}`, 'user');
        }
        else{
            appendMessage(userMessage, 'user');
        }
        console.log('formData:', formData);
        promptInput.value = '';

        const response = getExactResponse(userMessage);
        if(response){
            console.log('Found exact match in local storage');
            appendMessage(response, 'bot');
        }
        else{
            console.log('No exact match found, sending to server');
            try {
                const response = await fetch('/send_message', {
                    method: 'POST',
                    body: formData,
                });

                if (response.ok) {
                    const data = await response.json();
                    appendMessage(data.bot_response, 'bot');
                } else {
                    console.error('Error sending message:', response.statusText);
                    appendMessage('Sorry, something went wrong. Please try again.', 'bot');
                }
            } catch (error){
                console.error('Error:', error);
                appendMessage('Sorry, there was a network error. Please try again.', 'bot');
            }
        }
    });

    logoutButton.addEventListener('click', (e) => {
        e.preventDefault();
        clearChatHistoryFromCache();
        window.location.href = '/logout';
    });
});
