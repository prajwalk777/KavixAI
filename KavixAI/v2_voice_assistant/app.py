# backend/v2_voice/app.py
# Kavix AI v2 — Voice + Chat API
# Run: python v2_voice/app.py
# Port: 5002

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import pyttsx3
import speech_recognition as sr
import datetime
import tempfile
import random
import os

app  = Flask(__name__)
CORS(app)

# Init TTS once at startup
tts_engine = pyttsx3.init()
tts_engine.setProperty("rate",   165)
tts_engine.setProperty("volume", 0.9)

# ══════════════════════════════════════════
# INLINE UTILS
# ══════════════════════════════════════════

_memory = []

def save_memory(user, bot):
    _memory.append({"user": user, "bot": bot})

def find_memory(user_input):
    for m in reversed(_memory):
        if user_input.lower() in m["user"].lower():
            return m["bot"]
    return None

def get_time():
    return datetime.datetime.now().strftime("%H:%M:%S")

def get_date():
    return datetime.datetime.now().strftime("%A, %d %B %Y")

def detect_emotion(text):
    t = text.lower()
    if any(w in t for w in ["happy","great","awesome","love","yay"]):    return "happy"
    if any(w in t for w in ["sad","upset","cry","miss","hurt"]):         return "sad"
    if any(w in t for w in ["angry","hate","mad","furious","annoyed"]):  return "angry"
    if any(w in t for w in ["wow","omg","whoa","really"]):               return "surprised"
    return "neutral"

# ══════════════════════════════════════════
# TTS HELPER
# ══════════════════════════════════════════

def speak_to_bytes(text):
    """Convert text to WAV bytes using pyttsx3."""
    try:
        tmp = tempfile.mktemp(suffix=".wav")
        tts_engine.save_to_file(text[:400], tmp)
        tts_engine.runAndWait()
        with open(tmp, "rb") as f:
            data = f.read()
        os.unlink(tmp)
        return data
    except Exception as e:
        print(f"[TTS] Error: {e}")
        return None

# ══════════════════════════════════════════
# STT HELPER
# ══════════════════════════════════════════

def transcribe_audio(file_path):
    """Convert audio file to text."""
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(file_path) as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.3)
            audio = recognizer.record(source)
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return None
    except Exception as e:
        print(f"[STT] Error: {e}")
        return None

# ══════════════════════════════════════════
# REPLY LOGIC
# ══════════════════════════════════════════

def get_reply(msg):
    msg_lower = msg.lower()
    past = find_memory(msg)
    if past:
        return f"I remember! Last time: '{past}'"
    if "time"  in msg_lower: return f"It's {get_time()} ⏰"
    if "date"  in msg_lower: return f"Today is {get_date()} 📅"
    if "hello" in msg_lower or "hi" in msg_lower: return "Hey! I'm Kavix v2 with voice! 🎤"
    if "name"  in msg_lower: return "I'm Kavix AI v2 — I can hear and speak!"
    return f"You said: '{msg}'. I'm Kavix v2, listening! 🎤"

# ══════════════════════════════════════════
# ROUTES
# ══════════════════════════════════════════

@app.route("/")
def index():
    return jsonify({"name": "Kavix AI v2", "status": "online", "port": 5002})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    msg  = data.get("message", "").strip()
    if not msg:
        return jsonify({"error": "No message"}), 400

    reply   = get_reply(msg)
    emotion = detect_emotion(msg)
    save_memory(msg, reply)

    # Also speak the reply
    speak_to_bytes(reply)

    return jsonify({
        "reply":   reply,
        "emotion": emotion,
        "version": "v2"
    })

@app.route("/speak", methods=["POST"])
def speak():
    """POST { "text": "Hello" } → WAV audio bytes"""
    data = request.get_json(force=True)
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "No text"}), 400
    audio = speak_to_bytes(text)
    if audio:
        return Response(audio, mimetype="audio/wav")
    return jsonify({"error": "TTS failed"}), 500

@app.route("/listen", methods=["POST"])
def listen():
    """POST audio WAV file → { "transcript": "..." }"""
    if "audio" not in request.files:
        return jsonify({"error": "No audio file"}), 400
    f   = request.files["audio"]
    tmp = tempfile.mktemp(suffix=".wav")
    f.save(tmp)
    transcript = transcribe_audio(tmp)
    os.unlink(tmp)
    if transcript:
        return jsonify({"transcript": transcript})
    return jsonify({"error": "Could not understand audio"}), 422

if __name__ == "__main__":
    print("=" * 45)
    print("  🎤 Kavix AI v2 — Voice + Chat")
    print("  Running on http://localhost:5002")
    print("=" * 45)
    app.run(port=5002, debug=True)
