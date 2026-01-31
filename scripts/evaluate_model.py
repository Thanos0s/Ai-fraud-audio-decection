"""
Evaluation Script for Trained Model
"""
import torch
from pathlib import Path
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models.audio_classifier import VoiceDetectionModel
from backend.models.feature_extractor import AudioFeatureExtractor
import librosa
import numpy as np


def evaluate_model(model_path='models/best_model.pt', test_dir='data/test'):
    """Evaluate trained model on test data"""
    
    print("🔍 Evaluating model...\n")
    
    # Check if model exists
    if not Path(model_path).exists():
        print(f"❌ Model not found at {model_path}")
        print("Please train the model first with: python scripts/train_model.py")
        return
    
    # Load model
    model = VoiceDetectionModel(model_path)
    feature_extractor = AudioFeatureExtractor()
    
    print(f"✅ Model loaded from {model_path}\n")
    
    # Load test files
    test_path = Path(test_dir)
    if not test_path.exists():
        print(f"⚠️  Test directory not found: {test_dir}")
        print("Place test audio files in data/test/ directory")
        return
    
    test_files = list(test_path.glob('*.mp3')) + list(test_path.glob('*.wav'))
    
    if len(test_files) == 0:
        print("⚠️  No test files found in data/test/")
        return
    
    print(f"Found {len(test_files)} test files\n")
    print("=" * 80)
    
    # Evaluate each file
    for audio_file in test_files:
        try:
            # Load audio
            audio, sr = librosa.load(audio_file, sr=16000)
            
            # Extract features
            features = feature_extractor.extract_features(audio)
            
            # Make prediction
            classification, confidence, explanation = model.predict(features)
            
            # Display results
            print(f"\n📄 File: {audio_file.name}")
            print(f"🎯 Classification: {classification}")
            print(f"📊 Confidence: {confidence:.2%}")
            print(f"💡 Explanation: {explanation}")
            print("-" * 80)
            
        except Exception as e:
            print(f"\n❌ Error processing {audio_file.name}: {e}")
            print("-" * 80)
    
    print("\n✅ Evaluation complete!")


if __name__ == '__main__':
    evaluate_model()
