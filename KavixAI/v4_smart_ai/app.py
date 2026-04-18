# backend/v4_smart/app.py
# Kavix AI v4 — Smart Chat with SQLite Memory + Emotion AI
# Run: python v4_smart/app.py
# Port: 5004

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import datetime
import random
import os

app  = Flask(__name__)
CORS(app)

# ══════════════════════════════════════════
# INLINE UTILS
# ══════════════════════════════════════════

def get_time():
    return datetime.datetime.now().strftime("%H:%M:%S")

def get_date():
    return datetime.datetime.now().strftime("%A, %d %B %Y")

def detect_emotion(text):
    t = text.lower()
    if any(w in t for w in ["happy","great","awesome","love","yay","excited"]): return "happy"
    if any(w in t for w in ["sad","upset","cry","miss","hurt","alone"]):        return "sad"
    if any(w in t for w in ["angry","hate","mad","furious","annoyed"]):         return "angry"
    if any(w in t for w in ["wow","omg","whoa","really","unbelievable"]):       return "surprised"
    if any(w in t for w in ["hmm","maybe","wonder","think","question"]):        return "thinking"
    return "neutral"

# ══════════════════════════════════════════
# SQLITE DATABASE
# ══════════════════════════════════════════

DB_PATH = os.path.join(os.path.dirname(__file__), "kavix_memory.db")

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memory (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                user_msg  TEXT NOT NULL,
                bot_reply TEXT NOT NULL,
                emotion   TEXT DEFAULT 'neutral',
                timestamp TEXT DEFAULT (datetime('now','localtime'))
            )
        """)
        conn.commit()

def save_memory(user_msg, bot_reply, emotion="neutral"):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO memory (user_msg, bot_reply, emotion) VALUES (?, ?, ?)",
            (user_msg, bot_reply, emotion)
        )
        conn.commit()

def find_memory(user_input):
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT bot_reply FROM memory WHERE LOWER(user_msg) LIKE ? ORDER BY id DESC LIMIT 1",
            (f"%{user_input.lower()}%",)
        ).fetchone()
    return row[0] if row else None

def get_all_memory(limit=50):
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT user_msg, bot_reply, emotion, timestamp FROM memory ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()
    return [{"user": r[0], "bot": r[1], "emotion": r[2], "time": r[3]} for r in rows]

def count_memory():
    with sqlite3.connect(DB_PATH) as conn:
        return conn.execute("SELECT COUNT(*) FROM memory").fetchone()[0]

def clear_memory_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM memory")
        conn.commit()

# ══════════════════════════════════════════
# REPLY LOGIC
# ══════════════════════════════════════════

EMOTION_REPLIES = {
    "sad":       ["You seem sad. I'm here for you 💙", "It's okay to feel that way 💙"],
    "happy":     ["You sound happy! That's great! 😊", "Love that energy! 🌟"],
    "angry":     ["I understand you're frustrated. Let's work through it 💪"],
    "surprised": ["Whoa, something surprised you! Tell me more 😲"],
    "thinking":  ["Deep in thought? I'm here to help 🤔"],
}

def generate_reply(msg, emotion):
    msg_lower = msg.lower()
    if "time"  in msg_lower: return f"It's {get_time()} ⏰"
    if "date"  in msg_lower: return f"Today is {get_date()} 📅"
    if "hello" in msg_lower: return "Hey! I'm Kavix v4 — I remember everything! 🧠"

    past = find_memory(msg)
    if past:
        return f"I remember! When you said something similar, I replied: '{past}'"

    if emotion in EMOTION_REPLIES:
        return random.choice(EMOTION_REPLIES[emotion])

    return "Interesting! I've saved that to my memory 🧠"

# ══════════════════════════════════════════
# ROUTES
# ══════════════════════════════════════════

@app.route("/")
def index():
    return jsonify({
        "name":    "Kavix AI v4",
        "status":  "online",
        "port":    5004,
        "memory":  count_memory()
    })

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    msg  = data.get("message", "").strip()
    if not msg:
        return jsonify({"error": "No message"}), 400

    emotion = detect_emotion(msg)
    reply   = generate_reply(msg, emotion)
    save_memory(msg, reply, emotion)

    return jsonify({
        "reply":   reply,
        "emotion": emotion,
        "memory":  count_memory(),
        "version": "v4"
    })

@app.route("/memory", methods=["GET"])
def memory_get():
    limit = request.args.get("limit", 20, type=int)
    return jsonify({"history": get_all_memory(limit), "total": count_memory()})

@app.route("/memory/clear", methods=["POST"])
def memory_clear():
    clear_memory_db()
    return jsonify({"status": "cleared"})

if __name__ == "__main__":
    init_db()
    print("=" * 45)
    print("  🧠 Kavix AI v4 — Smart + Memory")
    print("  Running on http://localhost:5004")
    print("=" * 45)
    app.run(port=5004, debug=True)
