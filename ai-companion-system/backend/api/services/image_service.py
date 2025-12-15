"""
Image Generation Service using Stable Diffusion XL
Supports uncensored generation with multiple art styles
"""
import aiohttp
import asyncio
import base64
import time
import uuid
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from config import settings


class ImageGenerationService:
    """Service for generating images using Stable Diffusion WebUI API"""

    def __init__(self):
        self.api_url = settings.SD_API_URL
        self.enabled = settings.SD_ENABLED
        self.default_model = settings.SD_MODEL
        self.default_steps = settings.SD_STEPS
        self.default_cfg = settings.SD_CFG_SCALE
        self.default_width = settings.SD_WIDTH
        self.default_height = settings.SD_HEIGHT
        self.negative_prompt = settings.SD_NEGATIVE_PROMPT
        self.sampler = settings.SD_SAMPLER
        self.clip_skip = settings.SD_CLIP_SKIP

        self.storage_path = Path(settings.IMAGE_STORAGE_PATH)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    async def check_availability(self) -> bool:
        """Check if Stable Diffusion API is available"""
        if not self.enabled:
            return False

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_url}/sdapi/v1/sd-models", timeout=5) as resp:
                    return resp.status == 200
        except Exception as e:
            print(f"SD API not available: {e}")
            return False

    async def get_available_models(self) -> List[str]:
        """Get list of available models from SD WebUI"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_url}/sdapi/v1/sd-models") as resp:
                    if resp.status == 200:
                        models = await resp.json()
                        return [model["title"] for model in models]
        except Exception as e:
            print(f"Error fetching models: {e}")
        return []

    def enhance_prompt_for_style(self, prompt: str, style: str = "realistic") -> Tuple[str, str]:
        """
        Enhance prompt based on desired art style

        Args:
            prompt: Base prompt
            style: realistic, anime, manga, artistic, photographic

        Returns:
            Tuple of (enhanced_prompt, negative_prompt)
        """
        style_enhancements = {
            "realistic": {
                "prefix": "masterpiece, best quality, ultra-detailed, photorealistic, 8k uhd, professional photography,",
                "suffix": "realistic lighting, sharp focus, detailed skin texture, detailed features",
                "negative": "cartoon, anime, 3d render, painting, drawing, illustration, unrealistic, low quality, blurry"
            },
            "anime": {
                "prefix": "masterpiece, best quality, anime style, detailed anime art,",
                "suffix": "vibrant colors, anime aesthetic, clean linework, expressive",
                "negative": "realistic, photograph, 3d, ugly, poorly drawn, bad anatomy, low quality, blurry"
            },
            "manga": {
                "prefix": "masterpiece, manga style, black and white manga art, detailed line art,",
                "suffix": "manga aesthetic, dynamic composition, expressive, clean lines",
                "negative": "color, realistic, photograph, 3d, poorly drawn, low quality, blurry"
            },
            "artistic": {
                "prefix": "masterpiece, best quality, artistic, creative composition,",
                "suffix": "professional art, detailed, expressive, aesthetic",
                "negative": "amateur, poorly drawn, low quality, blurry, ugly"
            },
            "photographic": {
                "prefix": "masterpiece, professional photography, high resolution, dslr,",
                "suffix": "professional lighting, bokeh, sharp focus, detailed",
                "negative": "painting, drawing, illustration, low quality, blurry, distorted"
            }
        }

        enhancement = style_enhancements.get(style, style_enhancements["realistic"])

        enhanced_prompt = f"{enhancement['prefix']} {prompt}, {enhancement['suffix']}"
        negative_prompt = f"{self.negative_prompt}, {enhancement['negative']}"

        return enhanced_prompt, negative_prompt

    async def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        style: str = "realistic",
        width: Optional[int] = None,
        height: Optional[int] = None,
        steps: Optional[int] = None,
        cfg_scale: Optional[float] = None,
        seed: int = -1,
        character_id: Optional[int] = None,
        enhance_prompt: bool = True
    ) -> Dict:
        """
        Generate image using Stable Diffusion

        Args:
            prompt: Image generation prompt
            negative_prompt: Optional negative prompt
            style: Art style (realistic, anime, manga, etc.)
            width: Image width (default from config)
            height: Image height (default from config)
            steps: Number of generation steps
            cfg_scale: CFG scale value
            seed: Generation seed (-1 for random)
            character_id: Optional character ID for organization
            enhance_prompt: Whether to enhance prompt with style tags

        Returns:
            Dict with image info and file path
        """
        if not self.enabled:
            raise Exception("Image generation is disabled")

        start_time = time.time()

        if enhance_prompt:
            prompt, auto_negative = self.enhance_prompt_for_style(prompt, style)
            if not negative_prompt:
                negative_prompt = auto_negative

        if not negative_prompt:
            negative_prompt = self.negative_prompt

        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "steps": steps or self.default_steps,
            "cfg_scale": cfg_scale or self.default_cfg,
            "width": width or self.default_width,
            "height": height or self.default_height,
            "sampler_name": self.sampler,
            "seed": seed,
            "clip_skip": self.clip_skip,
            "save_images": False,
            "send_images": True,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/sdapi/v1/txt2img",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=300)
                ) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        raise Exception(f"SD API error: {error_text}")

                    result = await resp.json()

            generation_time = time.time() - start_time

            if not result.get("images"):
                raise Exception("No images returned from SD API")

            image_b64 = result["images"][0]
            image_data = base64.b64decode(image_b64)

            filename = f"{uuid.uuid4()}.png"
            if character_id:
                char_dir = self.storage_path / f"character_{character_id}"
                char_dir.mkdir(exist_ok=True)
                file_path = char_dir / filename
            else:
                file_path = self.storage_path / filename

            with open(file_path, "wb") as f:
                f.write(image_data)

            used_seed = result.get("info", {}).get("seed", seed)
            if isinstance(result.get("info"), str):
                import json
                info = json.loads(result["info"])
                used_seed = info.get("seed", seed)

            return {
                "success": True,
                "file_path": str(file_path),
                "file_url": f"/images/{filename}",
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "width": payload["width"],
                "height": payload["height"],
                "steps": payload["steps"],
                "cfg_scale": payload["cfg_scale"],
                "seed": used_seed,
                "style": style,
                "generation_time": generation_time,
                "model": self.default_model
            }

        except asyncio.TimeoutError:
            raise Exception("Image generation timeout - SD may be overloaded")
        except Exception as e:
            print(f"Image generation error: {e}")
            raise Exception(f"Failed to generate image: {str(e)}")

    async def generate_character_image(
        self,
        character_info: Dict,
        situation: str = "portrait",
        style: str = "realistic"
    ) -> Dict:
        """
        Generate image for a character based on their appearance and situation

        Args:
            character_info: Character information dict
            situation: Situation to depict (portrait, action, emotion, etc.)
            style: Art style

        Returns:
            Dict with image generation results
        """
        appearance = character_info.get("appearance_description", "")
        name = character_info.get("name", "character")

        if not appearance:
            raise Exception("Character has no appearance description")

        situation_prompts = {
            "portrait": f"portrait of {appearance}",
            "full_body": f"full body shot of {appearance}",
            "casual": f"{appearance}, casual pose, relaxed atmosphere",
            "happy": f"{appearance}, happy expression, smiling, positive mood",
            "thoughtful": f"{appearance}, thoughtful expression, contemplative",
            "romantic": f"{appearance}, romantic atmosphere, warm lighting",
            "action": f"{appearance}, dynamic pose, action scene",
            "serene": f"{appearance}, serene expression, peaceful atmosphere"
        }

        base_prompt = situation_prompts.get(situation, f"{appearance}, {situation}")

        return await self.generate_image(
            prompt=base_prompt,
            style=style,
            character_id=character_info.get("id"),
            enhance_prompt=True
        )

    async def generate_situation_image(
        self,
        description: str,
        character_appearance: Optional[str] = None,
        style: str = "realistic"
    ) -> Dict:
        """
        Generate image based on a situation description
        Used during chat when character wants to show something

        Args:
            description: Description of what to generate
            character_appearance: Optional character appearance to include
            style: Art style

        Returns:
            Dict with image generation results
        """
        prompt = description

        if character_appearance:
            prompt = f"{character_appearance}, {description}"

        return await self.generate_image(
            prompt=prompt,
            style=style,
            enhance_prompt=True
        )

    async def cleanup_old_images(self, max_age_days: int = 30):
        """Clean up old generated images"""
        cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)

        deleted_count = 0
        for image_file in self.storage_path.rglob("*.png"):
            if image_file.stat().st_mtime < cutoff_time:
                image_file.unlink()
                deleted_count += 1

        print(f"Cleaned up {deleted_count} old images")
        return deleted_count


image_service = ImageGenerationService()


if __name__ == "__main__":
    async def test_service():
        """Test image generation service"""
        print("Testing Image Generation Service...")

        available = await image_service.check_availability()
        print(f"SD API Available: {available}")

        if not available:
            print("SD WebUI not available. Start it with --api flag")
            return

        models = await image_service.get_available_models()
        print(f"Available models: {models}")

        print("\nTesting realistic image generation...")
        result = await image_service.generate_image(
            prompt="beautiful woman with long brown hair, green eyes, wearing casual clothes",
            style="realistic",
            steps=20
        )

        print(f"Generated: {result['file_path']}")
        print(f"Time: {result['generation_time']:.2f}s")
        print(f"Seed: {result['seed']}")

    asyncio.run(test_service())
