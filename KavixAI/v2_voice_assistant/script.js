function addMessage(text, type) {
    const chatBox = document.getElementById("chat-box");

    const msg = document.createElement("div");
    msg.className = "message " + type;
    msg.innerText = text;

    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
}


// 🔊 Text-to-Speech
function speak(text) {
    const speech = new SpeechSynthesisUtterance(text);
    speech.lang = "en-US";
    speech.rate = 1;
    speech.pitch = 1;

    speechSynthesis.speak(speech);
}


// 🤖 Basic AI logic (same as v1 but used with voice)
function botReply(input) {
    input = input.toLowerCase();

    if (input.includes("hello")) return "Hello! How can I help you?";
    if (input.includes("name")) return "I am Kavix AI voice assistant";
    if (input.includes("time")) return new Date().toLocaleTimeString();

    return "Sorry, I didn't understand that.";
}


// 💬 Send message (text)
function sendMessage() {
    const input = document.getElementById("input");
    const text = input.value;

    if (!text) return;

    addMessage(text, "user");

    const reply = botReply(text);

    setTimeout(() => {
        addMessage(reply, "bot");
        speak(reply); // 🔥 voice output
    }, 500);

    input.value = "";
}


// 🎤 Voice recognition
function startVoice() {
    const SpeechRecognition =
        window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        alert("Voice not supported in this browser");
        return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";

    recognition.start();

    recognition.onresult = (event) => {
        const text = event.results[0][0].transcript;

        document.getElementById("input").value = text;

        sendMessage(); // auto send after speaking
    };
}