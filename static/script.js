

let mediaRecorder;
let audioChunks = [];
let isRecording = false;

function getSessionId() {
  const urlParams = new URLSearchParams(window.location.search);
  let sessionId = urlParams.get("session_id");
  if (!sessionId) {
    sessionId = crypto.randomUUID();
    urlParams.set("session_id", sessionId);
    window.history.replaceState({}, "", `?${urlParams}`);
  }
  return sessionId;
}


function toggleRecording() {
  const btn = document.getElementById("recordBtn");
  if (!isRecording) {
    startRecording();
    btn.textContent = "⏹ Stop Recording";
    btn.classList.add("recording");
    isRecording = true;
  } else {
    stopRecording();
    btn.textContent = "🎤 Start Conversation";
    btn.classList.remove("recording");
    isRecording = false;
  }
}

function startRecording() {
  navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream => {
      mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm;codecs=opus' });
      audioChunks = [];
      mediaRecorder.ondataavailable = event => audioChunks.push(event.data);
      mediaRecorder.start();
      console.log("Recording started...");
    })
    .catch(err => {
      alert("Microphone access denied or unavailable.");
      console.error(err);
    });
}


function stopRecording() {
  if (mediaRecorder && mediaRecorder.state !== "inactive") {
    mediaRecorder.stop();
    mediaRecorder.onstop = () => {
      const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
      sendToChatAgent(audioBlob); // Call your Day 10 chat function
    };
  }
}



function sendToChatAgent(audioBlob) {
  const status = document.getElementById("uploadStatus");
  const userMessageBox = document.getElementById("userMessage");
  const aiMessageBox = document.getElementById("aiMessage");
  const sessionId = getSessionId();
  
  const formData = new FormData();
  formData.append("file", audioBlob, `recording_${Date.now()}.wav`);

  status.style.display = "block";
  status.textContent = "⏳ Thinking...";

  fetch(`/agent/chat/${sessionId}`, {
    method: "POST",
    body: formData
  })
    .then(res => res.json())
    .then(data => {
      if (data.transcript) {
        userMessageBox.textContent = "🗣 " + data.transcript;
        userMessageBox.style.display = "block";
      }
      if (data.llm_response) {
        aiMessageBox.textContent = "🤖 " + data.llm_response;
        aiMessageBox.style.display = "block";
      }
      if (data.audio_url) {
        const audio = document.getElementById("echoAudio");
        audio.src = data.audio_url;
        audio.play();
      }
      status.style.display = "none";
    })
    .catch(err => {
      status.textContent = "❌ Error occurred";
      console.error(err);
    });
}
