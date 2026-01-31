"""
Audio Processing Utilities
Handles Base64 decoding and audio format conversion
"""
import base64
import io
import librosa
import soundfile as sf
import numpy as np
from pydub import AudioSegment


class AudioProcessor:
    """Handle audio file processing"""
    
    @staticmethod
    def decode_base64_to_audio(
        audio_base64: str, 
        sample_rate: int = 16000
    ) -> np.ndarray:
        """
        Decode Base64 audio to audio array
        Handles multiple formats: MP3, WAV, WebM, OGG
        
        Args:
            audio_base64: Base64 encoded audio
            sample_rate: Target sample rate
            
        Returns:
            Audio signal as numpy array
        """
        try:
            # Decode Base64
            audio_bytes = base64.b64decode(audio_base64)
            
            # Try multiple approaches to handle different audio formats
            audio = None
            errors = []
            
            # Approach 1: Try as MP3
            try:
                audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format='mp3')
            except Exception as e1:
                errors.append(f"MP3: {str(e1)}")
                
                # Approach 2: Try as WAV
                try:
                    audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format='wav')
                except Exception as e2:
                    errors.append(f"WAV: {str(e2)}")
                    
                    # Approach 3: Try as WebM (common for browser recordings)
                    try:
                        audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format='webm')
                    except Exception as e3:
                        errors.append(f"WebM: {str(e3)}")
                        
                        # Approach 4: Try letting pydub auto-detect
                        try:
                            audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
                        except Exception as e4:
                            errors.append(f"Auto-detect: {str(e4)}")
                            
                            # Approach 5: Try direct librosa load
                            try:
                                y, sr = librosa.load(io.BytesIO(audio_bytes), sr=sample_rate)
                                return y
                            except Exception as e5:
                                errors.append(f"Librosa: {str(e5)}")
            
            if audio is None:
                raise ValueError(f"Could not decode audio. Tried formats: {', '.join(errors)}")
            
            # Convert to mono if stereo
            if audio.channels > 1:
                audio = audio.set_channels(1)
            
            # Export as WAV to memory
            wav_io = io.BytesIO()
            audio.export(wav_io, format='wav')
            wav_io.seek(0)
            
            # Load with librosa
            y, sr = librosa.load(wav_io, sr=sample_rate)
            
            # Ensure audio is not empty
            if len(y) == 0:
                raise ValueError("Decoded audio is empty")
            
            return y
            
        except Exception as e:
            raise ValueError(f"Error processing audio: {str(e)}")
    
    @staticmethod
    def validate_audio(audio: np.ndarray, max_length: int = 30) -> bool:
        """
        Validate audio meets requirements
        
        Args:
            audio: Audio signal
            max_length: Maximum length in seconds
            
        Returns:
            True if valid
        """
        if len(audio) == 0:
            raise ValueError("Audio is empty")
        
        # Check length (assuming 16kHz sample rate)
        duration = len(audio) / 16000
        if duration > max_length:
            raise ValueError(
                f"Audio too long: {duration:.1f}s (max: {max_length}s)"
            )
        
        return True

    @staticmethod
    def save_temp_wav(audio_data: np.ndarray, sample_rate: int = 16000) -> str:
        """
        Save audio array to temporary WAV file compatible with SpeechRecognition
        """
        import tempfile
        import os
        
        # Check for silence/low volume
        max_amp = np.max(np.abs(audio_data))
        print(f"DEBUG: Audio Max Amplitude: {max_amp:.4f}")
        
        if max_amp < 0.01:
            print("WARNING: Audio contains mostly silence")
        
        # Create temp file
        fd, path = tempfile.mkstemp(suffix='.wav')
        os.close(fd)
        
        # Ensure data is adequate for writing (clip to -1.0 to 1.0)
        audio_clipped = np.clip(audio_data, -1.0, 1.0)
        
        # Explicitly write as PCM_16 (standard WAV)
        # soundfile handles conversion if we pass subtype
        sf.write(path, audio_clipped, sample_rate, subtype='PCM_16')
        
        return path
