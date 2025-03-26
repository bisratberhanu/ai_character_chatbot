// static/js/auth.js

document.addEventListener("DOMContentLoaded", function () {
  const signupBtn = document.getElementById("signup-btn");
  const loginBtn = document.getElementById("login-btn");
  const signupSection = document.getElementById("signup-section");
  const loginSection = document.getElementById("login-section");
  const signupForm = document.getElementById("signup-form");
  const loginForm = document.getElementById("login-form");

  signupBtn.addEventListener("click", function () {
    signupBtn.classList.add("active");
    loginBtn.classList.remove("active");
    signupSection.classList.remove("hidden");
    loginSection.classList.add("hidden");
  });

  loginBtn.addEventListener("click", function () {
    loginBtn.classList.add("active");
    signupBtn.classList.remove("active");
    loginSection.classList.remove("hidden");
    signupSection.classList.add("hidden");
  });

  signupForm.addEventListener("submit", function (e) {
    e.preventDefault();
    const username = document.getElementById("signup-username").value;
    const password = document.getElementById("signup-password").value;
    fetch("/signup/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: JSON.stringify({ username, password }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          window.location.href = "/";
        } else {
          alert("Signup error: " + data.error);
        }
      })
      .catch((error) => {
        console.error("Signup error:", error);
        alert("An error occurred during signup.");
      });
  });

  loginForm.addEventListener("submit", function (e) {
    e.preventDefault();
    const username = document.getElementById("login-username").value;
    const password = document.getElementById("login-password").value;
    fetch("/login/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: JSON.stringify({ username, password }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          window.location.href = "/";
        } else {
          alert("Login error: " + data.error);
        }
      })
      .catch((error) => {
        console.error("Login error:", error);
        alert("An error occurred during login.");
      });
  });

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
