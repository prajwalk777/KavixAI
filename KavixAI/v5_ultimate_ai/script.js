function addMessage(text, type) {
    const chatBox = document.getElementById("chat-box");

    const msg = document.createElement("div");
    msg.className = "message " + type;
    msg.innerText = text;

    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
}


function detectEmotion(text) {
    if (text.includes("sad")) return "sad";
    if (text.includes("happy")) return "happy";
    return "neutral";
}


async function sendMessage() {
    const input = document.getElementById("input");
    const text = input.value;

    if (!text) return;

    addMessage(text, "user");

    let reply;

    // 🧠 memory check
    let past = findMemory(text);
    if (past) {
        reply = "I remember this: " + past.bot;
    } else {
        reply = await getAIResponse(text);
    }

    // 😀 emotion
    let emotion = detectEmotion(text);
    if (emotion === "sad") {
        reply = "You seem sad 💙 I'm here.";
    }

    setTimeout(() => {
        addMessage(reply, "bot");
        speak(reply);
        saveMemory(text, reply);
    }, 500);

    input.value = "";
}