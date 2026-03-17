// common/utils.js

import { CONFIG } from "./config.js";


// 🎤 Text-to-Speech
export function speak(text) {
    if (!text) return;

    const speech = new SpeechSynthesisUtterance(text);

    speech.lang = CONFIG.VOICE.LANG;
    speech.rate = CONFIG.VOICE.RATE;
    speech.pitch = CONFIG.VOICE.PITCH;
    speech.volume = CONFIG.VOICE.VOLUME;

    speechSynthesis.speak(speech);
}


// 💬 Add message to chat
export function addMessage(text, type = "bot") {
    const chatBox = document.getElementById("chat-box");

    const msg = document.createElement("div");
    msg.className = `message ${type}`;
    msg.innerText = text;

    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
}


// ⏳ Typing indicator
export function showTyping() {
    const chatBox = document.getElementById("chat-box");

    const typing = document.createElement("div");
    typing.id = "typing";
    typing.className = "message bot";
    typing.innerText = "Kavix is thinking... 🤖";

    chatBox.appendChild(typing);
}

export function removeTyping() {
    const typing = document.getElementById("typing");
    if (typing) typing.remove();
}


// 🌐 API call to backend
export async function getAIResponse(message) {
    try {
        const res = await fetch(
            CONFIG.API.BASE_URL + CONFIG.API.CHAT_ENDPOINT,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ message })
            }
        );

        const data = await res.json();
        return data.reply || "No response from AI";

    } catch (error) {
        console.error(error);
        return "Server error ⚠️";
    }
}


// 🔌 Send emotion to ESP32
export function sendToESP32(emotion) {
    fetch(`${CONFIG.ESP32.IP}/emotion?e=${emotion}`)
        .catch(() => console.log("ESP32 not reachable"));
}


// 😀 Get random emotion
export function getRandomEmotion() {
    const emotions = CONFIG.EMOTIONS;
    return emotions[Math.floor(Math.random() * emotions.length)];
}


// 🎤 Voice recognition
export function startVoiceRecognition(callback) {
    const SpeechRecognition =
        window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        alert("Voice recognition not supported");
        return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = CONFIG.VOICE.LANG;

    recognition.start();

    recognition.onresult = (event) => {
        const text = event.results[0][0].transcript;
        callback(text);
    };
}


// ⏰ Delay helper
export function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}