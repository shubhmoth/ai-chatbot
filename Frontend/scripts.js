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

async function fetchAccountData(accountId) {
    // Prepare the request data
    const data = {
      account_id: accountId,
    };
    // Set content type header to application/json
    const headers = new Headers({
      'Content-Type': 'application/json'
    });
    try {
      // Make the POST request
      const response = await fetch('http://127.0.0.1:5000/fetch-account-data', {
        method: 'POST',
        headers,
        body: JSON.stringify(data),
      });
      // Check for successful response
      if (!response.ok) {
        throw new Error(`API request failed with status: ${response.status}`);
      }
      // Parse the response data
      const jsonData = await response.json();
      // Handle the response data
      console.log("Response:", jsonData);
      // Access specific data like file_name or message
      const fileName = jsonData.file_name;
      const message = jsonData.message;
  
      console.log("File Name:", fileName);
      console.log("Message:", message);
  
      // You can further process the data (e.g., display it on the page) here
    } catch (error) {
      console.error("Error fetching account data:", error);
    }
}

// Fetch response from the backend
async function getBotResponse(userInput) {
    const accountId = 10;
    fetchAccountData(accountId);

    // const response = await fetch('http://localhost:5000/api/chat', { // Update the URL if needed
    //     method: 'POST',
    //     headers: {
    //         'Content-Type': 'application/json'
    //     },
    //     body: JSON.stringify({ query: userInput })
    // });

    // const data = await response.json();
    // console.log('Bot Response:', data);
    // return data.reply; // Extract the response
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
