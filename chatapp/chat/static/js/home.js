// static/js/home.js

document.addEventListener("DOMContentLoaded", function () {
  const buttons = document.querySelectorAll(".option-btn");

  buttons.forEach((button) => {
    button.addEventListener("click", function (e) {
      // Add a brief click animation
      button.style.transform = "scale(0.95)";
      setTimeout(() => {
        button.style.transform = "scale(1)";
      }, 100);
    });
  });
});


