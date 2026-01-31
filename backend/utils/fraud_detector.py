"""
Fraud Detection Module
Analyzes audio patterns, behavior, and keywords to detect potential spam/fraud
"""
import numpy as np
import speech_recognition as sr
import os

class FraudDetector:
    def __init__(self):
        # Risk weights
        self.weights = {
            'ai_score': 0.5,      # Adjusted to make room for keywords
            'urgency': 0.2,
            'keywords': 0.3       # New keyword weight
        }
        
        # Suspicious keywords (lowercase)
        self.keywords = [
            'password', 'otp', 'credit card', 'debit card', 'cvv', 
            'social security', 'ssn', 'bank account', 'refund', 
            'verify', 'urgent', 'blocked', 'expiry'
        ]
        
        self.recognizer = sr.Recognizer()

    def analyze_risk(self, ai_confidence, audio_features, keywords_detected=None):
        """
        Calculate fraud risk score (0-100)
        
        Args:
            ai_confidence (float): Probability of being AI (0.0-1.0)
            audio_features (dict): Extracted features (speech rate, pitch, etc.)
            keywords_detected (list): List of detected suspicious words
            
        Returns:
            dict: Risk assessment
        """
        if keywords_detected is None:
            keywords_detected = []
            
        # 1. AI Score Risk
        ai_risk = ai_confidence * 100
        
        # 2. Behavioral Analysis
        urgency_score = self._detect_urgency(audio_features)
        
        # 3. Keyword Risk
        keyword_risk = min(100, len(keywords_detected) * 25) # 25 points per keyword, max 100
        
        # 4. Calculate Weighted Score
        total_risk = (
            (ai_risk * self.weights['ai_score']) + 
            (urgency_score * self.weights['urgency']) +
            (keyword_risk * self.weights['keywords'])
        )
        
        # Boost risk if keywords found with AI or Urgency
        if keywords_detected and (ai_risk > 50 or urgency_score > 60):
            total_risk = min(100, total_risk * 1.3)
            
        return {
            'risk_score': round(total_risk, 1),
            'risk_level': self._get_risk_level(total_risk),
            'metrics': {
                'ai_probability': round(ai_confidence * 100, 1),
                'urgency_score': round(urgency_score, 1),
                'keyword_risk': round(keyword_risk, 1)
            },
            'alerts': self._generate_alerts(ai_risk, urgency_score, keywords_detected)
        }
    
    def detect_keywords(self, audio_path):
        """
        Transcribe audio and check for suspicious keywords
        
        Args:
            audio_path: Path to WAV file
            
        Returns:
            tuple: (detected_keywords, full_transcript_text)
        """
        detected = []
        full_text = ""
        try:
            with sr.AudioFile(audio_path) as source:
                # Record the audio data from the file
                audio_data = self.recognizer.record(source)
                
                # Recognize speech using Google Web Speech API
                try:
                    full_text = self.recognizer.recognize_google(audio_data)
                    lower_text = full_text.lower()
                    
                    print(f"Transcript: {full_text}")
                    
                    # Check for keywords
                    for kw in self.keywords:
                        if kw in lower_text:
                            detected.append(kw)
                            
                except sr.UnknownValueError:
                    full_text = "[Unintelligible / Silence]"
                    print("Speech Recognition could not understand audio")
                    
        except sr.RequestError as e:
            full_text = f"[API Error: {str(e)}]"
            print(f"Could not request results; {e}")
        except Exception as e:
            full_text = f"[Error: {str(e)}]"
            print(f"Error acting on keywords: {e}")
            
        return detected, full_text
    
    def _detect_urgency(self, features):
        """
        Estimate urgency based on audio energy and spectral flux
        """
        try:
            # Simple heuristic
            energy_mean = np.mean(features[280:290]) if len(features) > 290 else 0.5
            spectral_mean = np.mean(features[40:45]) if len(features) > 45 else 0.5
            urgency = (energy_mean * 0.5) + (spectral_mean * 0.02)
            return min(100, max(0, urgency))
        except:
            return 50.0
            
    def _get_risk_level(self, score):
        if score > 75: return "CRITICAL"
        if score > 50: return "HIGH"
        if score > 25: return "MEDIUM"
        return "LOW"
        
    def _generate_alerts(self, ai_risk, urgency, keywords):
        alerts = []
        if ai_risk > 85:
            alerts.append("⚠️ HIGH RISK: Synthetic voice detected (Robocall)")
        
        if urgency > 75:
            alerts.append("⚠️ THREAT: High urgency/pressure speech pattern detected")
            
        if keywords:
            kw_str = ", ".join(keywords)
            alerts.append(f"⚠️ SECURITY ALERT: Suspicious keywords detected: {kw_str}")
            
        if not alerts and ai_risk < 20:
            alerts.append("✅ Low Risk: Natural conversation detected")
            
        return alerts
