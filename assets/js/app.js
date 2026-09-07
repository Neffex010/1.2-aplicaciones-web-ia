const API_URL =
   "https://TU-PROYECTO.vercel.app/api/chat";

const form = document.getElementById("chatForm");
const input = document.getElementById("messageInput");
const messages = document.getElementById("messages");
const sendButton = document.getElementById("sendButton");

function addMessage(text, type) {
   const container = document.createElement("div");
   container.classList.add("message", type);

   const label = document.createElement("div");
   label.classList.add("message-label");
   label.textContent = type === "user" ? "Tú" : "IA";

   const content = document.createElement("div");
   content.classList.add("message-content");
   content.textContent = text;

   container.appendChild(label);
   container.appendChild(content);
   messages.appendChild(container);

   messages.scrollTop = messages.scrollHeight;

   return container;
}

form.addEventListener("submit", async (event) => {
   event.preventDefault();

   const message = input.value.trim();

   if (!message) {
       return;
   }

   addMessage(message, "user");

   input.value = "";
   input.disabled = true;
   sendButton.disabled = true;

   const loading = addMessage("Pensando...", "loading");

   try {
       const response = await fetch(API_URL, {
           method: "POST",
           headers: {
               "Content-Type": "application/json"
           },
           body: JSON.stringify({
               message: message
           })
       });

       const data = await response.json();

       loading.remove();

       if (!response.ok) {
           throw new Error(
               data.error || "Error del servidor"
           );
       }

       addMessage(data.reply, "assistant");
   }
   catch (error) {
       loading.remove();

       addMessage(
           "Error: " + error.message,
           "assistant"
       );
   }
   finally {
       input.disabled = false;
       sendButton.disabled = false;
       input.focus();
   }
});