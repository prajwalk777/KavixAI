// common/config.js

export const CONFIG = {
    APP: {
        NAME: "Kavix AI",
        VERSION: "v5 Ultimate"
    },

    API: {
        BASE_URL: "http://localhost:3000",
        CHAT_ENDPOINT: "/chat",
        TIMEOUT: 5000
    },

    ESP32: {
        IP: "http://192.168.1.100"
    },

    VOICE: {
        LANG: "en-US",
        RATE: 0.9,
        PITCH: 1.1,
        VOLUME: 1
    },

    UI: {
        TYPING_DELAY: 1200
    },

    EMOTIONS: ["happy", "sad", "neutral"]
};