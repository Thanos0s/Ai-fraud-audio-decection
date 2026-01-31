# Training Data Checklist

## Current Status

### AI Voices (Generated) ✅
- Tamil: 5 samples
- English: 5 samples
- Hindi: 5 samples
- Malayalam: 5 samples
- Telugu: 5 samples
- **Total: 25 AI samples**

### Human Voices (MISSING) ❌
- Tamil: **0 samples** 
- English: **0 samples**
- Hindi: **0 samples**
- Malayalam: **0 samples**
- Telugu: **0 samples**
- **Total: 0 human samples**

## ⚠️ Cannot Train Yet

**Problem:** No human voice files found in `data/train/human/<language>/`

**Solution:** Add human voice MP3 files to these folders

---

## 🎯 Next Steps: Add Human Voices

### Option 1: Use Common Voice Files (Best)

If you downloaded Common Voice:

1. **Extract the .tar.gz file**
   - Example: `cv-corpus-20.0-2024-12-06-en.tar.gz`
   - Extract to: `C:/Downloads/cv-corpus-20/en/`

2. **Find the clips folder**
   - Location: `C:/Downloads/cv-corpus-20/en/clips/`
   - Contains thousands of MP3 files

3. **Copy files to your project**
   - Copy 50-100 MP3 files from clips folder
   - Paste into: `ai-voice-detection/data/train/human/english/`

4. **Use the script (easier)**
   ```bash
   # Edit scripts/organize_commonvoice.py first
   # Set the path to your extracted Common Voice folder
   python scripts/organize_commonvoice.py
   ```

### Option 2: Record Yourself (Quick Test)

1. Open the frontend: http://localhost:8501
2. Go to "Live Recording" tab  
3. Record 25+ voice samples (10 seconds each)
4. Save each one as: `data/train/human/english/recording_XX.mp3`

### Option 3: Use Any MP3 Files Temporarily

For quick testing:
- Copy ANY human voice MP3 files you have
- Put them in `data/train/human/english/`
- Minimum 25 files to match the AI samples

---

## 📊 Minimum Requirements

| Category | Minimum | Recommended |
|----------|---------|-------------|
| **AI samples** | ✅ 25 | 100+ |
| **Human samples** | ❌ **0 (need 25+)** | 100+ |
| **Total** | Need 50+ | 200+ |

---

## ✅ When Ready

Once you have human voice files in place:

```bash
# Check data
python -c "import os; print('Human files:', len(os.listdir('data/train/human/english')))"

# Train model
python scripts/train_model.py
```

---

## 🗂️ Correct Folder Structure

```
data/train/
├── ai_generated/
│   └── english/
│       ├── sample_english_gtts_1.mp3 ✅
│       ├── sample_english_gtts_2.mp3 ✅
│       ├── ... (25 total) ✅
│
└── human/
    └── english/
        ├── YOUR_FILES_HERE.mp3 ❌ (0 files!)
        ├── cv_0001.mp3 ← Add files like this
        ├── cv_0002.mp3
        └── ... need 25+ files
```

---

## 💡 Quick Solution

**Just want to test?** 

1. Download 50 English clips from Common Voice
2. Extract and copy to `data/train/human/english/`
3. Run `python scripts/train_model.py`
4. Done in 30 minutes!
