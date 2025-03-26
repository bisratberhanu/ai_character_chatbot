// static/js/script.js

document.addEventListener("DOMContentLoaded", function () {
  const uploadForm = document.getElementById("upload-form");
  const charactersSection = document.getElementById("characters-section");
  const charactersList = document.getElementById("characters-list");
  const chatSection = document.getElementById("chat-section");
  const characterNameSpan = document.getElementById("character-name");
  const chatMessages = document.getElementById("chat-messages");
  const chatForm = document.getElementById("chat-form");
  const messageInput = document.getElementById("message-input");
  const uploadSection = document.getElementById("upload-section");
  const angerSpan = document.getElementById("anger");
  const sadnessSpan = document.getElementById("sadness");
  const prideSpan = document.getElementById("pride");
  const joySpan = document.getElementById("joy");
  const blissSpan = document.getElementById("bliss");

  let selectedCharacterId = null;

  uploadForm.addEventListener("submit", function (e) {
    e.preventDefault();
    const formData = new FormData(uploadForm);
    fetch("/api/upload_book/", {
      method: "POST",
      body: formData,
      headers: { "X-CSRFToken": getCookie("csrftoken") },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          charactersList.innerHTML = "";
          data.characters.forEach((char) => {
            const li = document.createElement("li");
            li.textContent = char.name;
            li.addEventListener("click", () =>
              selectCharacter(char.id, char.name)
            );
            charactersList.appendChild(li);
          });
          charactersSection.classList.remove("hidden");
          uploadSection.classList.add("hidden");
        } else {
          if (data.error.includes("already registered")) {
            alert(`${data.error} Click OK to go to the List Characters page.`);
            window.location.href = "/from_other_users_characters/";
          } else {
            alert("Error: " + data.error);
          }
        }
      })
      .catch((error) => {
        console.error("Upload error:", error);
        alert("An error occurred while uploading the book.");
      });
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
          appendMessage("You", message);
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
});
