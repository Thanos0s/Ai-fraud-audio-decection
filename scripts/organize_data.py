"""
Organize audio dataset into proper directory structure
"""
import os
from pathlib import Path


def organize_dataset():
    """
    Create directory structure for training data
    """
    languages = ['tamil', 'english', 'hindi', 'malayalam', 'telugu']
    categories = ['ai_generated', 'human']
    
    base_path = Path('data/train')
    
    for category in categories:
        for lang in languages:
            path = base_path / category / lang
            path.mkdir(parents=True, exist_ok=True)
            print(f"✓ Created: {path}")
    
    # Create test directory
    test_path = Path('data/test')
    test_path.mkdir(parents=True, exist_ok=True)
    print(f"✓ Created: {test_path}")
    
    print("\n✅ Data structure created successfully!")
    print("\nNext steps:")
    print("1. Add human voice samples to data/train/human/<language>/")
    print("2. Run generate_ai_samples.py to create AI voice samples")


if __name__ == '__main__':
    organize_dataset()
