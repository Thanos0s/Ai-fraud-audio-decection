/**
 * API Integration Module
 * Handles all backend API calls
 */

// ===================================
// Voice Detection API
// ===================================

async function analyzeAudioAPI(audioFile, language) {
    try {
        // Convert file to base64
        const base64Audio = await fileToBase64(audioFile);

        // Prepare request
        const payload = {
            language: language,
            audioFormat: 'mp3',
            audioBase64: base64Audio
        };

        const response = await axios.post(AppState.apiUrl, payload, {
            headers: {
                'Content-Type': 'application/json',
                'x-api-key': AppState.apiKey
            },
            timeout: 30000 // 30 seconds
        });

        return response.data;

    } catch (error) {
        handleAPIError(error);
        throw error;
    }
}

// ===================================
// Call Security Analysis API
// ===================================

async function analyzeSecurityAPI(audioFile, language) {
    try {
        const base64Audio = await fileToBase64(audioFile);

        // Use the call-analysis endpoint
        const securityUrl = AppState.apiUrl.replace('/voice-detection', '/call-analysis');

        const payload = {
            language: language,
            audioFormat: 'mp3',
            audioBase64: base64Audio
        };

        const response = await axios.post(securityUrl, payload, {
            headers: {
                'Content-Type': 'application/json',
                'x-api-key': AppState.apiKey
            },
            timeout: 30000
        });

        return response.data;

    } catch (error) {
        handleAPIError(error);
        throw error;
    }
}

// ===================================
// File to Base64 Conversion
// ===================================

function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();

        reader.onload = () => {
            // Remove data URL prefix (data:audio/mp3;base64,)
            const base64 = reader.result.split(',')[1];
            resolve(base64);
        };

        reader.onerror = () => {
            reject(new Error('Failed to read file'));
        };

        reader.readAsDataURL(file);
    });
}

// ===================================
// Blob to Base64 (for recorded audio)
// ===================================

function blobToBase64(blob) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();

        reader.onload = () => {
            const base64 = reader.result.split(',')[1];
            resolve(base64);
        };

        reader.onerror = () => {
            reject(new Error('Failed to convert blob'));
        };

        reader.readAsDataURL(blob);
    });
}

// ===================================
// Error Handling
// ===================================

function handleAPIError(error) {
    console.error('API Error:', error);

    if (error.response) {
        // Server responded with error
        const status = error.response.status;
        const data = error.response.data;

        if (status === 401) {
            throw new Error('Invalid API key. Please check your configuration.');
        } else if (status === 400) {
            throw new Error(data.message || 'Bad request. Please check your audio file.');
        } else if (status === 500) {
            throw new Error('Server error. Please try again later.');
        } else {
            throw new Error(`API error: ${status}`);
        }
    } else if (error.request) {
        // Request made but no response
        throw new Error('Cannot connect to backend. Please check the API URL and ensure the server is running.');
    } else {
        // Something else happened
        throw new Error(error.message || 'Unknown error occurred');
    }
}

// ===================================
// Health Check
// ===================================

async function checkBackendHealth() {
    try {
        const healthUrl = AppState.apiUrl.replace('/api/voice-detection', '/health');
        const response = await axios.get(healthUrl, { timeout: 5000 });
        return response.data;
    } catch (error) {
        console.warn('Backend health check failed:', error.message);
        return null;
    }
}

// Run health check on load
document.addEventListener('DOMContentLoaded', async () => {
    const health = await checkBackendHealth();
    if (health) {
        console.log('✅ Backend is online:', health);
    } else {
        console.warn('⚠️ Backend may be offline or unreachable');
        showNotification('Backend connection not verified. Please check API settings.', 'warning');
    }
});
