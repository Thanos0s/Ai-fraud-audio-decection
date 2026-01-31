# Common Voice Download Guide - Exact Datasets to Install

## 🎯 Which Voices to Download from Common Voice

Your AI Voice Detection system supports **5 languages**. Here's exactly what to download:

---

## 📥 Step-by-Step Download Instructions

### 1. Visit Common Voice Website
**URL**: https://commonvoice.mozilla.org/en/datasets

### 2. Download These Specific Datasets:

#### **Language 1: ENGLISH** 🇬🇧🇺🇸
- **Dataset Name**: "English"
- **Version**: Latest (20.0 or higher)
- **Size**: ~100 GB (full) or ~10 GB (validated clips only - recommended)
- **Download**: Click "English" → Download "Validated" split
- **What you get**: Thousands of English voice clips from native speakers
- **Use for**: General English voice detection

#### **Language 2: TAMIL** 🇮🇳 (தமிழ்)
- **Dataset Name**: "Tamil" (ta)
- **Version**: Latest available
- **Size**: ~5-10 GB
- **Download**: Click "Tamil" → Download "Validated" split
- **What you get**: Tamil speakers from India
- **Use for**: Tamil language voice detection

#### **Language 3: HINDI** 🇮🇳 (हिन्दी)
- **Dataset Name**: "Hindi" (hi)
- **Version**: Latest available
- **Size**: ~10-15 GB
- **Download**: Click "Hindi" → Download "Validated" split
- **What you get**: Hindi speakers from India
- **Use for**: Hindi language voice detection

#### **Language 4: MALAYALAM** 🇮🇳 (മലയാളം)
- **Dataset Name**: "Malayalam" (ml)
- **Version**: Latest available
- **Size**: ~3-5 GB (smaller dataset)
- **Download**: Click "Malayalam" → Download "Validated" split
- **What you get**: Malayalam speakers from Kerala, India
- **Use for**: Malayalam language voice detection

#### **Language 5: TELUGU** 🇮🇳 (తెలుగు)
- **Dataset Name**: "Telugu" (te)
- **Version**: Latest available
- **Size**: ~3-5 GB
- **Download**: Click "Telugu" → Download "Validated" split
- **What you get**: Telugu speakers from Andhra Pradesh/Telangana, India
- **Use for**: Telugu language voice detection

---

## 🎯 Quick Selection Guide

### **For Testing (Fast Start - 2 GB total)**
Download **ONLY English**:
- English (validated) - ~1-2 GB
- Use 100-200 clips for training
- **Time**: 30 minutes download + setup

### **For Production (All Languages - 30 GB total)**
Download **ALL 5 languages**:
- English - ~10 GB
- Tamil - ~5 GB
- Hindi - ~10 GB
- Malayalam - ~3 GB
- Telugu - ~3 GB
- **Time**: 2-4 hours download + setup

### **Recommended: Start with 1-2 Languages**
- English + Tamil (or your primary languages)
- **Time**: 1 hour download + setup
- Add more languages later as needed

---

## 📦 What You'll Download

Each dataset contains:
- **MP3 audio files** - Voice recordings (3-10 seconds each)
- **validated.tsv** - Metadata file listing validated clips
- **clips folder** - Contains all the audio files
- **Other files** - Test/dev splits (optional)

---

## 💾 Download Steps (Detailed)

### Step 1: Go to Common Voice
1. Open browser: https://commonvoice.mozilla.org/en/datasets
2. You'll see a list of languages

### Step 2: Select Language
1. Scroll to find your language (e.g., "English")
2. Click on the language name

### Step 3: Choose Version
1. Select the latest version (e.g., "Common Voice Corpus 20.0")
2. Click the download button

### Step 4: Download Splits
You'll see different splits:
- **validated** ✅ **DOWNLOAD THIS** - Pre-validated good quality clips
- **invalidated** ❌ Skip - Rejected clips
- **other** ⚠️ Optional - Unvalidated clips
- **test/dev/train** 📊 Optional - Pre-split datasets

**Download the "validated" or "train" split for best results.**

### Step 5: Wait for Download
- Files are large (TB format - compressed)
- Download time: 10 minutes - 2 hours depending on language

### Step 6: Extract Files
```bash
# Windows - Use 7-Zip or WinRAR
# Right-click → Extract here

# Extract to a temporary folder first
# Inside you'll find: clips folder + TSV files
```

---

## 📂 How to Organize After Download

### Automatic Organization Script

Create `scripts/organize_commonvoice.py`:

```python
import os
import shutil
from pathlib import Path
import pandas as pd
import random

def organize_common_voice(cv_extract_path, language, num_samples=100):
    """
    Organize Common Voice dataset into training structure
    
    Args:
        cv_extract_path: Path where you extracted Common Voice (e.g., 'C:/Downloads/cv-corpus-20.0-2024-12-06/en')
        language: Language name ('english', 'tamil', 'hindi', 'malayalam', 'telugu')
        num_samples: Number of samples to copy (default 100)
    """
    
    # Read validated.tsv to get list of good clips
    tsv_path = Path(cv_extract_path) / 'validated.tsv'
    if not tsv_path.exists():
        tsv_path = Path(cv_extract_path) / 'train.tsv'
    
    df = pd.read_csv(tsv_path, sep='\t')
    
    # Get random sample of clips
    sample_clips = df['path'].sample(min(num_samples, len(df))).tolist()
    
    # Source and destination
    clips_dir = Path(cv_extract_path) / 'clips'
    dest_dir = Path('data/train/human') / language.lower()
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy files
    copied = 0
    for clip_name in sample_clips:
        src = clips_dir / clip_name
        if src.exists():
            # Copy and rename
            dest = dest_dir / f'cv_{copied:04d}.mp3'
            shutil.copy2(src, dest)
            copied += 1
            
            if copied % 10 == 0:
                print(f'Copied {copied}/{num_samples} files...')
    
    print(f'✅ Copied {copied} {language} voice samples!')
    print(f'📁 Location: {dest_dir}')

# Example usage:
if __name__ == '__main__':
    # MODIFY THESE PATHS TO YOUR DOWNLOADS
    
    # English
    organize_common_voice(
        cv_extract_path='C:/Users/YourName/Downloads/cv-corpus-20.0-2024-12-06/en',
        language='english',
        num_samples=200
    )
    
    # Tamil
    # organize_common_voice(
    #     cv_extract_path='C:/Users/YourName/Downloads/cv-corpus-20.0-2024-12-06/ta',
    #     language='tamil',
    #     num_samples=200
    # )
    
    # Add more languages as needed...
```

### Manual Organization Steps

1. **Extract the downloaded .tar.gz file**
   - You'll get a folder like: `cv-corpus-20.0-2024-12-06/en/`

2. **Inside you'll find**:
   ```
   cv-corpus-20.0-2024-12-06/en/
   ├── clips/           ← Audio files here!
   │   ├── common_voice_en_12345.mp3
   │   ├── common_voice_en_12346.mp3
   │   └── ...
   ├── validated.tsv    ← List of good clips
   └── other files...
   ```

3. **Copy audio files to your project**:
   - From: `cv-corpus-20.0-2024-12-06/en/clips/`
   - To: `ai-voice-detection/data/train/human/english/`
   - Copy 100-200 random MP3 files

4. **Repeat for each language**:
   - Tamil → `data/train/human/tamil/`
   - Hindi → `data/train/human/hindi/`
   - Malayalam → `data/train/human/malayalam/`
   - Telugu → `data/train/human/telugu/`

---

## 🎯 How Many Files to Copy?

| Purpose | Files per Language | Total Dataset Size | Training Time |
|---------|-------------------|-------------------|---------------|
| **Quick Test** | 50-100 | ~500 files | 5-10 minutes |
| **Development** | 200-500 | ~2,000 files | 20-30 minutes |
| **Production** | 1000+ | ~5,000+ files | 1-2 hours |

**Recommended for your first training: 100-200 files per language**

---

## ✅ Verification Checklist

After organizing, your structure should look like:

```
data/train/human/
├── english/
│   ├── cv_0000.mp3
│   ├── cv_0001.mp3
│   ├── ...
│   └── cv_0099.mp3    (100 files)
├── tamil/
│   ├── cv_0000.mp3
│   └── ...
├── hindi/
│   └── ...
├── malayalam/
│   └── ...
└── telugu/
    └── ...
```

**Check:**
- [ ] Each language folder has 100+ MP3 files
- [ ] Files are between 3-30 seconds long
- [ ] Audio plays correctly
- [ ] No corrupted files

---

## 🚀 After Download & Organization

1. **Generate AI samples**:
   ```bash
   python scripts/generate_ai_samples.py
   ```

2. **Verify data structure**:
   ```bash
   python scripts/organize_data.py
   ```

3. **Train the model**:
   ```bash
   python scripts/train_model.py
   ```

---

## 💡 Pro Tips

1. **Start with English only** - It has the most data and trains fastest
2. **Use the organization script** - Saves hours of manual work
3. **Download "validated" split** - Pre-filtered for quality
4. **Don't download everything** - 100-200 samples is enough to start
5. **Test before downloading all languages** - Make sure your system works with one language first

---

## 🔗 Direct Download Links

Once on https://commonvoice.mozilla.org/en/datasets:

1. **English**: Search "English" → Download latest → Choose "validated"
2. **Tamil**: Search "Tamil" (ta) → Download latest → Choose "validated"  
3. **Hindi**: Search "Hindi" (hi) → Download latest → Choose "validated"
4. **Malayalam**: Search "Malayalam" (ml) → Download latest → Choose "validated"
5. **Telugu**: Search "Telugu" (te) → Download latest → Choose "validated"

---

## ⏱️ Time Estimates

| Task | Time Required |
|------|--------------|
| Download 1 language | 10-30 minutes |
| Download all 5 languages | 1-3 hours |
| Extract files | 5-15 minutes |
| Organize files (manual) | 30-60 minutes |
| Organize files (script) | 5 minutes |
| **Total (1 language)** | **45 minutes - 1.5 hours** |
| **Total (all languages)** | **2-4 hours** |

---

## 🎯 Quick Start Recommendation

**For your first run, do this:**

1. Download **English only** (fastest, most data available)
2. Extract and copy **100 files** to `data/train/human/english/`
3. Run `python scripts/generate_ai_samples.py` (generates AI voices for all languages)
4. Train with: `python scripts/train_model.py`
5. Test it!
6. If it works well, download more languages

**This gets you working in under 1 hour!**
