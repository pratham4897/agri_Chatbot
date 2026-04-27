function sendMessage() {
    const inputField = document.getElementById("userInput");
    const message = inputField.value.trim();

    if (message === "") return;

    const chatbox = document.getElementById("chatbox");

    // Add user message
    chatbox.innerHTML += `
        <div class="user-message">
            <div class="bubble user">${message}</div>
        </div>
    `;

    chatbox.scrollTop = chatbox.scrollHeight;

    // Clear input field
    inputField.value = "";

    // Add typing indicator
    const typing = document.createElement("div");
    typing.className = "bot-message";
    typing.id = "typing";
    typing.innerHTML = `
        <div class="bubble bot">
            <span>🌾 Agri Doctor is typing...</span>
        </div>
    `;

    chatbox.appendChild(typing);
    chatbox.scrollTop = chatbox.scrollHeight;

    // Send message to server
    fetch("/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: message })
    })
    .then(res => {
        if (!res.ok) {
            throw new Error("Server responded with error");
        }
        return res.json();
    })
    .then(data => {
        // Remove typing indicator
        const typingIndicator = document.getElementById("typing");
        if (typingIndicator) typingIndicator.remove();

        // Add bot reply
        chatbox.innerHTML += `
            <div class="bot-message">
                <div class="bubble bot">${data.reply || "Sorry, I couldn't process that."}</div>
            </div>
        `;

        chatbox.scrollTop = chatbox.scrollHeight;
    })
    .catch(error => {
        console.error("Error:", error);

        // Remove typing indicator
        const typingIndicator = document.getElementById("typing");
        if (typingIndicator) typingIndicator.remove();

        // Show error message
        chatbox.innerHTML += `
            <div class="bot-message">
                <div class="bubble bot">⚠️ Server error. Please try again.</div>
            </div>
        `;

        chatbox.scrollTop = chatbox.scrollHeight;
    });
}

// ENTER KEY SUPPORT
document.getElementById("userInput").addEventListener("keypress", function(e) {
    if (e.key === "Enter") {
        e.preventDefault();        // Prevent default form submission (important!)
        sendMessage();
    }
});