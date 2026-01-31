/**
 * Audio Recorder Module
 * Handles microphone recording using RecordRTC
 */

let recorder = null;
let audioStream = null;
let recordingStartTime = null;
let timerInterval = null;

// ===================================
// Initialize Recording (Tab 2)
// ===================================

document.addEventListener('DOMContentLoaded', () => {
    initializeRecording();
    initialize3DWaveform();
});

function initializeRecording() {
    const startRecordBtn = document.getElementById('start-record-btn');
    const stopRecordBtn = document.getElementById('stop-record-btn');
    const analyzeRecordedBtn = document.getElementById('analyze-recorded-btn');

    startRecordBtn.addEventListener('click', startRecording);
    stopRecordBtn.addEventListener('click', stopRecording);
    analyzeRecordedBtn.addEventListener('click', analyzeRecording);
}

// ===================================
// Start Recording
// ===================================

async function startRecording() {
    try {
        // Request microphone access
        audioStream = await navigator.mediaDevices.getUserMedia({
            audio: {
                echoCancellation: true,
                noiseSuppression: true,
                sampleRate: 44100
            }
        });

        // Initialize RecordRTC
        recorder = RecordRTC(audioStream, {
            type: 'audio',
            mimeType: 'audio/mp3',
            recorderType: RecordRTC.StereoAudioRecorder,
            numberOfAudioChannels: 1,
            desiredSampRate: 16000
        });

        recorder.startRecording();
        recordingStartTime = Date.now();

        // Update UI
        document.getElementById('start-record-btn').classList.add('hidden');
        document.getElementById('stop-record-btn').classList.remove('hidden');
        document.getElementById('recording-timer').classList.remove('hidden');

        // Start timer
        startTimer();

        // Start waveform visualization
        startWaveformVisualization(audioStream);

        console.log('🎙️ Recording started');
        showNotification('Recording started!', 'info');

    } catch (error) {
        console.error('Recording error:', error);
        showNotification('Microphone access denied or unavailable', 'error');
    }
}

// ===================================
// Stop Recording
// ===================================

function stopRecording() {
    if (!recorder) return;

    recorder.stopRecording(() => {
        const blob = recorder.getBlob();

        // Convert to File object
        const fileName = `recording-${Date.now()}.mp3`;
        const recordedFile = new File([blob], fileName, { type: 'audio/mp3' });

        AppState.recordedAudio = recordedFile;

        // Update UI
        const recordedAudioPlayer = document.getElementById('recorded-audio');
        recordedAudioPlayer.src = URL.createObjectURL(blob);
        recordedAudioPlayer.classList.remove('hidden');

        document.getElementById('start-record-btn').classList.remove('hidden');
        document.getElementById('stop-record-btn').classList.add('hidden');
        document.getElementById('analyze-recorded-btn').classList.remove('hidden');

        // Stop timer
        stopTimer();

        // Stop audio stream
        if (audioStream) {
            audioStream.getTracks().forEach(track => track.stop());
        }

        console.log('🎙️ Recording stopped');
        showNotification('Recording complete!', 'success');
    });
}

// ===================================
// Timer
// ===================================

function startTimer() {
    const timerEl = document.getElementById('recording-timer');

    timerInterval = setInterval(() => {
        const elapsed = Math.floor((Date.now() - recordingStartTime) / 1000);
        const minutes = Math.floor(elapsed / 60);
        const seconds = elapsed % 60;

        timerEl.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
    }, 1000);
}

function stopTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
}

// ===================================
// Analyze Recording
// ===================================

async function analyzeRecording() {
    const language = document.getElementById('record-language').value;

    if (!AppState.recordedAudio) {
        showNotification('No recording available', 'error');
        return;
    }

    const analyzeBtn = document.getElementById('analyze-recorded-btn');
    analyzeBtn.disabled = true;
    analyzeBtn.textContent = 'Analyzing...';

    try {
        const result = await analyzeAudioAPI(AppState.recordedAudio, language);
        displayResults(result, 'record-results-section');
        showNotification('Analysis complete!', 'success');
    } catch (error) {
        showNotification(error.message, 'error');
    } finally {
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = '<span class="btn-icon">🔍</span> Analyze Recording';
    }
}

// ===================================
// 3D Waveform Visualization
// ===================================

let waveformScene, waveformCamera, waveformRenderer, waveformBars;
let audioContext, analyser, dataArray;

function initialize3DWaveform() {
    const container = document.getElementById('waveform-container');
    const canvas = document.getElementById('waveform-canvas');

    if (!canvas) return;

    // Setup Three.js scene
    waveformScene = new THREE.Scene();
    waveformCamera = new THREE.PerspectiveCamera(75, container.offsetWidth / container.offsetHeight, 0.1, 1000);
    waveformRenderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true });

    waveformRenderer.setSize(container.offsetWidth, container.offsetHeight);
    waveformCamera.position.z = 50;

    // Create waveform bars
    waveformBars = [];
    const barCount = 64;
    const barWidth = 0.8;
    const spacing = 1.2;

    for (let i = 0; i < barCount; i++) {
        const geometry = new THREE.BoxGeometry(barWidth, 1, barWidth);
        const material = new THREE.MeshBasicMaterial({
            color: new THREE.Color().setHSL(0.6 + i / barCount * 0.2, 0.8, 0.5)
        });
        const bar = new THREE.Mesh(geometry, material);

        bar.position.x = (i - barCount / 2) * spacing;
        bar.position.y = 0;

        waveformScene.add(bar);
        waveformBars.push(bar);
    }

    // Start animation loop
    animateWaveform();
}

function startWaveformVisualization(stream) {
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
    analyser = audioContext.createAnalyser();
    const source = audioContext.createMediaStreamSource(stream);

    source.connect(analyser);
    analyser.fftSize = 128;

    const bufferLength = analyser.frequencyBinCount;
    dataArray = new Uint8Array(bufferLength);
}

function animateWaveform() {
    requestAnimationFrame(animateWaveform);

    if (analyser && dataArray) {
        analyser.getByteFrequencyData(dataArray);

        waveformBars.forEach((bar, i) => {
            const value = dataArray[i] || 0;
            const scale = value / 255 * 20 + 1;
            bar.scale.y = scale;
            bar.position.y = scale / 2;
        });
    } else {
        // Idle animation when not recording
        waveformBars.forEach((bar, i) => {
            const time = Date.now() * 0.001;
            const scale = Math.sin(time + i * 0.1) * 2 + 3;
            bar.scale.y = scale;
            bar.position.y = scale / 2;
        });
    }

    // Rotate scene
    waveformScene.rotation.y += 0.002;

    waveformRenderer.render(waveformScene, waveformCamera);
}

// Handle window resize
window.addEventListener('resize', () => {
    if (waveformRenderer && waveformCamera) {
        const container = document.getElementById('waveform-container');
        waveformCamera.aspect = container.offsetWidth / container.offsetHeight;
        waveformCamera.updateProjectionMatrix();
        waveformRenderer.setSize(container.offsetWidth, container.offsetHeight);
    }
});
