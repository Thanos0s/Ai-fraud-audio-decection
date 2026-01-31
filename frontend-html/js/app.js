/**
 * Main Application Logic
 * Handles tab navigation, file uploads, and UI interactions
 */

// ===================================
// Global State
// ===================================

const AppState = {
    currentTab: 'upload',
    apiUrl: 'http://localhost:8000/api/voice-detection',
    apiKey: 'sk_test_voice_detection_2026',
    currentAudioFile: null,
    recordedAudio: null
};

// ===================================
// Initialize App
// ===================================

document.addEventListener('DOMContentLoaded', () => {
    initializeTabs();
    initializeUpload();
    initializeConfiguration();
    initializeBatchAnalysis();
    initializeSidebarToggle();
    createParticles();
    console.log('🎤 AI Voice Detection System Initialized');
});

// ===================================
// Tab Navigation
// ===================================

function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabId = button.dataset.tab;

            // Update active tab button
            tabButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');

            // Update active tab pane
            tabPanes.forEach(pane => pane.classList.remove('active'));
            document.getElementById(`${tabId}-tab`).classList.add('active');

            AppState.currentTab = tabId;
        });
    });
}

// ===================================
// Configuration
// ===================================

function initializeConfiguration() {
    const apiUrlInput = document.getElementById('api-url');
    const apiKeyInput = document.getElementById('api-key');

    apiUrlInput.addEventListener('change', (e) => {
        AppState.apiUrl = e.target.value;
        console.log('API URL updated:', AppState.apiUrl);
    });

    apiKeyInput.addEventListener('change', (e) => {
        AppState.apiKey = e.target.value;
        console.log('API Key updated');
    });
}

// ===================================
// Sidebar Toggle
// ===================================

function initializeSidebarToggle() {
    const toggleBtn = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');

    toggleBtn.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
        toggleBtn.classList.toggle('sidebar-open');

        // Update button icon
        if (sidebar.classList.contains('collapsed')) {
            toggleBtn.textContent = '☰';
        } else {
            toggleBtn.textContent = '☰';
        }
    });
}

// ===================================
// File Upload (Tab 1)
// ===================================

function initializeUpload() {
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('audio-file');
    const audioPreview = document.getElementById('audio-preview');
    const analyzeBtn = document.getElementById('analyze-btn');

    // Click to upload
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });

    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = 'var(--primary)';
        uploadArea.style.background = 'rgba(255, 75, 75, 0.05)';
    });

    uploadArea.addEventListener('dragleave', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '';
        uploadArea.style.background = '';
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '';
        uploadArea.style.background = '';

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelect(files[0]);
        }
    });

    // File input change
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });

    // Analyze button
    analyzeBtn.addEventListener('click', () => {
        analyzeUploadedFile();
    });
}

function handleFileSelect(file) {
    if (!file.name.endsWith('.mp3')) {
        showNotification('Please upload an MP3 file', 'error');
        return;
    }

    AppState.currentAudioFile = file;

    // Show preview
    const audioPreview = document.getElementById('audio-preview');
    const analyzeBtn = document.getElementById('analyze-btn');

    audioPreview.src = URL.createObjectURL(file);
    audioPreview.classList.remove('hidden');
    analyzeBtn.classList.remove('hidden');

    console.log('File selected:', file.name);
}

async function analyzeUploadedFile() {
    const language = document.getElementById('upload-language').value;
    const loadingEl = document.getElementById('loading');
    const analyzeBtn = document.getElementById('analyze-btn');

    if (!AppState.currentAudioFile) {
        showNotification('Please select a file first', 'error');
        return;
    }

    // Show loading
    loadingEl.classList.remove('hidden');
    analyzeBtn.disabled = true;

    try {
        const result = await analyzeAudioAPI(AppState.currentAudioFile, language);
        displayResults(result, 'results-section');
        showNotification('Analysis complete!', 'success');
    } catch (error) {
        showNotification(error.message, 'error');
    } finally {
        loadingEl.classList.add('hidden');
        analyzeBtn.disabled = false;
    }
}

// ===================================
// Results Display
// ===================================

function displayResults(data, containerId) {
    const container = document.getElementById(containerId);

    const classification = data.classification || 'UNKNOWN';
    const confidence = data.confidenceScore || 0;
    const explanation = data.explanation || 'No explanation provided';

    const isAI = classification === 'AI_GENERATED';
    const color = isAI ? 'var(--danger)' : 'var(--success)';
    const icon = isAI ? '🤖' : '👤';
    const bgClass = isAI ? 'ai-generated' : 'human';

    container.innerHTML = `
        <div class="card">
            <div class="result-banner ${bgClass}">
                <h2 class="result-title" style="color: ${color};">
                    ${icon} ${classification.replace('_', ' ')}
                </h2>
                <p class="result-confidence" style="color: ${color};">
                    Confidence: ${(confidence * 100).toFixed(1)}%
                </p>
                <p class="result-explanation">${explanation}</p>
            </div>
            
            <div class="gauge-container">
                <canvas id="confidence-gauge"></canvas>
            </div>
            
            <button class="btn btn-secondary btn-block" onclick="downloadResults()">
                📥 Download Results (JSON)
            </button>
        </div>
    `;

    container.classList.remove('hidden');

    // Create gauge chart
    createGaugeChart('confidence-gauge', confidence, isAI);

    // Save results for download
    AppState.lastResults = data;
}

// ===================================
// Gauge Chart
// ===================================

function createGaugeChart(canvasId, confidence, isAI) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const color = isAI ? 'rgb(255, 75, 75)' : 'rgb(9, 171, 59)';

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [confidence * 100, 100 - (confidence * 100)],
                backgroundColor: [color, '#E6E9EF'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            circumference: 180,
            rotation: 270,
            cutout: '75%',
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: false
                }
            }
        },
        plugins: [{
            beforeDraw: function (chart) {
                const width = chart.width;
                const height = chart.height;
                const ctx = chart.ctx;
                ctx.restore();

                const fontSize = (height / 100).toFixed(2);
                ctx.font = fontSize + "em sans-serif";
                ctx.textBaseline = "middle";
                ctx.fillStyle = color;

                const text = (confidence * 100).toFixed(1) + "%";
                const textX = Math.round((width - ctx.measureText(text).width) / 2);
                const textY = height / 1.5;

                ctx.fillText(text, textX, textY);
                ctx.save();
            }
        }]
    });
}

// ===================================
// Download Results
// ===================================

function downloadResults() {
    if (!AppState.lastResults) {
        showNotification('No results to download', 'error');
        return;
    }

    const dataStr = JSON.stringify(AppState.lastResults, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = `voice-analysis-${Date.now()}.json`;
    a.click();

    URL.revokeObjectURL(url);
    showNotification('Results downloaded!', 'success');
}

// ===================================
// Batch Analysis
// ===================================

function initializeBatchAnalysis() {
    const batchUploadArea = document.getElementById('batch-upload-area');
    const batchFilesInput = document.getElementById('batch-files');
    const processBatchBtn = document.getElementById('process-batch-btn');

    batchUploadArea.addEventListener('click', () => {
        batchFilesInput.click();
    });

    batchFilesInput.addEventListener('change', (e) => {
        handleBatchFilesSelect(e.target.files);
    });

    processBatchBtn.addEventListener('click', () => {
        processBatchFiles();
    });
}

function handleBatchFilesSelect(files) {
    if (files.length === 0) return;

    AppState.batchFiles = Array.from(files);

    const fileListEl = document.getElementById('batch-file-list');
    const processBatchBtn = document.getElementById('process-batch-btn');

    fileListEl.innerHTML = `
        <div class="batch-file-list">
            <p><strong>${files.length} files selected</strong></p>
            ${Array.from(files).map((f, i) => `
                <div class="file-item">
                    <span>${i + 1}. ${f.name}</span>
                    <span>${(f.size / 1024).toFixed(1)} KB</span>
                </div>
            `).join('')}
        </div>
    `;

    fileListEl.classList.remove('hidden');
    processBatchBtn.classList.remove('hidden');
}

async function processBatchFiles() {
    const language = document.getElementById('batch-language').value;
    const progressEl = document.getElementById('batch-progress');
    const progressFill = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');
    const resultsEl = document.getElementById('batch-results');

    progressEl.classList.remove('hidden');

    const results = [];

    for (let i = 0; i < AppState.batchFiles.length; i++) {
        const file = AppState.batchFiles[i];
        const progress = ((i + 1) / AppState.batchFiles.length) * 100;

        progressFill.style.width = progress + '%';
        progressText.textContent = `Processing ${file.name}... (${i + 1}/${AppState.batchFiles.length})`;

        try {
            const result = await analyzeAudioAPI(file, language);
            results.push({
                file: file.name,
                classification: result.classification,
                confidence: (result.confidenceScore * 100).toFixed(1) + '%',
                explanation: result.explanation
            });
        } catch (error) {
            results.push({
                file: file.name,
                classification: 'ERROR',
                confidence: 'N/A',
                explanation: error.message
            });
        }
    }

    progressText.textContent = '✅ Batch processing complete!';
    displayBatchResults(results, resultsEl);
}

function displayBatchResults(results, container) {
    const aiCount = results.filter(r => r.classification === 'AI_GENERATED').length;
    const humanCount = results.filter(r => r.classification === 'HUMAN').length;
    const errorCount = results.filter(r => r.classification === 'ERROR').length;

    container.innerHTML = `
        <div class="card">
            <h3>📊 Batch Analysis Results</h3>
            
            <div class="batch-stats">
                <div class="stat-card">
                    <div class="stat-value">${aiCount}</div>
                    <div class="stat-label">AI Generated</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${humanCount}</div>
                    <div class="stat-label">Human Voice</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${errorCount}</div>
                    <div class="stat-label">Errors</div>
                </div>
            </div>
            
            <table class="results-table">
                <thead>
                    <tr>
                        <th>File</th>
                        <th>Classification</th>
                        <th>Confidence</th>
                    </tr>
                </thead>
                <tbody>
                    ${results.map(r => `
                        <tr>
                            <td>${r.file}</td>
                            <td>${r.classification}</td>
                            <td>${r.confidence}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
            
            <button class="btn btn-secondary btn-block" onclick="downloadBatchResults()">
                📥 Download Batch Results (CSV)
            </button>
        </div>
    `;

    container.classList.remove('hidden');
    AppState.batchResults = results;
}

function downloadBatchResults() {
    if (!AppState.batchResults) return;

    const csv = [
        ['File', 'Classification', 'Confidence', 'Explanation'],
        ...AppState.batchResults.map(r => [
            r.file,
            r.classification,
            r.confidence,
            r.explanation
        ])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = `batch-results-${Date.now()}.csv`;
    a.click();

    URL.revokeObjectURL(url);
    showNotification('Batch results downloaded!', 'success');
}

// ===================================
// Notification System
// ===================================

function showNotification(message, type = 'info') {
    // Create toast notification
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'error' ? 'var(--danger)' : type === 'success' ? 'var(--success)' : 'var(--secondary)'};
        color: white;
        padding: 16px 24px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    toast.textContent = message;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('hide');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ===================================
// Particle Background
// ===================================

function createParticles() {
    const container = document.getElementById('particles-bg');
    const particleCount = 30;

    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.style.cssText = `
            position: absolute;
            width: 4px;
            height: 4px;
            background: rgba(102, 126, 234, 0.3);
            border-radius: 50%;
            top: ${Math.random() * 100}%;
            left: ${Math.random() * 100}%;
            animation: float ${5 + Math.random() * 10}s ease-in-out infinite;
            animation-delay: ${Math.random() * 5}s;
        `;
        container.appendChild(particle);
    }
}
