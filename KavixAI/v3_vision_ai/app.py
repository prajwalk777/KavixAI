# backend/v3_vision/app.py
# Kavix AI v3 — Vision / Object Detection API
# Run: python v3_vision/app.py
# Port: 5003

from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import base64
import os

app  = Flask(__name__)
CORS(app)

# ══════════════════════════════════════════
# COCO LABELS (Pascal VOC 20 classes)
# ══════════════════════════════════════════

COCO_CLASSES = [
    "background","aeroplane","bicycle","bird","boat",
    "bottle","bus","car","cat","chair","cow",
    "diningtable","dog","horse","motorbike","person",
    "pottedplant","sheep","sofa","train","tvmonitor"
]

# ── Optional: load MobileNet-SSD model ────
MODEL_DIR    = os.path.join(os.path.dirname(__file__), "models")
PROTO_PATH   = os.path.join(MODEL_DIR, "MobileNetSSD_deploy.prototxt")
WEIGHTS_PATH = os.path.join(MODEL_DIR, "MobileNetSSD_deploy.caffemodel")

net = None
if os.path.exists(PROTO_PATH) and os.path.exists(WEIGHTS_PATH):
    net = cv2.dnn.readNetFromCaffe(PROTO_PATH, WEIGHTS_PATH)
    print("[Vision] MobileNet-SSD model loaded ✓")
else:
    print("[Vision] No model files — basic camera mode only.")
    print(f"         Place model files in: {MODEL_DIR}/")

# ══════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════

def detect_from_frame(frame, threshold=0.5):
    if net is None:
        return []
    h, w = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(
        cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5
    )
    net.setInput(blob)
    detections = net.forward()
    results = []
    for i in range(detections.shape[2]):
        conf = float(detections[0, 0, i, 2])
        if conf < threshold:
            continue
        idx = int(detections[0, 0, i, 1])
        if idx >= len(COCO_CLASSES):
            continue
        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
        x1, y1, x2, y2 = box.astype(int)
        results.append({
            "label":      COCO_CLASSES[idx],
            "confidence": round(conf, 3),
            "box":        [int(x1), int(y1), int(x2-x1), int(y2-y1)]
        })
    return results

def frame_to_b64(frame):
    _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
    return base64.standard_b64encode(buf).decode("utf-8")

def b64_to_frame(b64_str):
    try:
        arr = np.frombuffer(base64.b64decode(b64_str), dtype=np.uint8)
        return cv2.imdecode(arr, cv2.IMREAD_COLOR)
    except Exception:
        return None

# ══════════════════════════════════════════
# ROUTES
# ══════════════════════════════════════════

@app.route("/")
def index():
    return jsonify({
        "name":         "Kavix AI v3",
        "status":       "online",
        "port":         5003,
        "model_loaded": net is not None
    })

@app.route("/detect", methods=["GET"])
def detect_webcam():
    """Capture from webcam and detect objects."""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return jsonify({"error": "Camera not available"}), 503

    ret, frame = cap.read()
    cap.release()

    if not ret:
        return jsonify({"error": "Failed to capture frame"}), 500

    detections = detect_from_frame(frame)
    labels     = [d["label"] for d in detections]
    summary    = f"I can see: {', '.join(labels)}" if labels else "Camera working — nothing detected."

    return jsonify({
        "result":     summary,
        "detections": detections,
        "count":      len(detections)
    })

@app.route("/detect/image", methods=["POST"])
def detect_image():
    """Upload image for detection (multipart or base64 JSON)."""
    frame = None

    if "image" in request.files:
        arr   = np.frombuffer(request.files["image"].read(), dtype=np.uint8)
        frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    elif request.is_json:
        b64   = request.get_json(force=True).get("image_b64", "")
        frame = b64_to_frame(b64) if b64 else None

    if frame is None:
        return jsonify({"error": "No valid image"}), 400

    detections = detect_from_frame(frame)

    for d in detections:
        x, y, w, h = d["box"]
        label = f"{d['label']} {int(d['confidence']*100)}%"
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 200, 80), 2)
        cv2.putText(frame, label, (x, y-8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 80), 1)

    return jsonify({
        "detections":    detections,
        "labels":        list({d["label"] for d in detections}),
        "annotated_b64": frame_to_b64(frame),
        "count":         len(detections)
    })

@app.route("/camera/test", methods=["GET"])
def camera_test():
    cap = cv2.VideoCapture(0)
    ok  = cap.isOpened()
    cap.release()
    return jsonify({
        "camera_available": ok,
        "message": "Camera working ✓" if ok else "No camera found ✗"
    })

if __name__ == "__main__":
    print("=" * 45)
    print("  📷 Kavix AI v3 — Vision")
    print("  Running on http://localhost:5003")
    print("=" * 45)
    app.run(port=5003, debug=True)
