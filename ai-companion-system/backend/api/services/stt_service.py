"""
Speech-to-Text Service using Faster-Whisper
Free, local, high-quality speech recognition using OpenAI's Whisper
"""
import os
from pathlib import Path
from typing import Optional, Dict
import logging
import tempfile
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from config import settings

logger = logging.getLogger(__name__)


class STTService:
    """Speech-to-Text service using Faster-Whisper"""

    def __init__(self):
        self.model = None
        self.model_size = getattr(settings, 'WHISPER_MODEL_SIZE', 'base')
        self.device = getattr(settings, 'WHISPER_DEVICE', 'auto')  # auto, cpu, cuda
        self.compute_type = getattr(settings, 'WHISPER_COMPUTE_TYPE', 'int8')
        self.models_dir = Path(settings.DATA_DIR) / "whisper_models"
        self.models_dir.mkdir(parents=True, exist_ok=True)

        # Available model sizes with their characteristics
        self.available_models = {
            "tiny": {
                "size": "39 MB",
                "vram": "~1 GB",
                "speed": "Very Fast",
                "accuracy": "Good for clear speech",
                "recommended": "Quick responses"
            },
            "base": {
                "size": "74 MB",
                "vram": "~1 GB",
                "speed": "Fast",
                "accuracy": "Better accuracy",
                "recommended": "Balanced (default)"
            },
            "small": {
                "size": "244 MB",
                "vram": "~2 GB",
                "speed": "Medium",
                "accuracy": "Good accuracy",
                "recommended": "Quality over speed"
            },
            "medium": {
                "size": "769 MB",
                "vram": "~5 GB",
                "speed": "Slower",
                "accuracy": "High accuracy",
                "recommended": "Best quality"
            },
            "large-v2": {
                "size": "1550 MB",
                "vram": "~10 GB",
                "speed": "Slow",
                "accuracy": "Highest accuracy",
                "recommended": "Maximum quality"
            }
        }

    def load_model(self, model_size: Optional[str] = None):
        """Load Whisper model"""
        if model_size:
            self.model_size = model_size

        try:
            from faster_whisper import WhisperModel

            # Determine device
            device = self.device
            if device == "auto":
                try:
                    import torch
                    device = "cuda" if torch.cuda.is_available() else "cpu"
                except ImportError:
                    device = "cpu"

            logger.info(f"Loading Whisper model: {self.model_size} on {device}")

            self.model = WhisperModel(
                self.model_size,
                device=device,
                compute_type=self.compute_type,
                download_root=str(self.models_dir)
            )

            logger.info("Whisper model loaded successfully")
            return True

        except ImportError:
            logger.error("faster-whisper not installed. Run: pip install faster-whisper")
            return False
        except Exception as e:
            logger.error(f"Error loading Whisper model: {e}")
            return False

    def is_model_loaded(self) -> bool:
        """Check if model is loaded"""
        return self.model is not None

    async def transcribe_audio(
        self,
        audio_file_path: str,
        language: Optional[str] = "en",
        task: str = "transcribe"
    ) -> Optional[Dict]:
        """
        Transcribe audio to text

        Args:
            audio_file_path: Path to audio file (wav, mp3, etc.)
            language: Language code (en, es, fr, etc.) or None for auto-detect
            task: "transcribe" or "translate" (translate to English)

        Returns:
            Dictionary with transcription and metadata
        """
        # Load model if not already loaded
        if not self.is_model_loaded():
            if not self.load_model():
                return None

        try:
            # Transcribe
            segments, info = self.model.transcribe(
                audio_file_path,
                language=language,
                task=task,
                vad_filter=True,  # Voice activity detection
                vad_parameters=dict(
                    min_silence_duration_ms=500
                )
            )

            # Collect all segments
            transcription = ""
            segments_list = []

            for segment in segments:
                transcription += segment.text + " "
                segments_list.append({
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text
                })

            transcription = transcription.strip()

            if not transcription:
                logger.warning("No speech detected in audio")
                return None

            result = {
                "text": transcription,
                "language": info.language,
                "language_probability": info.language_probability,
                "duration": info.duration,
                "segments": segments_list,
                "model_size": self.model_size
            }

            logger.info(f"Transcribed: '{transcription[:50]}...'")
            return result

        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return None

    async def transcribe_audio_bytes(
        self,
        audio_bytes: bytes,
        filename: str = "audio.wav",
        language: Optional[str] = "en"
    ) -> Optional[Dict]:
        """
        Transcribe audio from bytes

        Args:
            audio_bytes: Audio data as bytes
            filename: Original filename (for format detection)
            language: Language code or None

        Returns:
            Dictionary with transcription and metadata
        """
        # Save to temporary file
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=Path(filename).suffix
        ) as temp_file:
            temp_file.write(audio_bytes)
            temp_path = temp_file.name

        try:
            # Transcribe temporary file
            result = await self.transcribe_audio(temp_path, language)
            return result
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_path)
            except:
                pass

    def get_available_models(self) -> Dict[str, Dict]:
        """Get information about available Whisper models"""
        return self.available_models

    def get_model_info(self) -> Dict:
        """Get current model information"""
        return {
            "model_size": self.model_size,
            "device": self.device,
            "compute_type": self.compute_type,
            "loaded": self.is_model_loaded(),
            "info": self.available_models.get(self.model_size, {})
        }

    def change_model(self, model_size: str) -> bool:
        """Change to a different model size"""
        if model_size not in self.available_models:
            logger.error(f"Invalid model size: {model_size}")
            return False

        logger.info(f"Switching to model: {model_size}")
        self.model = None  # Unload current model
        return self.load_model(model_size)

    def supports_language(self, language_code: str) -> bool:
        """Check if language is supported"""
        # Whisper supports 99+ languages
        supported = [
            "en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl",
            "cs", "ar", "sv", "hu", "fi", "ja", "ko", "zh", "hi", "uk"
        ]
        return language_code in supported


# Global STT service instance
stt_service = STTService()
