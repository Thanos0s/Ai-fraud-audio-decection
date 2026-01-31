"""
FastAPI Backend Application for AI Voice Detection
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal
import os
from dotenv import load_dotenv
import uvicorn
import io
import numpy as np

from models.audio_classifier import VoiceDetectionModel
from models.feature_extractor import AudioFeatureExtractor
from utils.audio_processor import AudioProcessor
from utils.auth import verify_api_key
from utils.fraud_detector import FraudDetector

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(
    title="AI Voice & Fraud Detection API",
    description="API for detecting AI-generated voices and analyzing call fraud risk",
    version="1.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize modules
MODEL_PATH = os.getenv('MODEL_PATH', 'models/best_model.pt')
voice_model = None

try:
    if os.path.exists(MODEL_PATH):
        voice_model = VoiceDetectionModel(MODEL_PATH)
        print(f"Model loaded from {MODEL_PATH}")
    else:
        print(f"Model not found at {MODEL_PATH}. Running in demo mode.")
except Exception as e:
    print(f"Error loading model: {e}. Running in demo mode.")

feature_extractor = AudioFeatureExtractor()
audio_processor = AudioProcessor()
fraud_detector = FraudDetector()


# Request/Response Models
class VoiceDetectionRequest(BaseModel):
    language: Literal['Tamil', 'English', 'Hindi', 'Malayalam', 'Telugu']
    audioFormat: Literal['mp3'] = 'mp3'
    audioBase64: str = Field(..., description="Base64-encoded MP3 audio")


class VoiceDetectionResponse(BaseModel):
    status: str = "success"
    language: str
    classification: Literal['AI_GENERATED', 'HUMAN']
    confidenceScore: float = Field(..., ge=0.0, le=1.0)
    explanation: str


class ErrorResponse(BaseModel):
    status: str = "error"
    message: str


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "AI Voice Detection API",
        "status": "operational",
        "supported_languages": ["Tamil", "English", "Hindi", "Malayalam", "Telugu"]
    }


@app.post(
    "/api/voice-detection",
    response_model=VoiceDetectionResponse,
    responses={
        200: {"model": VoiceDetectionResponse},
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def detect_voice(
    request: VoiceDetectionRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Detect if voice is AI-generated or Human
    
    - **language**: One of Tamil, English, Hindi, Malayalam, Telugu
    - **audioFormat**: Always 'mp3'
    - **audioBase64**: Base64-encoded MP3 audio file
    
    Returns classification, confidence score, and explanation
    """
    try:
        # 1. Decode audio
        audio = audio_processor.decode_base64_to_audio(request.audioBase64)
        
        # 2. Validate audio
        audio_processor.validate_audio(audio)
        
        # 3. Extract features
        features = feature_extractor.extract_features(audio)
        
        # 4. Make prediction (if model is loaded)
        if model.model is not None:
            classification, confidence, explanation = model.predict(features)
        else:
            # Demo mode - return simulated response
            import random
            classification = random.choice(["AI_GENERATED", "HUMAN"])
            confidence = random.uniform(0.75, 0.95)
            explanation = "Demo mode - model not trained yet"
        
        # 5. Return response
        return VoiceDetectionResponse(
            status="success",
            language=request.language,
            classification=classification,
            confidenceScore=round(confidence, 2),
            explanation=explanation
        )
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/call-analysis")
async def analyze_call(
    request: VoiceDetectionRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Complete call analysis: AI Detection + Fraud Risk Scoring + Keyword Detection
    """
    temp_file = None
    try:
        # 1. Decode audio
        audio = audio_processor.decode_base64_to_audio(request.audioBase64)
        
        # 2. Extract features
        features = feature_extractor.extract_features(audio)
        
        # 3. Keyword Detection (Requires WAV file)
        # Create temp file for speech recognition
        keywords_detected = []
        transcript = ""
        try:
            temp_file = audio_processor.save_temp_wav(audio)
            keywords_detected, transcript = fraud_detector.detect_keywords(temp_file)
        except Exception as kw_err:
            print(f"Keyword detection failed: {kw_err}")
            transcript = f"[Error: {str(kw_err)}]"
        
        # 4. AI Detection
        classification = "HUMAN"
        confidence = 0.0
        
        if voice_model and voice_model.model is not None:
            classification, confidence, _ = voice_model.predict(features)
        else:
            # Demo mode
            classification = "AI_GENERATED"
            confidence = 0.85
            
        # 5. Fraud Analysis
        # Create mock features for heuristic analysis since we don't return raw vector from model
        mock_features = np.zeros(425) 
        if classification == "AI_GENERATED":
            mock_features[40] = 3000  # High spectral centroid (synthetic)
        
        # Calculate risk (including keywords)
        ai_prob = confidence if classification == "AI_GENERATED" else (1 - confidence)
        risk_analysis = fraud_detector.analyze_risk(
            ai_prob, 
            mock_features,
            keywords_detected=keywords_detected
        )
        
        return {
            "status": "success",
            "voice_analysis": {
                "classification": classification,
                "confidence": round(confidence, 2)
            },
            "fraud_analysis": risk_analysis,
            "transcript_data": {
                "keywords_found": keywords_detected,
                "transcript": transcript
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup temp file
        if temp_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "model_loaded": model.model is not None,
        "feature_extractor": "ready",
        "model_path": MODEL_PATH
    }


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('PORT', os.getenv('API_PORT', 8000)))
    
    print(f"\nStarting AI Voice Detection API...")
    print(f"Server: http://{host}:{port}")
    print(f"Docs: http://{host}:{port}/docs")
    print(f"API Key: {os.getenv('API_KEY', 'sk_test_voice_detection_2026')}\n")
    
    uvicorn.run(app, host=host, port=port, reload=True)
