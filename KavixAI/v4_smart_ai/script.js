function addMessage(text, type) {
    const chatBox = document.getElementById("chat-box");

    const msg = document.createElement("div");
    msg.className = "message " + type;
    msg.innerText = text;

    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
}


// 🔊 Voice output
function speak(text) {
    const speech = new SpeechSynthesisUtterance(text);
    speech.lang = "en-US";
    speechSynthesis.speak(speech);
}


// 😀 Emotion detection (simple logic)
function detectEmotion(text) {
    text = text.toLowerCase();

    if (text.includes("sad")) return "sad";
    if (text.includes("happy")) return "happy";

    return "neutral";
}


// 🤖 Smart reply system
function botReply(input) {

    // Check memory
    let past = findMemory(input);
    if (past) return "You asked that before. " + past.bot;

    // Basic AI logic
    if (input.includes("name")) return "I am Kavix Smart AI 🤖";
    if (input.includes("time")) return new Date().toLocaleTimeString();

    return "I'm learning... tell me more!";
}


// 💬 Main function
function sendMessage() {
    const input = document.getElementById("input");
    const text = input.value;

    if (!text) return;

    addMessage(text, "user");

    const emotion = detectEmotion(text);

    let reply = botReply(text);

    // Emotion-aware response
    if (emotion === "sad") {
        reply = "You seem sad. I'm here for you 💙";
    }

    setTimeout(() => {
        addMessage(reply, "bot");
        speak(reply);

        saveMemory(text, reply); // 🧠 store memory

    }, 600);

    input.value = "";
}


// 🎤 Voice input
function startVoice() {
    const SpeechRecognition =
        window.SpeechRecognition || window.webkitSpeechRecognition;

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";

    recognition.start();

    recognition.onresult = (event) => {
        const text = event.results[0][0].transcript;
        document.getElementById("input").value = text;
        sendMessage();
    };
}