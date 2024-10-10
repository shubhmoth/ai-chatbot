// Toggle the visibility of the chatbox
function toggleChat() {
    console.log("clicked");
    const chatBox = document.getElementById("chat-box");

    // Check if the chat box is currently hidden or not, and toggle the classes for animation
    if (chatBox.classList.contains("hide")) {
        chatBox.classList.remove("hide");
        chatBox.classList.add("show");
    } else {
        chatBox.classList.remove("show");
        chatBox.classList.add("hide");
    }
}


// Fetch response from the backend
async function getBotResponse(userInput) {
    const response = await fetch('http://localhost:5000/api/chat', { // Update the URL if needed
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query: userInput })
    });

    const data = await response.json();
    console.log('Bot Response:', data);
    return data.reply; // Extract the response
}


// Handle user queries and display results
async function handleQuery(userInput) {
    // Show loader
    document.getElementById("loader").style.display = "block";

    const botReply = await getBotResponse(userInput);
    displayBotReply(botReply);

    // Hide loader
    document.getElementById("loader").style.display = "none";
}

function displayBotReply(reply) {
    const chatMessages = document.getElementById("chat-messages");
    const messageElement = document.createElement('div');
    messageElement.innerHTML = `<strong>Bot:</strong> ${reply}`;
    chatMessages.appendChild(messageElement);
    messageElement.scrollIntoView({ behavior: 'smooth' });
}

async function sendMessage() {
    const userInput = document.getElementById("user-input").value;
    const chatMessages = document.getElementById("chat-messages");

    // Display the user's message in the chat
    chatMessages.innerHTML += `<div><strong>You:</strong> ${userInput}</div>`;

    // Clear input field
    document.getElementById("user-input").value = "";

    // Scroll to the bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Handle the user's query
    await handleQuery(userInput);
}

// Allow sending messages with the Enter key
document.getElementById("user-input").addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});
