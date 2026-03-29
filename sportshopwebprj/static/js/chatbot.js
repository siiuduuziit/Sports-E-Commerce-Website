const chatIcon = document.getElementById("chat-icon");
const chatBox = document.getElementById("chat-box");
const closeChat = document.getElementById("close-chat");
const sendBtn = document.getElementById("send-btn");
const input = document.getElementById("chat-input");
const messages = document.getElementById("chat-messages");

/* ================= HELPER ================= */

// Lấy lời chào theo giờ Việt Nam
function getVietnamGreeting() {
  const now = new Date();
  const vietnamHour = new Date(
    now.toLocaleString("en-US", { timeZone: "Asia/Ho_Chi_Minh" })
  ).getHours();

  if (vietnamHour >= 5 && vietnamHour < 11) {
    return "Chào buổi sáng ☀️";
  } else if (vietnamHour >= 11 && vietnamHour < 18) {
    return "Chào buổi chiều 🌤️";
  } else {
    return "Chào buổi tối 🌙";
  }
}

// Render text bot
function renderBotText(text) {
  const html = `<div class="msg bot">${text}</div>`;
  messages.insertAdjacentHTML("beforeend", html);
}

// Render product card
function renderProduct(product) {
  const html = `
    <div class="msg bot">
      <div class="chat-product">
        <img src="${product.image}" alt="${product.title}">
        <div class="chat-product-info">
          <a href="${product.url}" target="_blank">${product.title}</a>
        </div>
      </div>
    </div>
  `;
  messages.insertAdjacentHTML("beforeend", html);
}

/* ================= CHAT OPEN / CLOSE (MƯỢT) ================= */

chatIcon.onclick = () => {
  chatBox.classList.toggle("show");

  // 👋 Chỉ chào khi vừa mở chat
  if (
    chatBox.classList.contains("show") &&
    !sessionStorage.getItem("chatbot_greeted")
  ) {
    const greeting = getVietnamGreeting();

    renderBotText(`${greeting}! 👋`);
    renderBotText("Mình là trợ lý bán hàng của shop 👟");
    renderBotText(
      "Bạn có thể hỏi mình về giá, tình trạng còn hàng hoặc xem các mẫu giày và đồ của shop nha!"
    );

    sessionStorage.setItem("chatbot_greeted", "true");

    setTimeout(() => {
      messages.scrollTop = messages.scrollHeight;
    }, 100);
  }
};

closeChat.onclick = () => {
  chatBox.classList.remove("show");
};

/* ================= SEND MESSAGE ================= */

sendBtn.onclick = sendMessage;

// Gửi khi nhấn Enter
input.addEventListener("keypress", function (e) {
  if (e.key === "Enter") {
    sendMessage();
  }
});

function sendMessage() {
  const text = input.value.trim();
  if (!text) return;

  // Render user message
  messages.insertAdjacentHTML(
    "beforeend",
    `<div class="msg user">${text}</div>`
  );
  input.value = "";
  messages.scrollTop = messages.scrollHeight;

  fetch("/chatbot/", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: `message=${encodeURIComponent(text)}`,
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.type === "text") {
        renderBotText(data.data);
      } 
      else if (data.type === "product") {
        renderProduct(data.data);
        if (data.message) renderBotText(data.message);
      } 
      else if (data.type === "products") {
        data.data.forEach((p) => renderProduct(p));
        if (data.message) renderBotText(data.message);
      } 
      else {
        renderBotText("🤖 Mình chưa hiểu lắm, bạn nói rõ hơn giúp mình nha!");
      }

      messages.scrollTop = messages.scrollHeight;
    })
    .catch(() => {
      renderBotText("⚠️ Có lỗi xảy ra, bạn thử lại giúp mình nha!");
    });
}
