"""
Image Generation Service using Stable Diffusion XL via Automatic1111 WebUI API
Supports uncensored image generation with custom LoRAs and styles
"""
import aiohttp
import asyncio
import base64
import time
import uuid
from pathlib import Path
from typing import Dict, Optional, List, Tuple
from PIL import Image
import io
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from config import settings


class ImageGenerationService:
    """Service for generating images using Stable Diffusion XL"""

    def __init__(self):
        self.api_url = settings.SD_API_URL
        self.model = settings.SD_MODEL
        self.vae = settings.SD_VAE
        self.steps = settings.SD_STEPS
        self.cfg_scale = settings.SD_CFG_SCALE
        self.width = settings.SD_WIDTH
        self.height = settings.SD_HEIGHT
        self.negative_prompt = settings.SD_NEGATIVE_PROMPT
        self.sampler = settings.SD_SAMPLER
        self.clip_skip = settings.SD_CLIP_SKIP
        self.storage_path = Path(settings.IMAGE_STORAGE_PATH)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.style_presets = {
            "realistic": {
                "prompt_suffix": ", photorealistic, realistic lighting, detailed skin texture, professional photography, 8k uhd, dslr",
                "negative": "anime, cartoon, illustration, drawing, painting, 3d render, low quality",
                "cfg_scale": 7.0,
            },
            "anime": {
                "prompt_suffix": ", anime style, manga, detailed anime art, vibrant colors, high quality anime",
                "negative": "realistic, photorealistic, 3d, low quality, sketch",
                "cfg_scale": 9.0,
            },
            "manga": {
                "prompt_suffix": ", manga style, black and white manga art, detailed linework, professional manga",
                "negative": "color, colored, realistic, photo, low quality",
                "cfg_scale": 8.0,
            },
            "artistic": {
                "prompt_suffix": ", digital art, artstation, concept art, detailed illustration, vibrant colors",
                "negative": "low quality, blurry, bad anatomy, worst quality",
                "cfg_scale": 7.5,
            },
        }

    async def check_api_status(self) -> bool:
        """Check if Stable Diffusion API is available"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_url}/sdapi/v1/sd-models", timeout=5) as response:
                    return response.status == 200
        except Exception as e:
            print(f"SD API not available: {e}")
            return False

    async def get_available_models(self) -> List[str]:
        """Get list of available SD models"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_url}/sdapi/v1/sd-models") as response:
                    if response.status == 200:
                        models = await response.json()
                        return [model["model_name"] for model in models]
            return []
        except Exception as e:
            print(f"Error fetching models: {e}")
            return []

    async def set_model(self, model_name: str) -> bool:
        """Set the active SD model"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {"sd_model_checkpoint": model_name}
                async with session.post(
                    f"{self.api_url}/sdapi/v1/options",
                    json=payload
                ) as response:
                    return response.status == 200
        except Exception as e:
            print(f"Error setting model: {e}")
            return False

    def enhance_prompt_with_style(
        self,
        prompt: str,
        style: str = "realistic"
    ) -> Tuple[str, str, float]:
        """
        Enhance prompt with style-specific additions

        Args:
            prompt: Base prompt
            style: Style preset (realistic, anime, manga, artistic)

        Returns:
            Tuple of (enhanced_prompt, negative_prompt, cfg_scale)
        """
        preset = self.style_presets.get(style, self.style_presets["realistic"])

        enhanced_prompt = prompt + preset["prompt_suffix"]
        negative_prompt = self.negative_prompt + ", " + preset["negative"]
        cfg_scale = preset["cfg_scale"]

        return enhanced_prompt, negative_prompt, cfg_scale

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
    ) -> Dict:
        """
        Generate an image using Stable Diffusion

        Args:
            prompt: Image generation prompt
            negative_prompt: Things to avoid in image
            style: Style preset (realistic, anime, manga, artistic)
            width: Image width (default from config)
            height: Image height (default from config)
            steps: Number of sampling steps
            cfg_scale: CFG scale for prompt adherence
            seed: Random seed (-1 for random)
            character_id: Character ID for organizing images

        Returns:
            Dict with image info and metadata
        """
        start_time = time.time()

        enhanced_prompt, enhanced_negative, style_cfg = self.enhance_prompt_with_style(
            prompt, style
        )

        if negative_prompt:
            enhanced_negative = f"{enhanced_negative}, {negative_prompt}"

        payload = {
            "prompt": enhanced_prompt,
            "negative_prompt": enhanced_negative,
            "width": width or self.width,
            "height": height or self.height,
            "steps": steps or self.steps,
            "cfg_scale": cfg_scale or style_cfg,
            "sampler_name": self.sampler,
            "seed": seed,
            "batch_size": 1,
            "n_iter": 1,
            "restore_faces": False,
            "override_settings": {
                "sd_model_checkpoint": self.model,
                "sd_vae": self.vae,
                "CLIP_stop_at_last_layers": self.clip_skip,
            },
            "save_images": False,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/sdapi/v1/txt2img",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=300)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"SD API error: {error_text}")

                    result = await response.json()

            if not result.get("images"):
                raise Exception("No images returned from SD API")

            image_data = result["images"][0]
            info = result.get("info", {})

            file_path = await self._save_image(image_data, character_id)

            generation_time = time.time() - start_time

            return {
                "success": True,
                "file_path": str(file_path),
                "file_url": f"/images/{file_path.name}",
                "prompt": enhanced_prompt,
                "negative_prompt": enhanced_negative,
                "width": width or self.width,
                "height": height or self.height,
                "steps": steps or self.steps,
                "cfg_scale": cfg_scale or style_cfg,
                "seed": info.get("seed", seed),
                "model": self.model,
                "style": style,
                "generation_time": generation_time,
            }

        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": "Image generation timed out. Try reducing steps or resolution.",
                "generation_time": time.time() - start_time,
            }
        except Exception as e:
            print(f"Error generating image: {e}")
            return {
                "success": False,
                "error": str(e),
                "generation_time": time.time() - start_time,
            }

    async def _save_image(self, image_b64: str, character_id: Optional[int] = None) -> Path:
        """Save base64 image to filesystem"""
        image_bytes = base64.b64decode(image_b64)
        image = Image.open(io.BytesIO(image_bytes))

        filename = f"{uuid.uuid4()}.png"
        if character_id:
            char_dir = self.storage_path / f"character_{character_id}"
            char_dir.mkdir(exist_ok=True)
            file_path = char_dir / filename
        else:
            file_path = self.storage_path / filename

        image.save(file_path, "PNG", optimize=True)

        return file_path

    async def generate_character_image(
        self,
        character_info: Dict,
        situation: str = "portrait",
        style: str = "realistic",
    ) -> Dict:
        """
        Generate an image of a character in a specific situation

        Args:
            character_info: Character information including appearance
            situation: Description of the situation/scene
            style: Art style preset

        Returns:
            Dict with generation result
        """
        appearance = character_info.get("appearance_description", "")
        name = character_info.get("name", "character")

        if not appearance:
            appearance = f"{name}, attractive person"

        prompt = f"{appearance}, {situation}"

        return await self.generate_image(
            prompt=prompt,
            style=style,
            character_id=character_info.get("id"),
        )

    async def enhance_prompt_with_llm(self, basic_prompt: str, llm_service) -> str:
        """
        Use LLM to enhance and detail the image prompt

        Args:
            basic_prompt: Basic prompt description
            llm_service: LLM service instance

        Returns:
            Enhanced detailed prompt
        """
        enhancement_request = f"""Create a detailed Stable Diffusion prompt from this description: "{basic_prompt}"

Add specific visual details about:
- Physical appearance and features
- Clothing and accessories
- Pose and expression
- Lighting and atmosphere
- Background and setting
- Camera angle and composition

Return only the enhanced prompt, no explanations."""

        try:
            response = await llm_service.generate_response(
                messages=[{"role": "user", "content": enhancement_request}],
                character_info={"persona_type": "default", "name": "AI"},
                stream=False,
            )

            return response["content"].strip()
        except Exception as e:
            print(f"Error enhancing prompt: {e}")
            return basic_prompt

    def get_lora_string(self, loras: List[Dict]) -> str:
        """
        Format LoRA strings for prompt

        Args:
            loras: List of LoRA dicts [{"name": "lora_name", "weight": 0.8}]

        Returns:
            Formatted LoRA string
        """
        lora_strings = []
        for lora in loras:
            name = lora.get("name", "")
            weight = lora.get("weight", 1.0)
            lora_strings.append(f"<lora:{name}:{weight}>")

        return " ".join(lora_strings)


image_service = ImageGenerationService()


if __name__ == "__main__":
    async def test_image_service():
        """Test image generation service"""
        print("Testing Image Generation Service...")

        api_available = await image_service.check_api_status()
        print(f"SD API Available: {api_available}")

        if not api_available:
            print("Make sure Stable Diffusion WebUI is running with --api flag")
            print(f"Expected at: {image_service.api_url}")
            return

        models = await image_service.get_available_models()
        print(f"Available models: {models}")

        print("\nGenerating test image...")
        result = await image_service.generate_image(
            prompt="beautiful woman, smiling, portrait",
            style="realistic",
            steps=20,
        )

        if result["success"]:
            print(f"✓ Image generated successfully!")
            print(f"  File: {result['file_path']}")
            print(f"  Time: {result['generation_time']:.2f}s")
            print(f"  Seed: {result['seed']}")
        else:
            print(f"✗ Generation failed: {result['error']}")

    asyncio.run(test_image_service())
