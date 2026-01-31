# AI Voice Detection System - What You Need

## ✅ Currently Working
- Backend API (http://localhost:8000) - Demo mode
- Frontend UI (http://localhost:8501) - Fully functional
- Live microphone recording feature
- File upload & batch processing

## ❌ What's Missing (To make it fully workable)

### 1. **FFmpeg** (Audio Processing - CRITICAL)
**Windows:**
```powershell
choco install ffmpeg
# Or download from: https://ffmpeg.org/download.html
```

### 2. **Training Data** (CRITICAL for accurate predictions)

**Human Voices (FREE):**
- Download from: https://commonvoice.mozilla.org/
- Need: 100+ samples per language
- Place in: `data/train/human/<language>/`

**AI Voices (FREE):**
```bash
python scripts/generate_ai_samples.py
```

### 3. **Train the Model**
```bash
python scripts/train_model.py
```

## 🎯 Quick Start (Minimum to get it working)

**Option 1: Test with 50 samples** (~1 hour)
1. Install FFmpeg
2. Download 50 human voice clips (English only)
3. Generate 50 AI samples: `python scripts/generate_ai_samples.py`
4. Train: `python scripts/train_model.py`
5. Restart backend - now it works with real predictions!

**Option 2: Production quality** (~1 day)
1. Install FFmpeg
2. Download 500+ samples per language from Common Voice
3. Use ElevenLabs API ($5/month) for better AI voices
4. Train model with full dataset
5. Deploy to cloud (AWS/GCP/Azure)

## 💰 Cost Summary

**FREE Option:**
- Mozilla Common Voice (human voices) - Free
- gTTS (AI voices) - Free
- Total: **$0**

**Paid Option (Better Quality):**
- ElevenLabs API for AI voices - $5/month
- Optional cloud hosting - $10-50/month
- Total: **$15-55/month**

## 📦 API Keys Needed (Optional)

**For Better AI Voice Generation:**
1. **ElevenLabs** - https://elevenlabs.io/ ($5/month)
2. **Google Cloud TTS** - https://cloud.google.com/text-to-speech (Free tier available)
3. **Azure Speech** - https://azure.microsoft.com/ (Free tier available)

**Current system works with gTTS (already free, no API key needed)**

## ✅ What's Already Set Up

- ✅ All code written
- ✅ Dependencies listed
- ✅ Project structure created
- ✅ Frontend with live recording
- ✅ Backend API ready
- ✅ Docker files for deployment
- ✅ Documentation complete

## 🚫 What You DON'T Need

- ❌ Expensive GPUs (runs on CPU fine)
- ❌ Complex cloud setup (works locally)
- ❌ Database (optional, not required)
- ❌ Paid APIs (free options available)

## 📝 Next Steps

1. **Install FFmpeg** (5 minutes)
2. **Download human voice data** (30 minutes)
3. **Generate AI samples** (5 minutes) 
4. **Train model** (10-30 minutes depending on data size)
5. **Test it!**

See `REQUIREMENTS_GUIDE.md` for detailed instructions.
