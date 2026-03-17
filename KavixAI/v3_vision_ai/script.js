let model;

// 🎥 Start camera
async function startCamera() {
    const video = document.getElementById("video");

    const stream = await navigator.mediaDevices.getUserMedia({
        video: true
    });

    video.srcObject = stream;
}

// 🧠 Load AI model
async function loadModel() {
    model = await cocoSsd.load();
    console.log("Model loaded");
}

// 📷 Detect objects
async function detectObjects() {
    const video = document.getElementById("video");

    const predictions = await model.detect(video);

    if (predictions.length === 0) {
        document.getElementById("output").innerText =
            "I don't see anything clearly 😅";
        return;
    }

    let objects = predictions.map(p => p.class);
    let result = "I see: " + objects.join(", ");

    document.getElementById("output").innerText = result;

    speak(result); // 🔊 optional voice
}


// 🔊 Voice output
function speak(text) {
    const speech = new SpeechSynthesisUtterance(text);
    speech.lang = "en-US";
    speechSynthesis.speak(speech);
}


// 🚀 Init
startCamera();
loadModel();