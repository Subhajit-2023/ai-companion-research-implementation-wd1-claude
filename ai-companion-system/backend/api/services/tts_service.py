"""
Text-to-Speech Service using Piper TTS
Free, local, high-quality neural TTS with multiple voices
"""
import os
import subprocess
import hashlib
from pathlib import Path
from typing import Optional, Dict, List
import json
import logging
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from config import settings

logger = logging.getLogger(__name__)


class TTSService:
    """Text-to-Speech service using Piper TTS"""

    def __init__(self):
        self.piper_path = getattr(settings, 'PIPER_PATH', 'piper')
        self.models_dir = Path(settings.DATA_DIR) / "tts_models"
        self.audio_dir = Path(settings.DATA_DIR) / "tts_audio"
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.audio_dir.mkdir(parents=True, exist_ok=True)

        # Available voices with their model paths
        self.available_voices = {
            # Female voices
            "en_US-lessac-medium": {
                "name": "Lessac (Female, US)",
                "gender": "female",
                "language": "en_US",
                "quality": "medium",
                "description": "Clear, professional female voice"
            },
            "en_US-amy-medium": {
                "name": "Amy (Female, US)",
                "gender": "female",
                "language": "en_US",
                "quality": "medium",
                "description": "Warm, friendly female voice"
            },
            "en_GB-alba-medium": {
                "name": "Alba (Female, UK)",
                "gender": "female",
                "language": "en_GB",
                "quality": "medium",
                "description": "British English, gentle female voice"
            },

            # Male voices
            "en_US-danny-low": {
                "name": "Danny (Male, US)",
                "gender": "male",
                "language": "en_US",
                "quality": "low",
                "description": "Clear male voice, fast generation"
            },
            "en_US-ryan-medium": {
                "name": "Ryan (Male, US)",
                "gender": "male",
                "language": "en_US",
                "quality": "medium",
                "description": "Deep, professional male voice"
            },
            "en_GB-northern_english_male-medium": {
                "name": "Northern (Male, UK)",
                "gender": "male",
                "language": "en_GB",
                "quality": "medium",
                "description": "British English, northern accent"
            },

            # Additional options
            "en_US-libritts-high": {
                "name": "LibriTTS (Neutral, US)",
                "gender": "neutral",
                "language": "en_US",
                "quality": "high",
                "description": "High quality, natural sounding voice"
            },
        }

        # Default voices for different personas
        self.persona_default_voices = {
            "girlfriend": "en_US-amy-medium",
            "therapist": "en_US-lessac-medium",
            "friend": "en_US-danny-low",
            "creative_muse": "en_GB-alba-medium",
            "custom": "en_US-libritts-high"
        }

    def check_piper_installed(self) -> bool:
        """Check if Piper is installed and accessible"""
        try:
            result = subprocess.run(
                [self.piper_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            logger.warning("Piper TTS not found. Please install Piper.")
            return False

    def get_model_path(self, voice_id: str) -> Optional[Path]:
        """Get the path to a voice model, download if necessary"""
        if voice_id not in self.available_voices:
            logger.error(f"Voice ID {voice_id} not found")
            return None

        model_file = self.models_dir / f"{voice_id}.onnx"
        config_file = self.models_dir / f"{voice_id}.onnx.json"

        # Check if model already exists
        if model_file.exists() and config_file.exists():
            return model_file

        # Model needs to be downloaded
        logger.info(f"Model {voice_id} not found. Need to download.")
        logger.info("Download Piper models from: https://github.com/rhasspy/piper/releases")
        logger.info(f"Place models in: {self.models_dir}")

        return None

    async def synthesize_speech(
        self,
        text: str,
        voice_id: Optional[str] = None,
        character_id: Optional[int] = None,
        speed: float = 1.0
    ) -> Optional[Dict]:
        """
        Convert text to speech

        Args:
            text: Text to convert
            voice_id: Voice model to use
            character_id: Character ID (for caching)
            speed: Speech speed multiplier (0.5 to 2.0)

        Returns:
            Dictionary with audio file path and metadata
        """
        if not self.check_piper_installed():
            logger.error("Piper TTS not installed")
            return None

        # Use default voice if not specified
        if not voice_id:
            voice_id = "en_US-libritts-high"

        # Get model path
        model_path = self.get_model_path(voice_id)
        if not model_path:
            logger.error(f"Model for voice {voice_id} not available")
            return None

        # Create unique filename based on text hash
        text_hash = hashlib.md5(text.encode()).hexdigest()[:12]
        output_file = self.audio_dir / f"tts_{character_id}_{text_hash}.wav"

        # Check cache
        if output_file.exists():
            logger.info(f"Using cached audio: {output_file}")
            return {
                "audio_path": str(output_file),
                "audio_url": f"/audio/{output_file.name}",
                "voice_id": voice_id,
                "text": text,
                "cached": True
            }

        try:
            # Run Piper TTS
            cmd = [
                self.piper_path,
                "--model", str(model_path),
                "--output_file", str(output_file),
            ]

            # Add speed parameter if not default
            if speed != 1.0:
                cmd.extend(["--length_scale", str(1.0 / speed)])

            # Run synthesis
            process = subprocess.run(
                cmd,
                input=text,
                capture_output=True,
                text=True,
                timeout=30
            )

            if process.returncode != 0:
                logger.error(f"Piper TTS failed: {process.stderr}")
                return None

            # Verify output exists
            if not output_file.exists():
                logger.error("Audio file was not created")
                return None

            logger.info(f"Generated audio: {output_file}")

            return {
                "audio_path": str(output_file),
                "audio_url": f"/audio/{output_file.name}",
                "voice_id": voice_id,
                "text": text,
                "cached": False,
                "file_size": output_file.stat().st_size
            }

        except subprocess.TimeoutExpired:
            logger.error("TTS generation timed out")
            return None
        except Exception as e:
            logger.error(f"TTS generation error: {e}")
            return None

    def get_available_voices(self) -> Dict[str, Dict]:
        """Get list of available voices with metadata"""
        voices = {}
        for voice_id, info in self.available_voices.items():
            model_path = self.models_dir / f"{voice_id}.onnx"
            voices[voice_id] = {
                **info,
                "installed": model_path.exists()
            }
        return voices

    def get_voice_for_persona(self, persona_type: str) -> str:
        """Get default voice for a persona type"""
        return self.persona_default_voices.get(persona_type, "en_US-libritts-high")

    def list_downloaded_models(self) -> List[str]:
        """List all downloaded voice models"""
        models = []
        for model_file in self.models_dir.glob("*.onnx"):
            voice_id = model_file.stem
            if voice_id in self.available_voices:
                models.append(voice_id)
        return models

    async def download_voice_model(self, voice_id: str) -> bool:
        """
        Download a voice model
        Note: This provides instructions, actual download is manual
        """
        if voice_id not in self.available_voices:
            return False

        logger.info(f"""
To download voice model {voice_id}:

1. Visit: https://github.com/rhasspy/piper/releases/latest
2. Download: {voice_id}.onnx and {voice_id}.onnx.json
3. Place both files in: {self.models_dir}

Alternative: Use the provided download script
""")
        return False

    def cleanup_old_audio(self, max_age_days: int = 7):
        """Clean up old TTS audio files"""
        import time
        current_time = time.time()
        max_age_seconds = max_age_days * 86400

        deleted = 0
        for audio_file in self.audio_dir.glob("tts_*.wav"):
            file_age = current_time - audio_file.stat().st_mtime
            if file_age > max_age_seconds:
                audio_file.unlink()
                deleted += 1

        logger.info(f"Cleaned up {deleted} old audio files")


# Global TTS service instance
tts_service = TTSService()
