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
  let userName = localStorage.getItem("user_name");

  if (!userName) {
    userName = prompt("Please enter your name to start chatting:");
    if (!userName) {
      alert("A name is required to proceed.");
      return;
    }
    localStorage.setItem("user_name", userName);
  }

  // Fetch existing characters
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
        user_id: userName,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          appendMessage(userName, message);
          appendMessage(characterNameSpan.textContent, data.response);
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

  function appendMessage(sender, text) {
    const p = document.createElement("p");
    p.textContent = `${sender}: ${text}`;
    chatMessages.appendChild(p);
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

  // Add button click animation
  const sendButton = chatForm.querySelector(".btn");
  sendButton.addEventListener("click", function (e) {
    sendButton.style.transform = "scale(0.95)";
    setTimeout(() => {
      sendButton.style.transform = "scale(1)";
    }, 100);
  });
});
