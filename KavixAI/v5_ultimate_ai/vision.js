let model;

async function initVision() {
    const video = document.getElementById("video");

    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = stream;

    model = await cocoSsd.load();
}

async function detectObjects() {
    const video = document.getElementById("video");
    const predictions = await model.detect(video);

    let objects = predictions.map(p => p.class);
    let result = "I see: " + objects.join(", ");

    addMessage(result, "bot");
    speak(result);
}

initVision();