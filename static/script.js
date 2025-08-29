const recordBtn = document.getElementById('recordBtn');
const aiMessage = document.getElementById('aiMessage');
const llmReply = document.getElementById("llmReply");
const llmText = document.getElementById("llmText");


let ws = null;
let stream, audioCtx, source, processor;
let isRecording = false;
let startTime = 0;
let audioChunks = []; // store streaming chunks for final playback

document.addEventListener("DOMContentLoaded", () => {
  // --- Modal elements ---
  const modal = document.getElementById("keysModal");
  const openBtn = document.getElementById("openKeysBtn");
  const closeBtn = document.getElementById("closeModal");

  // Open modal
  openBtn.addEventListener("click", () => {
    modal.style.display = "flex"; // use flex to center
  });

  // Close modal on X click
  closeBtn.addEventListener("click", () => {
    modal.style.display = "none";
  });

  // Close modal on outside click
  window.addEventListener("click", (e) => {
    if (e.target === modal) modal.style.display = "none";
  });

  // Save keys button

  // --- Save keys ---
  const saveBtn = document.getElementById("saveKeysBtn");
  if (saveBtn) {
    saveBtn.addEventListener("click", async () => {
      const googleKey = document.getElementById("googleKey").value.trim();
      const tavilyKey = document.getElementById("tavilyKey").value.trim();
      const assemblyKey = document.getElementById("assemblyKey").value.trim();
      const murfKey = document.getElementById("murfKey").value.trim();
      const openweatherKey = document.getElementById("openweatherKey").value.trim();

      if (!googleKey || !tavilyKey || !assemblyKey || !murfKey) {
        alert("⚠️ Please enter ALL required API keys before saving.");
        return; // stop execution
      }

      const keys = {
        google_api_key: googleKey || null,
        tavily_api_key: tavilyKey || null,
        assembly_api_key: assemblyKey || null,
        murf_api_key: murfKey || null,
        openweather_api_key: openweatherKey || null
      };


      try {
        const response = await fetch("/set-keys", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(keys),
        });

        const result = await response.json();
        if (result.status === "success") {
          const statusMsg = document.getElementById("saveStatus");
          statusMsg.style.display = "block";
          setTimeout(() => {
            statusMsg.style.display = "none";
            modal.style.display = "none"; // auto close after save
          }, 2000);
        } else {
          alert("❌ Failed to save keys: " + result.message);
        }
      } catch (error) {
        console.error("Error saving keys:", error);
      }
    });
  }
});
recordBtn.addEventListener("click", async () => {
  if (!isRecording) {
    const sessionId = "default";
    const wsProtocol = window.location.protocol === "https:" ? "wss" : "ws";
    const wsHost = window.location.host;
    ws = new WebSocket(`${wsProtocol}://${wsHost}/ws/${sessionId}`);

    ws.onopen = () => console.log("✅ WebSocket connected");
    ws.onclose = () => console.log("❌ WebSocket closed");
    ws.onerror = (err) => console.error("⚠️ WebSocket error", err);

    ws.onmessage = async (event) => {
      try {
        const data = JSON.parse(event.data);

        // Display transcript
        if (data.type === "turn_detected") {
          console.log("📝 Transcript:", data.transcript);
          aiMessage.style.display = "block";
          aiMessage.textContent = "You: " + data.transcript;
        }
        if (data.type === "llm_transcript") {
          llmReply.style.display = "block";

          // Clear old reply if this is the first chunk of a new reply
          if (!llmText.dataset.started || llmText.dataset.started === "false") {
            llmText.textContent = "";           // clear previous reply
            llmText.dataset.started = "true";   // mark reply as started
          }

          llmText.textContent += data.transcript; // append streaming chunks
        }

        if (data.type === "llm_final") {
          // Reply finished → reset flag for the next question
          llmText.dataset.started = "false";
        }



        // Play streaming audio
        if (data.type === "audio_chunk") {
          console.log("🎧 Received audio chunk (base64):", data.data.slice(0, 50) + "...");

          // Decode base64 → PCM16
          const byteArray = Uint8Array.from(atob(data.data), c => c.charCodeAt(0));
          const pcm16 = new Int16Array(byteArray.buffer);

          // Convert PCM16 → Float32
          const float32 = new Float32Array(pcm16.length);
          for (let i = 0; i < pcm16.length; i++) {
            float32[i] = pcm16[i] / 0x8000;
          }

          // Store chunk for optional final playback


          // Create AudioBuffer at 16kHz
          const audioBuffer = audioCtx.createBuffer(1, float32.length, 44100);

          audioBuffer.getChannelData(0).set(float32);

          // Play chunk
          const sourceNode = audioCtx.createBufferSource();
          sourceNode.buffer = audioBuffer;
          sourceNode.connect(audioCtx.destination);

          if (startTime === 0) startTime = audioCtx.currentTime;
          sourceNode.start(startTime);
          startTime += audioBuffer.duration;

          console.log("🎧 Streaming audio — playing chunk...");
        }

        // All audio chunks received
        if (data.type === "audio_end") {
          console.log("🎵 All audio chunks received and played");
          startTime = 0;

          // Optional: merge chunks and display <audio> player
        }

      } catch (e) {
        console.error("Failed to parse message", e, event.data);
      }
    };

    // Start microphone
    stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioCtx = new AudioContext({ sampleRate: 44100 });
    source = audioCtx.createMediaStreamSource(stream);
    processor = audioCtx.createScriptProcessor(4096, 1, 1);

    source.connect(processor);
    processor.connect(audioCtx.destination);

    processor.onaudioprocess = (e) => {
      const inputData = e.inputBuffer.getChannelData(0);
      const buffer = new ArrayBuffer(inputData.length * 2);
      const view = new DataView(buffer);
      for (let i = 0; i < inputData.length; i++) {
        let s = Math.max(-1, Math.min(1, inputData[i]));
        view.setInt16(i * 2, s < 0 ? s * 0x8000 : s * 0x7fff, true);
      }
      if (ws.readyState === WebSocket.OPEN) ws.send(buffer);
    };

    recordBtn.textContent = "⏹️ Stop Recording";
    isRecording = true;

  } else {
    // Stop recording
    if (processor) processor.disconnect();
    if (source) source.disconnect();
    if (audioCtx) audioCtx.close();
    if (stream) stream.getTracks().forEach(track => track.stop());
    if (ws) ws.close();

    recordBtn.textContent = "🎤 Start Recording";
    isRecording = false;
  }
});

// Helper to merge Float32Array chunks into single AudioBuffer
function mergeAudioChunks(chunks) {
  const length = chunks.reduce((sum, arr) => sum + arr.length, 0);
  const mergedBuffer = new Float32Array(length);
  let offset = 0;
  chunks.forEach(chunk => {
    mergedBuffer.set(chunk, offset);
    offset += chunk.length;
  });

  // Create AudioBuffer for bufferToWave
  const audioBuffer = audioCtx.createBuffer(1, mergedBuffer.length, 44100);
  audioBuffer.getChannelData(0).set(mergedBuffer);
  return audioBuffer;
}
