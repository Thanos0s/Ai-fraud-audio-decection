"""
Generate AI voice samples using various TTS engines
"""
import os
from pathlib import Path

# Note: Install gTTS with: pip install gtts
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    print("⚠️  gTTS not installed. Install with: pip install gtts")


def generate_samples():
    """Generate AI samples for all languages"""
    
    if not GTTS_AVAILABLE:
        print("Warning: gTTS not installed. Install with: pip install gtts")
        return
    
    # Sample texts for each language
    texts = {
        'tamil': 'வணக்கம், இது செயற்கை நுண்ணறிவு உருவாக்கிய குரல்.',
        'english': 'Hello, this is an AI-generated voice sample for testing purposes.',
        'hindi': 'नमस्ते, यह एक एआई द्वारा उत्पन्न आवाज का नमूना है।',
        'malayalam': 'ഹലോ, ഇത് AI സൃഷ്ടിച്ച ശബ്ദ സാമ്പിൾ ആണ്.',
        'telugu': 'హలో, ఇది AI ద్వారా సృష్టించబడిన వాయిస్ నమూనా.'
    }
    
    # Language codes for gTTS
    lang_codes = {
        'tamil': 'ta',
        'english': 'en',
        'hindi': 'hi',
        'malayalam': 'ml',
        'telugu': 'te'
    }
    
    output_dir = Path('data/train/ai_generated')
    
    print("\nGenerating AI voice samples...")
    print("-" * 50)
    
    for lang, text in texts.items():
        lang_dir = output_dir / lang
        lang_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate multiple variations
        for i in range(5):
            try:
                # Using gTTS (basic example)
                tts = gTTS(text=text, lang=lang_codes[lang], slow=False)
                output_file = lang_dir / f'sample_{lang}_gtts_{i+1}.mp3'
                tts.save(str(output_file))
                print(f"[OK] Generated: {output_file}")
            except Exception as e:
                print(f"[ERROR] Error generating {lang} sample {i+1}: {e}")
    
    print("\n" + "=" * 50)
    print("AI sample generation complete!")
    print("\nNext steps:")
    print("1. Add human voice samples to data/train/human/<language>/")
    print("2. Run train_model.py to train the classifier")


if __name__ == '__main__':
    generate_samples()
