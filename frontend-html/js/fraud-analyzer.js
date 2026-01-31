/**
 * Fraud Analyzer Module
 * Handles call security analysis with 3D visualization
 */

// ===================================
// Initialize Security Tab
// ===================================

document.addEventListener('DOMContentLoaded', () => {
    initializeSecurityAnalyzer();
    initialize3DRiskSphere();
});

function initializeSecurityAnalyzer() {
    const uploadBtn = document.getElementById('security-upload-btn');
    const recordBtn = document.getElementById('security-record-btn');
    const fileInput = document.getElementById('security-file');
    const scanBtn = document.getElementById('scan-threats-btn');

    uploadBtn.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleSecurityFileSelect(e.target.files[0]);
        }
    });

    recordBtn.addEventListener('click', () => {
        // Switch to recording tab for now
        // In a production app, you'd implement recording here too
        showNotification('Please use the Live Recording tab to record audio, then upload it here', 'info');
    });

    scanBtn.addEventListener('click', () => {
        scanForThreats();
    });
}

function handleSecurityFileSelect(file) {
    if (!file.name.endsWith('.mp3')) {
        showNotification('Please upload an MP3 file', 'error');
        return;
    }

    AppState.securityAudioFile = file;

    const audioPreview = document.getElementById('security-audio-preview');
    const scanBtn = document.getElementById('scan-threats-btn');

    audioPreview.src = URL.createObjectURL(file);
    audioPreview.classList.remove('hidden');
    scanBtn.classList.remove('hidden');

    console.log('Security file selected:', file.name);
}

// ===================================
// Scan for Threats
// ===================================

async function scanForThreats() {
    const language = document.getElementById('security-language').value;

    if (!AppState.securityAudioFile) {
        showNotification('Please select an audio file first', 'error');
        return;
    }

    const scanBtn = document.getElementById('scan-threats-btn');
    scanBtn.disabled = true;
    scanBtn.textContent = '🔄 Scanning...';

    try {
        const result = await analyzeSecurityAPI(AppState.securityAudioFile, language);
        displaySecurityResults(result);
        showNotification('Security scan complete!', 'success');
    } catch (error) {
        showNotification(error.message, 'error');
    } finally {
        scanBtn.disabled = false;
        scanBtn.innerHTML = '<span class="btn-icon">🛡️</span> Scan for Threats';
    }
}

// ===================================
// Display Security Results
// ===================================

function displaySecurityResults(data) {
    const container = document.getElementById('security-results');
    const sphereContainer = document.getElementById('risk-sphere-container');

    // Extract data
    const voiceAnalysis = data.voice_analysis || {};
    const fraudAnalysis = data.fraud_analysis || {};
    const transcriptData = data.transcript_data || {};

    const classification = voiceAnalysis.classification || 'UNKNOWN';
    const confidence = voiceAnalysis.confidence || 0;
    const riskScore = fraudAnalysis.risk_score || 0;
    const riskLevel = fraudAnalysis.risk_level || 'UNKNOWN';
    const alerts = fraudAnalysis.alerts || [];
    const keywords = transcriptData.keywords_found || [];
    const transcript = transcriptData.transcript || '';

    // Determine threat level color
    const threatColors = {
        'LOW': 'low',
        'MEDIUM': 'medium',
        'HIGH': 'high',
        'CRITICAL': 'critical'
    };

    const threatClass = threatColors[riskLevel] || 'low';

    // Build results HTML
    container.innerHTML = `
        <div class="card">
            <div class="threat-level-banner ${threatClass}">
                🛡️ THREAT LEVEL: ${riskLevel}
            </div>
            
            <div class="risk-score-display">
                <p style="font-size: 1.2rem; color: var(--text-secondary); margin-bottom: 8px;">Risk Score</p>
                <div class="risk-score-value" style="color: ${getRiskColor(riskScore)};">
                    ${riskScore}/100
                </div>
            </div>
            
            <div class="grid-2" style="margin-top: 24px;">
                <div>
                    <h4>🔍 Voice Analysis</h4>
                    <p><strong>Classification:</strong> ${classification}</p>
                    <p><strong>Confidence:</strong> ${(confidence * 100).toFixed(1)}%</p>
                    <p><strong>AI Probability:</strong> ${classification === 'AI_GENERATED' ? (confidence * 100).toFixed(1) : ((1 - confidence) * 100).toFixed(1)}%</p>
                </div>
                
                <div>
                    <h4>⚠️ Risk Metrics</h4>
                    <p><strong>Overall Score:</strong> ${riskScore}/100</p>
                    <p><strong>AI Detection:</strong> ${fraudAnalysis.ai_detection_score || 0}/100</p>
                    <p><strong>Urgency:</strong> ${fraudAnalysis.urgency_score || 0}/100</p>
                </div>
            </div>
            
            ${keywords.length > 0 ? `
                <div style="margin-top: 24px;">
                    <h4>🚨 Suspicious Keywords Detected</h4>
                    <div class="keywords-detected">
                        ${keywords.map(kw => `<span class="keyword-tag">${kw}</span>`).join('')}
                    </div>
                </div>
            ` : ''}
            
            ${alerts.length > 0 ? `
                <div style="margin-top: 24px;">
                    <h4>🔔 Security Alerts</h4>
                    <ul style="padding-left: 20px; color: var(--text-secondary);">
                        ${alerts.map(alert => `<li>${alert}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
            
            ${transcript ? `
                <div class="transcript-box">
                    <h4 style="margin-bottom: 12px;">📝 Transcript</h4>
                    <p class="transcript-text">${transcript}</p>
                </div>
            ` : ''}
            
            <button class="btn btn-secondary btn-block" onclick="downloadSecurityReport()" style="margin-top: 24px;">
                📥 Download Security Report
            </button>
        </div>
    `;

    container.classList.remove('hidden');
    sphereContainer.classList.remove('hidden');

    // Update 3D risk sphere
    updateRiskSphere(riskScore);

    // Save results
    AppState.securityResults = data;
}

function getRiskColor(score) {
    if (score < 30) return 'var(--success)';
    if (score < 60) return 'var(--warning)';
    return 'var(--danger)';
}

// ===================================
// Download Security Report
// ===================================

function downloadSecurityReport() {
    if (!AppState.securityResults) {
        showNotification('No report to download', 'error');
        return;
    }

    const dataStr = JSON.stringify(AppState.securityResults, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = `security-report-${Date.now()}.json`;
    a.click();

    URL.revokeObjectURL(url);
    showNotification('Security report downloaded!', 'success');
}

// ===================================
// 3D Risk Sphere Visualization
// ===================================

let sphereScene, sphereCamera, sphereRenderer, riskSphere;

function initialize3DRiskSphere() {
    const canvas = document.getElementById('risk-sphere-canvas');
    if (!canvas) return;

    const container = document.getElementById('risk-sphere-container');

    // Setup Three.js scene
    sphereScene = new THREE.Scene();
    sphereCamera = new THREE.PerspectiveCamera(75, container.offsetWidth / container.offsetHeight, 0.1, 1000);
    sphereRenderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });

    sphereRenderer.setSize(container.offsetWidth, container.offsetHeight);
    sphereCamera.position.z = 5;

    // Create sphere
    const geometry = new THREE.SphereGeometry(2, 32, 32);
    const material = new THREE.MeshPhongMaterial({
        color: 0x09AB3B,
        emissive: 0x09AB3B,
        emissiveIntensity: 0.3,
        shininess: 100,
        transparent: true,
        opacity: 0.8
    });

    riskSphere = new THREE.Mesh(geometry, material);
    sphereScene.add(riskSphere);

    // Add lighting
    const light1 = new THREE.PointLight(0xffffff, 1, 100);
    light1.position.set(5, 5, 5);
    sphereScene.add(light1);

    const light2 = new THREE.AmbientLight(0x404040);
    sphereScene.add(light2);

    // Start animation
    animateRiskSphere();
}

function animateRiskSphere() {
    requestAnimationFrame(animateRiskSphere);

    if (riskSphere) {
        riskSphere.rotation.x += 0.005;
        riskSphere.rotation.y += 0.01;
    }

    if (sphereRenderer && sphereScene && sphereCamera) {
        sphereRenderer.render(sphereScene, sphereCamera);
    }
}

function updateRiskSphere(riskScore) {
    if (!riskSphere) return;

    // Change color based on risk score
    let color, emissive;

    if (riskScore < 30) {
        color = 0x09AB3B; // Green
        emissive = 0x09AB3B;
    } else if (riskScore < 60) {
        color = 0xFFA500; // Orange
        emissive = 0xFFA500;
    } else {
        color = 0xFF4B4B; // Red
        emissive = 0xFF4B4B;
    }

    riskSphere.material.color.setHex(color);
    riskSphere.material.emissive.setHex(emissive);
    riskSphere.material.emissiveIntensity = 0.5;

    // Pulsate based on risk
    const pulseSpeed = riskScore / 100;
    animateRiskSpherePulse(pulseSpeed);
}

function animateRiskSpherePulse(speed) {
    const animate = () => {
        if (!riskSphere) return;

        const time = Date.now() * 0.001 * speed;
        const scale = 1 + Math.sin(time) * 0.1;
        riskSphere.scale.set(scale, scale, scale);

        requestAnimationFrame(animate);
    };

    animate();
}

// Handle window resize
window.addEventListener('resize', () => {
    if (sphereRenderer && sphereCamera) {
        const container = document.getElementById('risk-sphere-container');
        if (container && container.offsetWidth > 0) {
            sphereCamera.aspect = container.offsetWidth / container.offsetHeight;
            sphereCamera.updateProjectionMatrix();
            sphereRenderer.setSize(container.offsetWidth, container.offsetHeight);
        }
    }
});
