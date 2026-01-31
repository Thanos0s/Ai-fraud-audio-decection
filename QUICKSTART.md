# 🚀 Quick Setup Guide

## Step 1: Install Dependencies

### Windows
```powershell
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# Install backend dependencies
pip install -r backend/requirements.txt

# Install frontend dependencies
pip install -r frontend/requirements.txt

# Install gTTS for AI sample generation
pip install gtts
```

### Linux/Mac
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt

# Install frontend dependencies
pip install -r frontend/requirements.txt

# Install gTTS for AI sample generation
pip install gtts
```

## Step 2: Generate Sample Data

```bash
# Generate AI voice samples (creates 5 samples per language)
python scripts/generate_ai_samples.py
```

**Important:** For a production model, you also need human voice samples:
- Download from Mozilla Common Voice: https://commonvoice.mozilla.org/
- Place in: `data/train/human/<language>/`

## Step 3: Train the Model (Optional)

If you have training data:
```bash
python scripts/train_model.py
```

**Note:** The system will work in demo mode without a trained model.

## Step 4: Run the Application

### Terminal 1 - Backend API
```bash
cd backend
python app.py
```
✅ Backend will start at: http://localhost:8000

### Terminal 2 - Frontend UI
```bash
cd frontend
streamlit run streamlit_app.py
```
✅ Frontend will start at: http://localhost:8501

## Step 5: Test the System

1. Open browser to http://localhost:8501
2. Upload an MP3 audio file (max 30 seconds)
3. Select language
4. Click "Analyze Voice"
5. View results!

## 🐳 Docker Quick Start (Alternative)

```bash
# Build and run everything
docker-compose up -d

# Access:
# - Frontend: http://localhost:8501
# - Backend: http://localhost:8000
# - API Docs: http://localhost:8000/docs

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## 🔑 API Key

Default API key is set in `.env`:
```
API_KEY=sk_test_voice_detection_2026
```

Change this for production use!

## 📝 Test API with cURL

```bash
# Create a test request
curl -X POST http://localhost:8000/api/voice-detection \
  -H "Content-Type: application/json" \
  -H "x-api-key: sk_test_voice_detection_2026" \
  -d '{
    "language": "English",
    "audioFormat": "mp3",
    "audioBase64": "BASE64_ENCODED_AUDIO..."
  }'
```

## 🎯 Next Steps

1. **Collect more training data** for better accuracy
2. **Train the model** with your dataset
3. **Customize** the UI in `frontend/streamlit_app.py`
4. **Deploy** to cloud (AWS, GCP, Azure)

## ❓ Troubleshooting

**Backend won't start:**
- Check if port 8000 is available
- Verify all dependencies are installed

**Frontend can't connect to backend:**
- Make sure backend is running
- Check API URL in sidebar settings

**Model not found:**
- Train the model first OR
- System will run in demo mode

**FFmpeg error:**
- Windows: Download from https://ffmpeg.org/
- Linux: `sudo apt-get install ffmpeg`
- Mac: `brew install ffmpeg`

## 📚 Full Documentation

See [README.md](README.md) for complete documentation.

---

**Ready to detect AI voices! 🎤**
