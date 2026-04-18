# backend/v1_basic/app.py
# Kavix AI v1 — Basic Chat API
# Run: python v1_basic/app.py
# Port: 5001

from flask import Flask, request, jsonify
from flask_cors import CORS
import datetime
import random

app = Flask(__name__)
CORS(app)

# ══════════════════════════════════════════
# INLINE UTILS (no external import needed)
# ══════════════════════════════════════════

_memory = []

def save_memory(user: str, bot: str) -> None:
    _memory.append({"user": user, "bot": bot})

def find_memory(user_input: str) -> str | None:
    for m in reversed(_memory):
        if user_input.lower() in m["user"].lower():
            return m["bot"]
    return None

def get_time() -> str:
    return datetime.datetime.now().strftime("%H:%M:%S")

def get_date() -> str:
    return datetime.datetime.now().strftime("%A, %d %B %Y")

def detect_emotion(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ["happy","great","awesome","love","yay","excited"]): return "happy"
    if any(w in t for w in ["sad","upset","cry","miss","hurt","alone"]):        return "sad"
    if any(w in t for w in ["angry","hate","mad","furious","annoyed"]):         return "angry"
    if any(w in t for w in ["wow","omg","whoa","really","unbelievable"]):       return "surprised"
    if any(w in t for w in ["hmm","maybe","wonder","think","question"]):        return "thinking"
    return "neutral"

# ══════════════════════════════════════════
# REPLY LOGIC
# ══════════════════════════════════════════

RULES = {
    "hello":    ["Hi! I'm Kavix AI v1 🤖", "Hey there! 👋", "Hello! How can I help?"],
    "hi":       ["Hey! 👋", "Hi there!", "Hello!"],
    "name":     ["I'm Kavix AI — your personal assistant!", "My name is Kavix 🤖"],
    "how are":  ["I'm running perfectly! Thanks for asking 😊", "All systems online! 🟢"],
    "bye":      ["Goodbye! 👋", "See you soon!", "Take care! 😊"],
    "thanks":   ["You're welcome! 😊", "Happy to help!", "Anytime! 🤖"],
    "help":     ["I can chat, tell the time, and remember things. Try me!"],
    "joke":     [
        "Why did the robot go on a diet? It had too many bytes! 😄",
        "What do you call a lazy robot? A slackbot! 😂",
        "Why do robots make great musicians? Because they have perfect beet! 🎵"
    ],
}

def get_reply(msg: str) -> str:
    msg_lower = msg.lower()

    # Check memory first
    past = find_memory(msg)
    if past:
        return f"I remember you mentioned this before! You got: '{past}'"

    # Dynamic
    if "time"  in msg_lower: return f"The time is {get_time()} ⏰"
    if "date"  in msg_lower: return f"Today is {get_date()} 📅"
    if "day"   in msg_lower: return f"It's {datetime.datetime.now().strftime('%A')} today 📅"

    # Keyword rules
    for keyword, replies in RULES.items():
        if keyword in msg_lower:
            return random.choice(replies)

    return random.choice([
        "Interesting! Tell me more 🤔",
        "I'm still learning — try asking something else!",
        "Hmm, I don't have an answer for that yet 🤖",
        "Could you rephrase that? I want to understand!",
    ])

# ══════════════════════════════════════════
# ROUTES
# ══════════════════════════════════════════

@app.route("/")
def index():
    return jsonify({
        "name":    "Kavix AI v1",
        "status":  "online",
        "port":    5001,
        "memory":  len(_memory)
    })

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    msg  = data.get("message", "").strip()

    if not msg:
        return jsonify({"error": "No message provided"}), 400

    reply   = get_reply(msg)
    emotion = detect_emotion(msg)

    save_memory(msg, reply)

    return jsonify({
        "reply":   reply,
        "emotion": emotion,
        "version": "v1",
        "memory":  len(_memory)
    })

@app.route("/memory", methods=["GET"])
def memory_view():
    return jsonify({"history": _memory, "total": len(_memory)})

@app.route("/memory/clear", methods=["POST"])
def memory_clear():
    _memory.clear()
    return jsonify({"status": "cleared"})

# ══════════════════════════════════════════
# RUN
# ══════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 45)
    print("  🤖 Kavix AI v1 — Basic Chat")
    print("  Running on http://localhost:5001")
    print("=" * 45)
    app.run(port=5001, debug=True)
