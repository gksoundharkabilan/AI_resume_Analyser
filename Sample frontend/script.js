// Mobile Menu
const toggle = document.querySelector(".menu-toggle");
const navLinks = document.querySelector(".nav-links");

toggle.addEventListener("click", () => {
  navLinks.classList.toggle("active");
});

// Smooth scroll
function scrollToUpload() {
  document.getElementById("upload").scrollIntoView({
    behavior: "smooth"
  });
}

// Drag & Drop Upload
const dropArea = document.getElementById("drop-area");
const fileInput = document.getElementById("fileInput");
const fileName = document.getElementById("file-name");

dropArea.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropArea.classList.add("dragover");
});

dropArea.addEventListener("dragleave", () => {
  dropArea.classList.remove("dragover");
});

dropArea.addEventListener("drop", (e) => {
  e.preventDefault();
  dropArea.classList.remove("dragover");
  fileName.textContent = e.dataTransfer.files[0].name;
});

fileInput.addEventListener("change", () => {
  fileName.textContent = fileInput.files[0].name;
});

// Counter Animation
const counters = document.querySelectorAll(".counter");

counters.forEach(counter => {
  const updateCount = () => {
    const target = +counter.getAttribute("data-target");
    const count = +counter.innerText;
    const increment = target / 200;

    if (count < target) {
      counter.innerText = Math.ceil(count + increment);
      setTimeout(updateCount, 10);
    } else {
      counter.innerText = target;
    }
  };
  updateCount();
});
