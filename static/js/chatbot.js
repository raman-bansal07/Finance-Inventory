// Chatbot functionality
document.addEventListener("DOMContentLoaded", () => {
    // Create chatbot elements
    const chatbotContainer = document.createElement("div")
    chatbotContainer.className = "chatbot-container"
    chatbotContainer.innerHTML = `
          <div class="chatbot-button" id="chatbot-button">
              <i class="fas fa-comment"></i>
          </div>
          <div class="chatbot-popup" id="chatbot-popup">
              <div class="chatbot-header">
                  <div class="chatbot-title">
                      <i class="fas fa-robot"></i>
                      <span>Inventory Assistant</span>
                  </div>
                  <div class="chatbot-close" id="chatbot-close">
                      <i class="fas fa-times"></i>
                  </div>
              </div>
              <div class="chatbot-messages" id="chatbot-messages">
                  <!-- Messages will be added here dynamically -->
              </div>
              <div class="chatbot-input-container">
                  <input type="text" class="chatbot-input" id="chatbot-input" placeholder="Type your message...">
                  <button class="chatbot-send" id="chatbot-send">
                      <i class="fas fa-paper-plane"></i>
                  </button>
              </div>
          </div>
      `
  
    // Append to body
    document.body.appendChild(chatbotContainer)
  
    // Get elements
    const chatbotButton = document.getElementById("chatbot-button")
    const chatbotPopup = document.getElementById("chatbot-popup")
    const chatbotClose = document.getElementById("chatbot-close")
    const chatbotMessages = document.getElementById("chatbot-messages")
    const chatbotInput = document.getElementById("chatbot-input")
    const chatbotSend = document.getElementById("chatbot-send")
  
    // Toggle chatbot popup
    chatbotButton.addEventListener("click", () => {
      chatbotPopup.classList.toggle("active")
      if (chatbotPopup.classList.contains("active")) {
        chatbotInput.focus()
        if (chatbotMessages.children.length === 0) {
          // Add welcome message if this is the first time opening
          addBotMessage("Hello! I'm your inventory assistant. How can I help you today?")
        }
      }
    })
  
    // Close chatbot popup
    chatbotClose.addEventListener("click", () => {
      chatbotPopup.classList.remove("active")
    })
  
    // Send message on Enter key
    chatbotInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        sendMessage()
      }
    })
  
    // Send message on button click
    chatbotSend.addEventListener("click", sendMessage)
  
    function sendMessage() {
      const message = chatbotInput.value.trim()
      if (message === "") return
  
      // Add user message to chat
      addUserMessage(message)
      chatbotInput.value = ""
  
      // Show typing indicator
      showTypingIndicator()
  
      // Send message to backend
      fetch("/api/chatbot", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: message }),
      })
        .then((response) => response.json())
        .then((data) => {
          // Remove typing indicator
          hideTypingIndicator()
  
          // Add bot response to chat
          addBotMessage(data.response)
  
          // Scroll to bottom
          chatbotMessages.scrollTop = chatbotMessages.scrollHeight
        })
        .catch((error) => {
          console.error("Error:", error)
          hideTypingIndicator()
          addBotMessage("Sorry, I'm having trouble connecting. Please try again later.")
        })
    }
  
    function addUserMessage(message) {
      const messageElement = document.createElement("div")
      messageElement.className = "chatbot-message user-message"
      messageElement.innerHTML = `
              <div class="message-content">${escapeHtml(message)}</div>
          `
      chatbotMessages.appendChild(messageElement)
      chatbotMessages.scrollTop = chatbotMessages.scrollHeight
    }
  
    function addBotMessage(message) {
      const messageElement = document.createElement("div")
      messageElement.className = "chatbot-message bot-message"
      messageElement.innerHTML = `
              <div class="bot-avatar">
                  <i class="fas fa-robot"></i>
              </div>
              <div class="message-content">${message}</div>
          `
      chatbotMessages.appendChild(messageElement)
      chatbotMessages.scrollTop = chatbotMessages.scrollHeight
    }
  
    function showTypingIndicator() {
      const typingElement = document.createElement("div")
      typingElement.className = "chatbot-message bot-message typing-indicator"
      typingElement.id = "typing-indicator"
      typingElement.innerHTML = `
              <div class="bot-avatar">
                  <i class="fas fa-robot"></i>
              </div>
              <div class="message-content">
                  <div class="typing-dots">
                      <span></span>
                      <span></span>
                      <span></span>
                  </div>
              </div>
          `
      chatbotMessages.appendChild(typingElement)
      chatbotMessages.scrollTop = chatbotMessages.scrollHeight
    }
  
    function hideTypingIndicator() {
      const typingIndicator = document.getElementById("typing-indicator")
      if (typingIndicator) {
        typingIndicator.remove()
      }
    }
  
    // Helper function to escape HTML
    function escapeHtml(unsafe) {
      return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;")
    }
  })
  
  