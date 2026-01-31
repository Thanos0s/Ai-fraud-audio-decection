# Making the AI Voice Detection System Fully Workable

## 🎯 Current Status
✅ Backend API - Running in **demo mode** (random predictions)  
✅ Frontend UI - Fully functional with live recording  
❌ Trained Model - **NOT YET TRAINED** (needs data)

---

## 📋 What You Need

### 1️⃣ **Training Data** (CRITICAL - Required for real AI detection)

#### Human Voice Datasets (Free Sources):

**Option A: Mozilla Common Voice** (Recommended)
- **URL**: https://commonvoice.mozilla.org/
- **Languages**: Tamil, English, Hindi, Malayalam, Telugu
- **Size**: Thousands of validated voice clips
- **Format**: MP3/WAV
- **License**: CC0 (Public Domain)
- **How to get**:
  1. Visit https://commonvoice.mozilla.org/datasets
  2. Download datasets for your languages
  3. Extract and place in `data/train/human/<language>/`

**Option B: LibriSpeech** (English only)
- **URL**: https://www.openslr.org/12/
- **Size**: 1000 hours of read English speech
- **Quality**: High quality audiobook recordings

**Option C: MUCS (Indian Languages)**
- **URL**: https://github.com/AI4Bharat/MUCS
- **Languages**: Tamil, Hindi, Malayalam, Telugu
- **Type**: Multi-speaker conversational speech

**Option D: Google Speech Commands**
- **URL**: https://ai.google/tools/datasets/speech-commands/
- **Type**: Short spoken commands

#### AI-Generated Voice Samples:

You have two options:

**Option 1: Use gTTS (Already included - Free)**
```bash
# Already installed
python scripts/generate_ai_samples.py
```
This generates 5 samples per language using Google TTS.

**Option 2: Use Advanced TTS APIs (Better quality)**

1. **Google Cloud Text-to-Speech API**
   - **URL**: https://cloud.google.com/text-to-speech
   - **Pricing**: Free tier: 0-4M characters/month, then $4-$16 per 1M characters
   - **Quality**: Very high, multiple voices
   - **API Key**: Required (get from Google Cloud Console)
   
   ```python
   from google.cloud import texttospeech
   # Set GOOGLE_APPLICATION_CREDENTIALS environment variable
   ```

2. **ElevenLabs API** (Most realistic AI voices)
   - **URL**: https://elevenlabs.io/
   - **Pricing**: Free tier: 10,000 characters/month, paid from $5/month
   - **Quality**: State-of-the-art voice cloning
   - **API Key**: Required
   
   ```python
   import requests
   url = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
   headers = {"xi-api-key": "YOUR_API_KEY"}
   ```

3. **Azure Speech Services**
   - **URL**: https://azure.microsoft.com/en-us/services/cognitive-services/text-to-speech/
   - **Pricing**: Free tier: 5 million characters/month
   - **Quality**: High, supports many languages
   - **API Key**: Required (Azure subscription)

4. **Amazon Polly**
   - **URL**: https://aws.amazon.com/polly/
   - **Pricing**: Free tier: 5M characters/month for 12 months
   - **Quality**: High, neural voices available

5. **Coqui TTS** (Open Source - No API needed)
   - **URL**: https://github.com/coqui-ai/TTS
   - **Pricing**: FREE (run locally)
   - **Quality**: Good, open source
   
   ```bash
   pip install TTS
   tts --text "Hello" --model_name "tts_models/en/ljspeech/tacotron2-DDC"
   ```

---

### 2️⃣ **System Dependencies**

#### FFmpeg (REQUIRED for audio processing)

**Windows:**
```powershell
# Download from: https://ffmpeg.org/download.html
# Or use Chocolatey:
choco install ffmpeg

# Or use Scoop:
scoop install ffmpeg
```

**Linux:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg libsndfile1
```

**macOS:**
```bash
brew install ffmpeg
```

**Verify installation:**
```bash
ffmpeg -version
```

---

### 3️⃣ **Python Dependencies**

Already installed, but if needed:

```bash
# Backend
pip install fastapi uvicorn librosa soundfile pydub torch scikit-learn numpy pandas python-multipart pydantic python-dotenv

# Frontend
pip install streamlit requests plotly audio-recorder-streamlit

# Optional: For TTS generation
pip install gtts  # Google TTS (already installed)
pip install TTS   # Coqui TTS (advanced)
```

---

### 4️⃣ **API Keys & Configuration**

#### Current .env file:
```env
API_KEY=sk_test_voice_detection_2026
API_HOST=0.0.0.0
API_PORT=8000
MODEL_PATH=models/best_model.pt
SCALER_PATH=models/scaler.pkl
SAMPLE_RATE=16000
MAX_AUDIO_LENGTH=30
```

#### For Production - Add these:

```env
# TTS APIs (choose one or more)
GOOGLE_APPLICATION_CREDENTIALS=path/to/google-credentials.json
ELEVENLABS_API_KEY=your_elevenlabs_key
AZURE_SPEECH_KEY=your_azure_key
AZURE_REGION=eastus
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret

# Change default API key for security
API_KEY=sk_prod_your_secure_random_key_here

# For production deployment
ENVIRONMENT=production
ALLOWED_ORIGINS=https://yourdomain.com
```

---

## 🚀 Step-by-Step: Make It Fully Workable

### **Step 1: Install FFmpeg**
```bash
# Windows (with Chocolatey)
choco install ffmpeg

# Verify
ffmpeg -version
```

### **Step 2: Collect Human Voice Data**

**Quick Start (Small dataset for testing):**
```bash
# Download Common Voice sample
# Visit: https://commonvoice.mozilla.org/datasets
# Download Tamil/English/Hindi clips (start with ~100 each)
# Extract to: data/train/human/<language>/
```

**For Production (Large dataset):**
- Download 500+ samples per language
- Mix different speakers, accents, ages
- Ensure clean audio quality

### **Step 3: Generate AI Voice Samples**

**Option A: Use gTTS (Simple):**
```bash
python scripts/generate_ai_samples.py
```

**Option B: Use ElevenLabs (Better):**

Create `scripts/generate_ai_elevenlabs.py`:
```python
import os
import requests
from pathlib import Path

API_KEY = "your_elevenlabs_api_key"
VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice

texts = {
    'english': 'Hello, this is an AI-generated voice sample.',
    # Add more languages
}

for lang, text in texts.items():
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {"xi-api-key": API_KEY}
    data = {"text": text, "model_id": "eleven_monolingual_v1"}
    
    response = requests.post(url, json=data, headers=headers)
    
    output_dir = Path(f'data/train/ai_generated/{lang}')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / f'elevenlabs_sample.mp3', 'wb') as f:
        f.write(response.content)
```

### **Step 4: Train the Model**

```bash
# With at least 100 samples per category per language
python scripts/train_model.py
```

**Expected output:**
- Model saved to `models/best_model.pt`
- Training accuracy: 80%+ after 10 epochs
- Validation accuracy: 75%+ 

### **Step 5: Restart Backend with Trained Model**

```bash
# Backend will auto-load the model from models/best_model.pt
cd backend
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

You'll see: `Model loaded from models/best_model.pt` ✅

---

## 📊 Data Requirements Summary

| Component | Minimum | Recommended | Source |
|-----------|---------|-------------|---------|
| **Human Voices** | 50 per language | 500+ per language | Mozilla Common Voice |
| **AI Voices** | 50 per language | 200+ per language | gTTS / ElevenLabs |
| **Total Samples** | 100 per language | 700+ per language | Mixed sources |
| **Languages** | 1 (English) | All 5 languages | Tamil, English, Hindi, Malayalam, Telugu |
| **Audio Quality** | 16kHz, clear | 48kHz, studio quality | Any source |

---

## 💰 Cost Estimation

### **FREE Option** (Recommended for testing):
- ✅ Mozilla Common Voice - Free
- ✅ gTTS - Free
- ✅ Coqui TTS - Free (open source)
- **Total Cost: $0**

### **Paid Option** (Better quality):
- ElevenLabs: $5-$22/month
- Google Cloud TTS: $0-$20/month (depending on usage)
- **Total Cost: $5-$50/month**

### **Production Deployment**:
- AWS/GCP/Azure: $10-$100/month (depending on traffic)
- Domain + SSL: $10-$20/year
- **Total: $15-$120/month**

---

## 🔧 Optional Enhancements

### 1. **Database Integration**
Store analysis history:
```bash
pip install sqlalchemy psycopg2
# Set up PostgreSQL or MongoDB
```

### 2. **Authentication System**
```bash
pip install fastapi-users
# Add user registration/login
```

### 3. **Cloud Storage**
Store audio files:
```bash
pip install boto3  # For AWS S3
# Or google-cloud-storage for GCP
```

### 4. **Monitoring & Analytics**
```bash
pip install prometheus-client  # Metrics
pip install sentry-sdk  # Error tracking
```

---

## ✅ Verification Checklist

Before going to production:

**Data Collection:**
- [ ] Downloaded human voice datasets (100+ samples per language)
- [ ] Generated AI voice samples (100+ samples per language)
- [ ] Organized files in correct directory structure
- [ ] Verified audio quality (clear, no corruption)

**Model Training:**
- [ ] Installed all dependencies (torch, librosa, etc.)
- [ ] Trained model successfully
- [ ] Model accuracy > 80%
- [ ] Model saved to `models/best_model.pt`

**System Setup:**
- [ ] FFmpeg installed and working
- [ ] All Python packages installed
- [ ] Backend starts without errors
- [ ] Frontend connects to backend

**Testing:**
- [ ] Uploaded audio file works
- [ ] Live microphone recording works
- [ ] Batch processing works
- [ ] Results are accurate (not random)

**Production Ready:**
- [ ] Changed API key in .env
- [ ] Set up domain/hosting
- [ ] Configured HTTPS/SSL
- [ ] Added rate limiting
- [ ] Set up monitoring

---

## 🎯 Quick Start (Minimal Setup)

**Just want to test it quickly? Here's the absolute minimum:**

1. **Install FFmpeg**
2. **Get 50 human voices** (download from Common Voice)
3. **Generate 50 AI voices** (run `python scripts/generate_ai_samples.py`)
4. **Train model** (run `python scripts/train_model.py`)
5. **Done!** System will now make real predictions

**Time required:** ~2 hours (mostly downloading data)

---

## 📞 Need Help?

Common issues and solutions are in the main README.md file.

For specific API documentation:
- Google TTS: https://cloud.google.com/text-to-speech/docs
- ElevenLabs: https://docs.elevenlabs.io/
- Azure Speech: https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/
