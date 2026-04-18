# backend/v5_ultimate/app.py
# Kavix AI v5 — Ultimate: Claude AI + Voice + Vision + SQLite + ESP32
# Run: python v5_ultimate/app.py
# Port: 5005

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import anthropic
import sqlite3
import cv2
import pyttsx3
import speech_recognition as sr
import numpy as np
import base64
import requests as req
import tempfile
import threading
import random
import datetime
import os

app  = Flask(__name__)
CORS(app)

# ══════════════════════════════════════════
# CONFIG — edit these or set as env vars
# ══════════════════════════════════════════

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ESP32_IP          = os.environ.get("ESP32_IP", "http://192.168.1.100")
DB_PATH           = os.path.join(os.path.dirname(__file__), "kavix_v5.db")

claude   = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None
tts_lock = threading.Lock()
_tts     = None

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
# DATABASE
# ══════════════════════════════════════════

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                role      TEXT NOT NULL,
                content   TEXT NOT NULL,
                emotion   TEXT DEFAULT 'neutral',
                timestamp TEXT DEFAULT (datetime('now','localtime'))
            )
        """)
        conn.commit()

def db_add(role, content, emotion="neutral"):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO conversations (role, content, emotion) VALUES (?, ?, ?)",
            (role, content, emotion)
        )
        conn.commit()

def db_history(limit=20):
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT role, content FROM conversations ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()
    return [{"role": r[0], "content": r[1]} for r in reversed(rows)]

def db_count():
    with sqlite3.connect(DB_PATH) as conn:
        return conn.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]

def db_all(limit=50):
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT role, content, emotion, timestamp FROM conversations ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()
    return [{"role": r[0], "content": r[1], "emotion": r[2], "time": r[3]} for r in rows]

def db_clear():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM conversations")
        conn.commit()

# ══════════════════════════════════════════
# AI REPLY
# ══════════════════════════════════════════

SYSTEM_PROMPT = (
    "You are Kavix, an intelligent and friendly AI assistant with vision and voice. "
    "Be helpful, concise, and natural. When describing images, be specific."
)

def get_ai_reply(user_msg, image_b64=None):
    if not claude:
        return local_reply(user_msg)

    history  = db_history(limit=20)
    content  = []
    if image_b64:
        content.append({
            "type":   "image",
            "source": {"type": "base64", "media_type": "image/jpeg", "data": image_b64}
        })
    content.append({"type": "text", "text": user_msg})

    messages = history + [{"role": "user", "content": content if image_b64 else user_msg}]

    try:
        resp = claude.messages.create(
            model="claude-opus-4-5", max_tokens=1024,
            system=SYSTEM_PROMPT, messages=messages
        )
        return resp.content[0].text
    except Exception as e:
        print(f"[Claude] Error: {e}")
        return local_reply(user_msg)

def local_reply(msg):
    m = msg.lower()
    if "time"  in m: return f"It's {get_time()} ⏰"
    if "date"  in m: return f"Today is {get_date()} 📅"
    if "hello" in m: return "Hi! I'm Kavix v5 🤖 (Set ANTHROPIC_API_KEY for full AI)"
    return "I'm Kavix v5. Set ANTHROPIC_API_KEY environment variable to unlock Claude AI 🔑"

# ══════════════════════════════════════════
# ESP32 BRIDGE
# ══════════════════════════════════════════

def send_to_esp32(emotion):
    try:
        r = req.post(f"{ESP32_IP}/emotion", json={"emotion": emotion}, timeout=2)
        return {"sent": True, "response": r.text}
    except Exception as e:
        return {"sent": False, "error": str(e)}

# ══════════════════════════════════════════
# TTS
# ══════════════════════════════════════════

def get_tts():
    global _tts
    if _tts is None:
        _tts = pyttsx3.init()
        _tts.setProperty("rate", 165)
        _tts.setProperty("volume", 0.9)
    return _tts

def speak_to_bytes(text):
    with tts_lock:
        try:
            tts = get_tts()
            tmp = tempfile.mktemp(suffix=".wav")
            tts.save_to_file(text[:400], tmp)
            tts.runAndWait()
            with open(tmp, "rb") as f:
                data = f.read()
            os.unlink(tmp)
            return data
        except Exception as e:
            print(f"[TTS] Error: {e}")
            return None

# ══════════════════════════════════════════
# STT
# ══════════════════════════════════════════

def transcribe(file_path):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(file_path) as source:
            audio = recognizer.record(source)
        return recognizer.recognize_google(audio)
    except Exception:
        return None

# ══════════════════════════════════════════
# VISION
# ══════════════════════════════════════════

def capture_webcam_b64():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return None
    ret, frame = cap.read()
    cap.release()
    if not ret:
        return None
    _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
    return base64.standard_b64encode(buf).decode("utf-8")

# ══════════════════════════════════════════
# ROUTES
# ══════════════════════════════════════════

@app.route("/")
def index():
    return jsonify({
        "name":       "Kavix AI v5 Ultimate",
        "status":     "online",
        "port":       5005,
        "ai_enabled": claude is not None,
        "memory":     db_count(),
        "features":   ["chat","voice","vision","memory","emotion","esp32"]
    })

@app.route("/chat", methods=["POST"])
def chat():
    data      = request.get_json(force=True)
    msg       = data.get("message", "").strip()
    image_b64 = data.get("image_b64", None)
    if not msg:
        return jsonify({"error": "No message"}), 400

    emotion = detect_emotion(msg)
    reply   = get_ai_reply(msg, image_b64)
    db_add("user",      msg,   emotion)
    db_add("assistant", reply, "neutral")
    esp32 = send_to_esp32(emotion)

    return jsonify({
        "reply":   reply,
        "emotion": emotion,
        "esp32":   esp32,
        "memory":  db_count(),
        "version": "v5"
    })

@app.route("/vision/chat", methods=["POST"])
def vision_chat():
    msg = (request.get_json(force=True) or {}).get("message", "What do you see?")
    b64 = capture_webcam_b64()
    if not b64:
        return jsonify({"error": "Camera not available"}), 503
    reply   = get_ai_reply(msg, b64)
    emotion = detect_emotion(reply)
    db_add("user",      f"[Vision] {msg}", "neutral")
    db_add("assistant", reply,              emotion)
    return jsonify({"reply": reply, "emotion": emotion, "image_b64": b64})

@app.route("/voice/listen", methods=["POST"])
def voice_listen():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file"}), 400
    f   = request.files["audio"]
    tmp = tempfile.mktemp(suffix=".wav")
    f.save(tmp)
    transcript = transcribe(tmp)
    os.unlink(tmp)
    if not transcript:
        return jsonify({"error": "Could not understand audio"}), 422
    emotion = detect_emotion(transcript)
    reply   = get_ai_reply(transcript)
    db_add("user",      transcript, emotion)
    db_add("assistant", reply,      "neutral")
    send_to_esp32(emotion)
    return jsonify({"transcript": transcript, "reply": reply, "emotion": emotion})

@app.route("/voice/speak", methods=["POST"])
def voice_speak():
    text = (request.get_json(force=True) or {}).get("text", "")
    if not text:
        return jsonify({"error": "No text"}), 400
    audio = speak_to_bytes(text)
    if audio:
        return Response(audio, mimetype="audio/wav")
    return jsonify({"error": "TTS failed"}), 500

@app.route("/memory", methods=["GET"])
def memory_get():
    limit = request.args.get("limit", 30, type=int)
    return jsonify({"history": db_all(limit), "total": db_count()})

@app.route("/memory/clear", methods=["POST"])
def memory_clear():
    db_clear()
    return jsonify({"status": "cleared"})

@app.route("/emotion", methods=["POST"])
def emotion_direct():
    emotion = (request.get_json(force=True) or {}).get("emotion", "neutral")
    return jsonify({"emotion": emotion, "esp32": send_to_esp32(emotion)})

@app.route("/status", methods=["GET"])
def status():
    cap = cv2.VideoCapture(0)
    cam = cap.isOpened()
    cap.release()
    return jsonify({
        "server":     "online",
        "ai_enabled": claude is not None,
        "camera":     cam,
        "memory":     db_count(),
        "esp32_ip":   ESP32_IP,
        "time":       get_time(),
        "date":       get_date()
    })

# ══════════════════════════════════════════
# RUN
# ══════════════════════════════════════════

if __name__ == "__main__":
    init_db()
    print("=" * 50)
    print("  🤖 KAVIX AI v5 ULTIMATE")
    print(f"  AI:    {'✓ Claude enabled' if claude else '✗ Set ANTHROPIC_API_KEY'}")
    print(f"  ESP32: {ESP32_IP}")
    print("  Running on http://localhost:5005")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5005, debug=True)
