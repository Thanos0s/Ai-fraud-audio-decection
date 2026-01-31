"""
API Key Authentication
"""
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('API_KEY', 'sk_test_voice_detection_2026')
api_key_header = APIKeyHeader(name='x-api-key', auto_error=True)


async def verify_api_key(api_key: str = Security(api_key_header)):
    """Verify API key from request header"""
    if api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    return api_key
