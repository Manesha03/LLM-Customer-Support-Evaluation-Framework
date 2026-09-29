const chatLog = document.querySelector("#chatLog");
const chatForm = document.querySelector("#chatForm");
const messageInput = document.querySelector("#messageInput");
const sendButton = chatForm.querySelector("button");
const quickButtons = document.querySelectorAll("[data-prompt]");

function addMessage(role, text) {
  const article = document.createElement("article");
  article.className = `message ${role}`;

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = role === "user" ? "U" : "S";

  const bubble = document.createElement("p");
  bubble.textContent = text;

  article.append(avatar, bubble);
  chatLog.append(article);
  chatLog.scrollTop = chatLog.scrollHeight;
  return article;
}

async function sendMessage(message) {
  addMessage("user", message);
  const pending = addMessage("bot", "One moment, I am checking the best next step...");
  sendButton.disabled = true;

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    const data = await response.json();
    pending.querySelector("p").textContent = data.response || data.error || "Something went wrong.";
  } catch (error) {
    pending.querySelector("p").textContent = "I could not reach the chatbot service. Please try again.";
  } finally {
    sendButton.disabled = false;
    messageInput.focus();
  }
}

chatForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const message = messageInput.value.trim();
  if (!message) return;
  messageInput.value = "";
  sendMessage(message);
});

messageInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    chatForm.requestSubmit();
  }
});

quickButtons.forEach((button) => {
  button.addEventListener("click", () => {
    sendMessage(button.dataset.prompt);
  });
});
