# 🤖 Kavix AI

**Kavix AI** is an intelligent virtual assistant powered by AI, featuring voice interaction, vision capabilities, an OLED robot face, and a modern ChatGPT-style interface.

---

## ✨ Features

* 🎤 Voice Input & Response
* 👁️ Vision AI (Camera-based understanding)
* 🤖 OLED Robot Face Display
* 💬 ChatGPT-style UI
* ⚡ Fast & Lightweight
* 🔒 Works Offline (optional setup)

---

## 🧠 Tech Stack

* Python 🐍
* ESP32 (IoT Integration)
* AI Models (Local / API-based)
* OpenCV (Vision AI)
* Text-to-Speech & Speech Recognition

---
---

## 📦 Requirements

### 🔌 Arduino Libraries

Install the following libraries in **Arduino IDE**:

* `WiFi.h`
* `WebServer.h`
* `Adafruit_GFX`
* `Adafruit_SSD1306`

---

### 🐍 Python Dependencies

Create a `requirements.txt` file in your project root:

```txt
opencv-python
flask
numpy
```

Install using:

```bash
pip install -r requirements.txt
```

---

### 🔑 Environment Variables

Create a `.env` file for API keys:

```env
OPENAI_API_KEY=your_key_here
```

> ⚠️ Do NOT share your API keys publicly.

---

## ⚙️ Setup Instructions

1. Install Arduino libraries
2. Install Python dependencies
3. Add your API key in `.env`
4. Upload `.ino` code to ESP32
5. Run the Python/Frontend app

---

## 📂 Project Structure

```
KavixAI/
├── common/
│   ├── utils.js
│   └── config.js
├── assets/
│   ├── demo.gif
│   └── screenshots/
├── backend/
├── frontend/
├── README.md
├── LICENSE
```

---

## 🛠️ Installation

```bash
git clone https://github.com/prajwalk777/KavixAI.git
cd KavixAI
pip install -r requirements.txt
```

---

## ▶️ Run the Project

```bash
python app.py
```

---

## 📸 Demo

*Add your demo GIF here (important for GitHub impact)*
Example:

```
![Demo](assets/demo.gif)
```

---

## 🔮 Future Upgrades

* 🧠 Advanced AI Memory
* 🌐 Web Dashboard
* 📱 Mobile App Version
* 🗣️ Real-time Conversation Mode

---

## 👨‍💻 Author

**prajwalk777**

---

## 📜 License

This project is licensed under the MIT License.
