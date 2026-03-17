function addMessage(text, type) {
    const chatBox = document.getElementById("chat-box");

    const msg = document.createElement("div");
    msg.className = "message " + type;
    msg.innerText = text;

    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
}


function botReply(input) {
    input = input.toLowerCase();

    if (input.includes("hello")) return "Hello! 👋";
    if (input.includes("name")) return "I am Kavix AI 🤖";
    if (input.includes("how are you")) return "I'm just code, but I'm doing great! 😄";

    return "I don't understand that yet 😅";
}


function sendMessage() {
    const input = document.getElementById("input");
    const text = input.value;

    if (!text) return;

    addMessage(text, "user");

    const reply = botReply(text);

    setTimeout(() => {
        addMessage(reply, "bot");
    }, 500);

    input.value = "";
}