"""
Organize Common Voice Dataset into Training Structure
Automatically copies files from downloaded Common Voice to training folders
"""
import os
import shutil
from pathlib import Path
import pandas as pd
import random


def organize_common_voice(cv_extract_path, language, num_samples=100):
    """
    Organize Common Voice dataset into training structure
    
    Args:
        cv_extract_path: Path where you extracted Common Voice 
                        (e.g., 'C:/Downloads/cv-corpus-20.0-2024-12-06/en')
        language: Language name ('english', 'tamil', 'hindi', 'malayalam', 'telugu')
        num_samples: Number of samples to copy (default 100)
    
    Example:
        organize_common_voice(
            cv_extract_path='C:/Users/YourName/Downloads/cv-corpus-20/en',
            language='english',
            num_samples=200
        )
    """
    
    cv_path = Path(cv_extract_path)
    
    if not cv_path.exists():
        print(f"ERROR: Path not found: {cv_path}")
        print("Please check the path and try again.")
        return
    
    # Read validated.tsv to get list of good clips
    tsv_path = cv_path / 'validated.tsv'
    if not tsv_path.exists():
        tsv_path = cv_path / 'train.tsv'
    
    if not tsv_path.exists():
        print(f"ERROR: Could not find validated.tsv or train.tsv in {cv_path}")
        return
    
    print(f"Reading metadata from {tsv_path}...")
    df = pd.read_csv(tsv_path, sep='\t')
    
    # Get random sample of clips
    sample_size = min(num_samples, len(df))
    sample_clips = df['path'].sample(sample_size).tolist()
    
    # Source and destination
    clips_dir = cv_path / 'clips'
    dest_dir = Path('data/train/human') / language.lower()
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy files
    print(f"\nCopying {sample_size} files to {dest_dir}...")
    copied = 0
    skipped = 0
    
    for clip_name in sample_clips:
        src = clips_dir / clip_name
        if src.exists():
            # Copy and rename with sequential numbering
            dest = dest_dir / f'cv_{copied:04d}.mp3'
            shutil.copy2(src, dest)
            copied += 1
            
            if copied % 20 == 0:
                print(f'  Copied {copied}/{sample_size} files...')
        else:
            skipped += 1
    
    print(f"\n✅ Successfully copied {copied} {language} voice samples!")
    if skipped > 0:
        print(f"⚠️  Skipped {skipped} files (not found)")
    print(f"📁 Location: {dest_dir}")
    print()


def main():
    """
    Main function - EDIT THE PATHS BELOW to match your downloads
    """
    
    print("=" * 70)
    print("Common Voice Dataset Organizer")
    print("=" * 70)
    print()
    
    # ========================================================================
    # EDIT THESE PATHS TO MATCH WHERE YOU EXTRACTED COMMON VOICE DATASETS
    # ========================================================================
    
    # Example paths - CHANGE THESE to your actual download locations
    downloads = {
        # Uncomment and modify the languages you downloaded:
        
        'english': {
            'path': 'C:/Users/YourName/Downloads/cv-corpus-20.0-2024-12-06/en',
            'samples': 200  # Number of files to copy
        },
        
        # 'tamil': {
        #     'path': 'C:/Users/YourName/Downloads/cv-corpus-20.0-2024-12-06/ta',
        #     'samples': 200
        # },
        
        # 'hindi': {
        #     'path': 'C:/Users/YourName/Downloads/cv-corpus-20.0-2024-12-06/hi',
        #     'samples': 200
        # },
        
        # 'malayalam': {
        #     'path': 'C:/Users/YourName/Downloads/cv-corpus-20.0-2024-12-06/ml',
        #     'samples': 150
        # },
        
        # 'telugu': {
        #     'path': 'C:/Users/YourName/Downloads/cv-corpus-20.0-2024-12-06/te',
        #     'samples': 150
        # },
    }
    
    # ========================================================================
    
    # Process each language
    processed = 0
    for language, config in downloads.items():
        print(f"\nProcessing {language.upper()}...")
        print("-" * 70)
        
        organize_common_voice(
            cv_extract_path=config['path'],
            language=language,
            num_samples=config['samples']
        )
        processed += 1
    
    print("=" * 70)
    print(f"✨ Complete! Processed {processed} language(s)")
    print()
    print("Next steps:")
    print("1. Generate AI samples: python scripts/generate_ai_samples.py")
    print("2. Train the model: python scripts/train_model.py")
    print("=" * 70)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease check:")
        print("1. Did you edit the paths in this script to match your downloads?")
        print("2. Did you extract the .tar.gz files?")
        print("3. Do the paths exist and contain clips folder + validated.tsv?")
