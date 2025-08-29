class AudioProcessor extends AudioWorkletProcessor {
    process(inputs) {
        const input = inputs[0];
        if (input && input.length > 0) {
            const pcmData = input[0];
            // Validate and clamp audio samples
            const int16Data = new Int16Array(pcmData.length);
            
            for (let i = 0; i < pcmData.length; i++) {
                // Clamp between -1 and 1 before conversion
                const sample = Math.max(-1, Math.min(1, pcmData[i]));
                int16Data[i] = sample * 0x7FFF;
            }
            
            try {
                this.port.postMessage(int16Data.buffer, [int16Data.buffer]);
            } catch (e) {
                console.error('Error posting audio message:', e);
            }
        }
        return true;
    }
}

registerProcessor('audio-processor', AudioProcessor);