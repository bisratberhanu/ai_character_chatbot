// static/js/existing_characters.js

document.addEventListener("DOMContentLoaded", function () {
  const charactersSection = document.getElementById("characters-section");
  const charactersList = document.getElementById("characters-list");
  const chatSection = document.getElementById("chat-section");
  const characterNameSpan = document.getElementById("character-name");
  const chatMessages = document.getElementById("chat-messages");
  const chatForm = document.getElementById("chat-form");
  const messageInput = document.getElementById("message-input");
  const angerSpan = document.getElementById("anger");
  const sadnessSpan = document.getElementById("sadness");
  const prideSpan = document.getElementById("pride");
  const joySpan = document.getElementById("joy");
  const blissSpan = document.getElementById("bliss");

  let selectedCharacterId = null;

  fetch("/api/clear_session/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify({}),
  })
    .then((response) => response.json())
    .then((data) => {
      if (!data.success) {
        console.error("Failed to clear session:", data.error);
      }
    })
    .catch((error) => {
      console.error("Error clearing session:", error);
    });

  fetch("/api/characters/")
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        charactersList.innerHTML = "";
        data.characters.forEach((char) => {
          const li = document.createElement("li");
          li.textContent = `${char.name} from ${char.book__title}`;
          li.addEventListener("click", () =>
            selectCharacter(char.id, char.name)
          );
          charactersList.appendChild(li);
        });
      } else {
        charactersList.innerHTML = "<li>No characters available.</li>";
      }
    })
    .catch((error) => {
      console.error("Fetch error:", error);
      charactersList.innerHTML = "<li>Error loading characters.</li>";
    });

  function selectCharacter(id, name) {
    selectedCharacterId = id;
    characterNameSpan.textContent = name;
    chatMessages.innerHTML = "";
    angerSpan.textContent = 1;
    sadnessSpan.textContent = 1;
    prideSpan.textContent = 1;
    joySpan.textContent = 1;
    blissSpan.textContent = 1;
    chatSection.classList.remove("hidden");
    charactersSection.classList.add("hidden");
  }

  chatForm.addEventListener("submit", function (e) {
    e.preventDefault();
    const message = messageInput.value.trim();
    if (!message) return;
    sendMessage(message);
    messageInput.value = "";
  });

  function sendMessage(message) {
    fetch("/api/chat/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: JSON.stringify({
        character_id: selectedCharacterId,
        message: message,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          appendMessage("You", message, true);
          appendMessage(characterNameSpan.textContent, data.response, false);
          updateEmotions(data.emotions);
        } else {
          alert("Chat error: " + data.error);
        }
      })
      .catch((error) => {
        console.error("Chat error:", error);
        alert("An error occurred while chatting.");
      });
  }

  function appendMessage(sender, text, isUser) {
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${isUser ? "user" : ""}`;

    const senderSpan = document.createElement("span");
    senderSpan.className = "sender";
    senderSpan.textContent = `${sender}:`;

    const textSpan = document.createElement("span");
    textSpan.className = "text";
    textSpan.textContent = text;

    messageDiv.appendChild(senderSpan);
    messageDiv.appendChild(textSpan);
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function updateEmotions(emotions) {
    angerSpan.textContent = emotions.Anger;
    sadnessSpan.textContent = emotions.Sadness;
    prideSpan.textContent = emotions.Pride;
    joySpan.textContent = emotions.Joy;
    blissSpan.textContent = emotions.Bliss;
  }

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === name + "=") {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  const sendButton = chatForm.querySelector(".btn");
  sendButton.addEventListener("click", function (e) {
    sendButton.style.transform = "scale(0.95)";
    setTimeout(() => {
      sendButton.style.transform = "scale(1)";
    }, 100);
  });
});
