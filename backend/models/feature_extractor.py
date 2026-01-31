"""
Audio Feature Extractor for AI Voice Detection
Extracts comprehensive audio features for machine learning classification
"""
import librosa
import numpy as np
from typing import Dict, Tuple


class AudioFeatureExtractor:
    """Extract features from audio for AI detection"""
    
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
    
    def extract_features(self, audio: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Extract comprehensive audio features
        
        Args:
            audio: Audio signal as numpy array
            
        Returns:
            Dictionary of extracted features
        """
        features = {}
        
        # 1. MFCCs - Captures timbral characteristics
        mfccs = librosa.feature.mfcc(
            y=audio, 
            sr=self.sample_rate, 
            n_mfcc=40
        )
        features['mfcc_mean'] = np.mean(mfccs, axis=1)
        features['mfcc_std'] = np.std(mfccs, axis=1)
        features['mfcc_delta'] = np.mean(
            librosa.feature.delta(mfccs), 
            axis=1
        )
        
        # 2. Spectral Features
        # Spectral Centroid - "brightness" of sound
        spectral_centroid = librosa.feature.spectral_centroid(
            y=audio, 
            sr=self.sample_rate
        )
        features['spectral_centroid_mean'] = np.mean(spectral_centroid)
        features['spectral_centroid_std'] = np.std(spectral_centroid)
        
        # Spectral Rolloff - frequency below which X% of energy is contained
        spectral_rolloff = librosa.feature.spectral_rolloff(
            y=audio, 
            sr=self.sample_rate
        )
        features['spectral_rolloff_mean'] = np.mean(spectral_rolloff)
        features['spectral_rolloff_std'] = np.std(spectral_rolloff)
        
        # Spectral Bandwidth
        spectral_bandwidth = librosa.feature.spectral_bandwidth(
            y=audio, 
            sr=self.sample_rate
        )
        features['spectral_bandwidth_mean'] = np.mean(spectral_bandwidth)
        features['spectral_bandwidth_std'] = np.std(spectral_bandwidth)
        
        # Spectral Contrast - difference in amplitude between peaks/valleys
        spectral_contrast = librosa.feature.spectral_contrast(
            y=audio, 
            sr=self.sample_rate
        )
        features['spectral_contrast_mean'] = np.mean(
            spectral_contrast, 
            axis=1
        )
        
        # Spectral Flatness - how noise-like vs tone-like
        spectral_flatness = librosa.feature.spectral_flatness(y=audio)
        features['spectral_flatness_mean'] = np.mean(spectral_flatness)
        features['spectral_flatness_std'] = np.std(spectral_flatness)
        
        # 3. Temporal Features
        # Zero Crossing Rate - how often signal changes sign
        zcr = librosa.feature.zero_crossing_rate(audio)
        features['zcr_mean'] = np.mean(zcr)
        features['zcr_std'] = np.std(zcr)
        
        # RMS Energy
        rms = librosa.feature.rms(y=audio)
        features['rms_mean'] = np.mean(rms)
        features['rms_std'] = np.std(rms)
        
        # 4. Pitch Features
        # Fundamental frequency estimation
        pitches, magnitudes = librosa.piptrack(
            y=audio, 
            sr=self.sample_rate
        )
        pitch_values = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            if pitch > 0:
                pitch_values.append(pitch)
        
        if len(pitch_values) > 0:
            features['pitch_mean'] = np.mean(pitch_values)
            features['pitch_std'] = np.std(pitch_values)
            features['pitch_min'] = np.min(pitch_values)
            features['pitch_max'] = np.max(pitch_values)
        else:
            features['pitch_mean'] = 0
            features['pitch_std'] = 0
            features['pitch_min'] = 0
            features['pitch_max'] = 0
        
        # 5. Chroma Features - pitch class profile
        chroma = librosa.feature.chroma_stft(y=audio, sr=self.sample_rate)
        features['chroma_mean'] = np.mean(chroma, axis=1)
        features['chroma_std'] = np.std(chroma, axis=1)
        
        # 6. AI-Specific Artifacts
        # Detect unnatural periodicity
        tempogram = librosa.feature.tempogram(y=audio, sr=self.sample_rate)
        features['tempogram_mean'] = np.mean(tempogram)
        features['tempogram_std'] = np.std(tempogram)
        
        # Mel Spectrogram
        mel_spec = librosa.feature.melspectrogram(
            y=audio, 
            sr=self.sample_rate
        )
        features['mel_spec_mean'] = np.mean(mel_spec, axis=1)
        features['mel_spec_std'] = np.std(mel_spec, axis=1)
        
        return self._flatten_features(features)
    
    def _flatten_features(self, features: Dict) -> np.ndarray:
        """Flatten nested features into single vector"""
        flat_features = []
        
        for key, value in features.items():
            if isinstance(value, np.ndarray):
                flat_features.extend(value.flatten())
            else:
                flat_features.append(value)
        
        return np.array(flat_features)
    
    def get_feature_names(self) -> list:
        """Return list of feature names for debugging"""
        return [
            'mfcc_mean', 'mfcc_std', 'mfcc_delta',
            'spectral_centroid', 'spectral_rolloff',
            'spectral_bandwidth', 'spectral_contrast',
            'spectral_flatness', 'zcr', 'rms',
            'pitch_mean', 'pitch_std', 'chroma',
            'tempogram', 'mel_spec'
        ]
