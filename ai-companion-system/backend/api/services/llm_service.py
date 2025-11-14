"""
LLM Service using Ollama for local inference
"""
import ollama
import time
from typing import List, Dict, Optional, AsyncGenerator
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from config import settings, SYSTEM_PROMPTS


class LLMService:
    """Service for interacting with local LLM via Ollama"""

    def __init__(self):
        self.client = ollama.Client(host=settings.OLLAMA_HOST)
        self.model = settings.LLM_MODEL
        self.temperature = settings.LLM_TEMPERATURE
        self.top_p = settings.LLM_TOP_P
        self.max_tokens = settings.LLM_MAX_TOKENS

    def _build_system_prompt(self, character_info: Dict) -> str:
        """Build system prompt from character information"""
        persona_type = character_info.get("persona_type", "default")
        base_prompt = SYSTEM_PROMPTS.get(persona_type, SYSTEM_PROMPTS["default"])

        # Add character-specific details
        name = character_info.get("name", "AI")
        personality = character_info.get("personality", "")
        backstory = character_info.get("backstory", "")
        interests = character_info.get("interests", [])
        speaking_style = character_info.get("speaking_style", "")

        custom_prompt = f"""{base_prompt}

Your name is {name}.

Personality: {personality}

Backstory: {backstory}

Interests: {', '.join(interests) if interests else 'various topics'}

Speaking Style: {speaking_style}

Remember: Be authentic, remember past conversations, and maintain your character consistently.
You can suggest generating images when appropriate by saying something like "Let me show you..." or "I can create an image of...".
"""
        return custom_prompt.strip()

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        character_info: Dict,
        memories: Optional[List[str]] = None,
        stream: bool = False,
    ) -> Dict:
        """
        Generate response from LLM

        Args:
            messages: Conversation history [{"role": "user", "content": "..."}]
            character_info: Character configuration
            memories: Relevant memories to include in context
            stream: Whether to stream the response

        Returns:
            Dict with response and metadata
        """
        start_time = time.time()

        # Build system message with memories
        system_content = self._build_system_prompt(character_info)

        if memories:
            memory_context = "\n\nRelevant memories:\n" + "\n".join(f"- {m}" for m in memories)
            system_content += memory_context

        # Prepare messages for Ollama
        ollama_messages = [{"role": "system", "content": system_content}]
        ollama_messages.extend(messages)

        try:
            if stream:
                return self._generate_streaming(ollama_messages, start_time)
            else:
                return await self._generate_complete(ollama_messages, start_time)

        except Exception as e:
            print(f"Error generating response: {e}")
            return {
                "content": "I apologize, but I'm having trouble processing that right now. Could you try again?",
                "error": str(e),
                "generation_time": time.time() - start_time,
            }

    async def _generate_complete(self, messages: List[Dict], start_time: float) -> Dict:
        """Generate complete response (non-streaming)"""
        response = self.client.chat(
            model=self.model,
            messages=messages,
            options={
                "temperature": self.temperature,
                "top_p": self.top_p,
                "num_predict": self.max_tokens,
            },
        )

        generation_time = time.time() - start_time

        return {
            "content": response["message"]["content"],
            "model": response.get("model", self.model),
            "tokens": {
                "prompt": response.get("prompt_eval_count", 0),
                "completion": response.get("eval_count", 0),
                "total": response.get("prompt_eval_count", 0) + response.get("eval_count", 0),
            },
            "generation_time": generation_time,
        }

    async def _generate_streaming(
        self, messages: List[Dict], start_time: float
    ) -> AsyncGenerator[Dict, None]:
        """Generate streaming response"""
        stream = self.client.chat(
            model=self.model,
            messages=messages,
            stream=True,
            options={
                "temperature": self.temperature,
                "top_p": self.top_p,
                "num_predict": self.max_tokens,
            },
        )

        full_response = ""
        for chunk in stream:
            if chunk.get("message", {}).get("content"):
                content = chunk["message"]["content"]
                full_response += content

                yield {
                    "type": "chunk",
                    "content": content,
                    "done": False,
                }

        generation_time = time.time() - start_time

        # Send final message with metadata
        yield {
            "type": "done",
            "content": full_response,
            "done": True,
            "generation_time": generation_time,
            "model": self.model,
        }

    def check_model_availability(self) -> bool:
        """Check if the configured model is available"""
        try:
            models = self.client.list()
            available_models = [m["name"] for m in models.get("models", [])]
            return any(self.model in m for m in available_models)
        except Exception as e:
            print(f"Error checking model availability: {e}")
            return False

    def list_available_models(self) -> List[str]:
        """List all available models in Ollama"""
        try:
            models = self.client.list()
            return [m["name"] for m in models.get("models", [])]
        except Exception as e:
            print(f"Error listing models: {e}")
            return []

    async def generate_title(self, first_message: str) -> str:
        """Generate a title for a conversation based on the first message"""
        try:
            prompt = f"Generate a short 3-5 word title for a conversation that starts with: '{first_message[:100]}'\nTitle:"

            response = self.client.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.7, "num_predict": 20},
            )

            title = response["message"]["content"].strip().strip('"').strip("'")
            return title[:50]  # Limit length

        except Exception as e:
            print(f"Error generating title: {e}")
            return "New Conversation"

    async def extract_keywords(self, text: str, max_keywords: int = 5) -> List[str]:
        """Extract keywords from text for memory indexing"""
        try:
            prompt = f"""Extract {max_keywords} key concepts or keywords from the following text.
Return only the keywords, separated by commas.

Text: {text}

Keywords:"""

            response = self.client.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.3, "num_predict": 50},
            )

            keywords_str = response["message"]["content"].strip()
            keywords = [k.strip() for k in keywords_str.split(",")]
            return keywords[:max_keywords]

        except Exception as e:
            print(f"Error extracting keywords: {e}")
            return []

    async def should_generate_image(self, message: str, context: List[Dict]) -> bool:
        """
        Determine if the AI should generate an image based on the conversation

        Returns: True if image generation would be appropriate
        """
        # Simple heuristic checks
        image_triggers = [
            "show you",
            "let me show",
            "here's what",
            "picture of",
            "image of",
            "look like",
            "wearing",
            "visualize",
            "imagine",
        ]

        message_lower = message.lower()
        return any(trigger in message_lower for trigger in image_triggers)

    async def generate_image_prompt(
        self, context: str, character_appearance: str, situation: str = ""
    ) -> str:
        """
        Generate a detailed image prompt based on context

        Args:
            context: Conversation context
            character_appearance: Character's appearance description
            situation: Specific situation to depict

        Returns:
            Detailed Stable Diffusion prompt
        """
        try:
            prompt_request = f"""Create a detailed Stable Diffusion XL prompt for generating an image.

Character appearance: {character_appearance}
Context: {context}
Situation: {situation or 'portrait'}

Generate a detailed, high-quality prompt focusing on visual details, lighting, and composition.
Format: Direct prompt only, no explanations.

Prompt:"""

            response = self.client.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt_request}],
                options={"temperature": 0.8, "num_predict": 150},
            )

            generated_prompt = response["message"]["content"].strip()

            # Enhance with quality tags
            quality_tags = ", high quality, detailed, professional photography, 8k uhd"
            return generated_prompt + quality_tags

        except Exception as e:
            print(f"Error generating image prompt: {e}")
            # Fallback to basic prompt
            return f"{character_appearance}, {situation}, high quality, detailed"


# Singleton instance
llm_service = LLMService()


if __name__ == "__main__":
    import asyncio

    async def test_llm():
        """Test LLM service"""
        print("Testing LLM Service...")

        # Check availability
        available = llm_service.check_model_availability()
        print(f"Model available: {available}")

        if not available:
            print("Available models:", llm_service.list_available_models())
            return

        # Test generation
        character_info = {
            "name": "Emma",
            "persona_type": "girlfriend",
            "personality": "caring, playful",
            "backstory": "A loving companion",
            "interests": ["movies", "music"],
            "speaking_style": "warm and friendly",
        }

        messages = [{"role": "user", "content": "Hi! How are you today?"}]

        print("\nGenerating response...")
        response = await llm_service.generate_response(messages, character_info)

        print(f"\nResponse: {response['content']}")
        print(f"Generation time: {response['generation_time']:.2f}s")
        print(f"Tokens: {response.get('tokens', {})}")

    asyncio.run(test_llm())
