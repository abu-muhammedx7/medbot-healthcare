document.addEventListener("DOMContentLoaded", () => {
    const chatBox = document.getElementById("chatBox");
    const userInput = document.getElementById("userInput");
    const sendBtn = document.getElementById("sendBtn");
    const newChatBtn = document.querySelector(".new-chat-btn");
    const quickOptions = document.querySelectorAll(".quick-option");
    const welcomeMessage = document.querySelector(".welcome-message");

    // Initialize with welcome message
    let isFirstMessage = true;

    // Quick question buttons
    quickOptions.forEach(option => {
        option.addEventListener("click", () => {
            userInput.value = option.textContent;
            sendMessage();
        });
    });

    // New chat button
    newChatBtn.addEventListener("click", () => {
        if (confirm("Start a new chat? Your current conversation will be cleared.")) {
            chatBox.innerHTML = '';
            addMessage("Hello! I'm MediAI. How can I assist you with medical questions today?", "bot");
            isFirstMessage = false;
        }
    });

    function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;

        // Remove welcome message on first user input
        if (isFirstMessage) {
            welcomeMessage.remove();
            isFirstMessage = false;
        }

        // Add user message
        addMessage(message, "user");
        userInput.value = "";

        // Show typing indicator
        const typingIndicator = addTypingIndicator();

        // Get AI response
        fetch("/ask", {
            method: "POST",
            headers: { 
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            body: JSON.stringify({ query: message })
        })
        .then(async response => {
            chatBox.removeChild(typingIndicator);
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || "Request failed");
            }
            
            return response.json();
        })
        .then(data => {
            if (data.error) {
                addMessage(`Error: ${data.error}`, "bot");
            } else {
                addMessage(data.response, "bot");
            }
        })
        .catch(error => {
            chatBox.removeChild(typingIndicator);
            addMessage(`Error: ${error.message}`, "bot");
        });
    }

    function addMessage(text, sender) {
        const msgDiv = document.createElement("div");
        msgDiv.className = `message ${sender}`;

        const avatar = document.createElement("div");
        avatar.className = "avatar";
        avatar.textContent = sender === "bot" ? "MA" : "You";

        const content = document.createElement("div");
        content.className = "content";
        content.textContent = text;

        msgDiv.appendChild(avatar);
        msgDiv.appendChild(content);
        chatBox.appendChild(msgDiv);

        // Auto-scroll to bottom
        chatBox.scrollTop = chatBox.scrollHeight;
        return msgDiv;
    }

    function addTypingIndicator() {
        const typingDiv = document.createElement("div");
        typingDiv.className = "message bot typing";

        const avatar = document.createElement("div");
        avatar.className = "avatar";
        avatar.textContent = "MA";

        const content = document.createElement("div");
        content.className = "content";
        content.textContent = "MediAI is thinking...";

        typingDiv.appendChild(avatar);
        typingDiv.appendChild(content);
        chatBox.appendChild(typingDiv);

        // Auto-scroll
        chatBox.scrollTop = chatBox.scrollHeight;
        return typingDiv;
    }

    // Event listeners
    sendBtn.addEventListener("click", sendMessage);
    userInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") sendMessage();
    });

    // Add initial welcome message
    addMessage("Hello! I'm MediAI. How can I assist you with medical questions today?", "bot");
});