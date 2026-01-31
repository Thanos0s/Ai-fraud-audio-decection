"""
Audio Classifier Neural Network for AI vs Human Voice Detection
"""
import torch
import torch.nn as nn
import numpy as np
from typing import Tuple


class AudioClassifierNN(nn.Module):
    """Neural Network for AI vs Human voice classification"""
    
    def __init__(self, input_size: int, hidden_sizes: list = [512, 256, 128]):
        super(AudioClassifierNN, self).__init__()
        
        layers = []
        prev_size = input_size
        
        for hidden_size in hidden_sizes:
            layers.extend([
                nn.Linear(prev_size, hidden_size),
                nn.BatchNorm1d(hidden_size),
                nn.ReLU(),
                nn.Dropout(0.3)
            ])
            prev_size = hidden_size
        
        # Output layer
        layers.append(nn.Linear(prev_size, 2))  # Binary: AI or Human
        
        self.network = nn.Sequential(*layers)
    
    def forward(self, x):
        return self.network(x)


class VoiceDetectionModel:
    """Complete model wrapper for inference"""
    
    def __init__(self, model_path: str = None):
        self.device = torch.device(
            'cuda' if torch.cuda.is_available() else 'cpu'
        )
        self.model = None
        self.scaler = None
        
        if model_path:
            self.load_model(model_path)
    
    def load_model(self, model_path: str):
        """Load trained model"""
        checkpoint = torch.load(model_path, map_location=self.device)
        
        input_size = checkpoint['input_size']
        self.model = AudioClassifierNN(input_size)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.to(self.device)
        self.model.eval()
        
        # Load scaler if available
        if 'scaler' in checkpoint:
            self.scaler = checkpoint['scaler']
    
    def predict(
        self, 
        features: np.ndarray
    ) -> Tuple[str, float, str]:
        """
        Make prediction on audio features
        
        Returns:
            (classification, confidence, explanation)
        """
        # Ensure features are 1D array first
        if features.ndim > 1:
            features = features.flatten()
        
        # Reshape to 2D for model (batch_size=1, features)
        features = features.reshape(1, -1)
        
        # Normalize features
        if self.scaler:
            features = self.scaler.transform(features)
        
        # Convert to tensor (already 2D from reshape above)
        features_tensor = torch.FloatTensor(features).to(self.device)
        
        # Make prediction
        with torch.no_grad():
            outputs = self.model(features_tensor)
            probabilities = torch.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probabilities, 1)
        
        # Classification
        classification = "AI_GENERATED" if predicted.item() == 0 else "HUMAN"
        confidence_score = confidence.item()
        
        # Generate explanation
        explanation = self._generate_explanation(
            features, 
            classification, 
            confidence_score
        )
        
        return classification, confidence_score, explanation
    
    def _generate_explanation(
        self, 
        features: np.ndarray, 
        classification: str, 
        confidence: float
    ) -> str:
        """Generate human-readable explanation"""
        
        reasons = []
        
        # Extract key feature values (example indices)
        spectral_centroid = features[0][40] if len(features[0]) > 40 else 0
        zcr = features[0][80] if len(features[0]) > 80 else 0
        pitch_std = features[0][85] if len(features[0]) > 85 else 0
        
        if classification == "AI_GENERATED":
            if spectral_centroid > 2000:
                reasons.append("Synthetic spectral patterns detected")
            if zcr < 0.05:
                reasons.append("Unnatural voice transitions")
            if pitch_std < 20:
                reasons.append("Robotic pitch consistency")
            if confidence > 0.9:
                reasons.append("High AI likelihood")
        else:
            if pitch_std > 50:
                reasons.append("Natural pitch variations")
            reasons.append("Organic spectral characteristics")
            if confidence > 0.8:
                reasons.append("Strong human voice patterns")
        
        if not reasons:
            reasons.append(
                f"Model confidence: {confidence:.2%}"
            )
        
        return "; ".join(reasons)
