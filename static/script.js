
document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const chatContainer = document.getElementById('chat-container');
    const promptInput = document.querySelector('input[name="prompt"]');

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(chatForm);
        const userMessage = formData.get('prompt');

        appendMessage(userMessage, 'user');
        promptInput.value = '';

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
        } catch (error) {
            console.error('Error:', error);
            appendMessage('Sorry, there was a network error. Please try again.', 'bot');
        }
    });

    function appendMessage(content, role) {
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
    }
});
