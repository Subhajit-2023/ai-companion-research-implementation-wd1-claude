"""
Brain - Core LLM integration for the Maker-Researcher system
Uses Mistral/CodeLlama via Ollama optimized for RTX 4060 8GB
"""
import ollama
import time
import json
from typing import List, Dict, Optional, AsyncGenerator, Literal
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import settings, AGENT_PROMPTS


class ModelType(Enum):
    GENERAL = "general"
    CODE = "code"
    REASONING = "reasoning"


@dataclass
class ThinkingStep:
    step: int
    thought: str
    action: Optional[str] = None
    result: Optional[str] = None


@dataclass
class BrainResponse:
    content: str
    model: str
    thinking: List[ThinkingStep] = field(default_factory=list)
    tokens_used: int = 0
    generation_time: float = 0.0
    confidence: float = 0.8
    sources: List[str] = field(default_factory=list)
    error: Optional[str] = None


class Brain:
    def __init__(self):
        self.client = ollama.Client(host=settings.OLLAMA_HOST)
        self.models = {
            ModelType.GENERAL: settings.PRIMARY_MODEL,
            ModelType.CODE: settings.CODE_MODEL,
            ModelType.REASONING: settings.PRIMARY_MODEL,
        }
        self.current_model = settings.PRIMARY_MODEL
        self.conversation_history: List[Dict] = []
        self.max_history = 20

    def _select_model(self, task_type: ModelType) -> str:
        model = self.models.get(task_type, settings.PRIMARY_MODEL)
        if not self._check_model_available(model):
            model = settings.FALLBACK_MODEL
            if not self._check_model_available(model):
                available = self.list_models()
                if available:
                    model = available[0]
        return model

    def _check_model_available(self, model: str) -> bool:
        try:
            models = self.client.list()
            available = [m["name"] for m in models.get("models", [])]
            return any(model.split(":")[0] in m for m in available)
        except Exception:
            return False

    def list_models(self) -> List[str]:
        try:
            models = self.client.list()
            return [m["name"] for m in models.get("models", [])]
        except Exception:
            return []

    async def think(
        self,
        prompt: str,
        agent_type: str = "orchestrator",
        task_type: ModelType = ModelType.GENERAL,
        context: Optional[List[Dict]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> BrainResponse:
        start_time = time.time()
        model = self._select_model(task_type)

        system_prompt = AGENT_PROMPTS.get(agent_type, AGENT_PROMPTS["orchestrator"])

        if task_type == ModelType.CODE:
            temperature = temperature or settings.LLM_CODE_TEMPERATURE
        else:
            temperature = temperature or settings.LLM_TEMPERATURE

        max_tokens = max_tokens or settings.LLM_MAX_TOKENS

        messages = [{"role": "system", "content": system_prompt}]

        if context:
            messages.extend(context[-10:])

        recent_history = self.conversation_history[-self.max_history:]
        messages.extend(recent_history)
        messages.append({"role": "user", "content": prompt})

        try:
            if stream:
                return await self._generate_streaming(messages, model, temperature, max_tokens, start_time)

            response = self.client.chat(
                model=model,
                messages=messages,
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    "top_p": 0.9,
                    "num_ctx": settings.LLM_CONTEXT_WINDOW,
                },
            )

            content = response["message"]["content"]
            tokens = response.get("prompt_eval_count", 0) + response.get("eval_count", 0)

            self.conversation_history.append({"role": "user", "content": prompt})
            self.conversation_history.append({"role": "assistant", "content": content})

            if len(self.conversation_history) > self.max_history * 2:
                self.conversation_history = self.conversation_history[-self.max_history * 2:]

            return BrainResponse(
                content=content,
                model=model,
                tokens_used=tokens,
                generation_time=time.time() - start_time,
            )

        except Exception as e:
            return BrainResponse(
                content="",
                model=model,
                error=str(e),
                generation_time=time.time() - start_time,
            )

    async def _generate_streaming(
        self,
        messages: List[Dict],
        model: str,
        temperature: float,
        max_tokens: int,
        start_time: float,
    ) -> AsyncGenerator[Dict, None]:
        try:
            stream = self.client.chat(
                model=model,
                messages=messages,
                stream=True,
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    "top_p": 0.9,
                },
            )

            full_response = ""
            for chunk in stream:
                if chunk.get("message", {}).get("content"):
                    content = chunk["message"]["content"]
                    full_response += content
                    yield {"type": "chunk", "content": content, "done": False}

            yield {
                "type": "done",
                "content": full_response,
                "done": True,
                "generation_time": time.time() - start_time,
                "model": model,
            }

        except Exception as e:
            yield {"type": "error", "error": str(e), "done": True}

    async def reason_step_by_step(
        self,
        problem: str,
        agent_type: str = "orchestrator",
        max_steps: int = 5,
    ) -> BrainResponse:
        start_time = time.time()
        thinking_steps = []

        cot_prompt = f"""Solve this problem step by step. For each step:
1. State what you're thinking
2. What action you'll take
3. What result you expect

Problem: {problem}

Think through this systematically:"""

        response = await self.think(
            prompt=cot_prompt,
            agent_type=agent_type,
            task_type=ModelType.REASONING,
            temperature=0.5,
        )

        if response.error:
            return response

        lines = response.content.split("\n")
        current_step = 0
        current_thought = ""

        for line in lines:
            line = line.strip()
            if line.startswith(("Step", "1.", "2.", "3.", "4.", "5.")):
                if current_thought:
                    thinking_steps.append(ThinkingStep(
                        step=current_step,
                        thought=current_thought.strip(),
                    ))
                current_step += 1
                current_thought = line
            else:
                current_thought += " " + line

        if current_thought:
            thinking_steps.append(ThinkingStep(
                step=current_step,
                thought=current_thought.strip(),
            ))

        response.thinking = thinking_steps
        response.generation_time = time.time() - start_time
        return response

    async def analyze_code(
        self,
        code: str,
        language: str = "python",
        analysis_type: Literal["review", "explain", "optimize", "debug"] = "review",
    ) -> BrainResponse:
        prompts = {
            "review": f"""Review this {language} code for:
- Code quality and best practices
- Potential bugs or issues
- Security concerns
- Performance considerations

Code:
```{language}
{code}
```

Provide specific, actionable feedback:""",

            "explain": f"""Explain this {language} code clearly:
- What does it do overall?
- How does each part work?
- What are the key concepts used?

Code:
```{language}
{code}
```

Explanation:""",

            "optimize": f"""Optimize this {language} code for:
- Performance
- Memory usage
- Readability
- Maintainability

Code:
```{language}
{code}
```

Optimized version with explanations:""",

            "debug": f"""Debug this {language} code:
- Identify potential bugs
- Find logical errors
- Check edge cases
- Suggest fixes

Code:
```{language}
{code}
```

Issues found and fixes:""",
        }

        return await self.think(
            prompt=prompts[analysis_type],
            agent_type="coder" if analysis_type != "debug" else "debugger",
            task_type=ModelType.CODE,
        )

    async def generate_code(
        self,
        description: str,
        language: str = "python",
        context: Optional[str] = None,
        style_guide: Optional[str] = None,
    ) -> BrainResponse:
        prompt = f"""Generate {language} code for the following:

Description: {description}
"""
        if context:
            prompt += f"\nContext/Existing code:\n{context}\n"

        if style_guide:
            prompt += f"\nStyle guide: {style_guide}\n"

        prompt += """
Requirements:
- Clean, readable code
- Proper error handling
- Follow best practices
- Include type hints where applicable

Generate the code:"""

        return await self.think(
            prompt=prompt,
            agent_type="coder",
            task_type=ModelType.CODE,
        )

    async def plan_task(
        self,
        task_description: str,
        constraints: Optional[List[str]] = None,
    ) -> BrainResponse:
        prompt = f"""Create a detailed plan for this task:

Task: {task_description}
"""
        if constraints:
            prompt += f"\nConstraints:\n" + "\n".join(f"- {c}" for c in constraints)

        prompt += """

Provide:
1. Step-by-step plan
2. Required resources/tools
3. Potential challenges
4. Success criteria
5. Time/effort estimate

Plan:"""

        return await self.think(
            prompt=prompt,
            agent_type="orchestrator",
            task_type=ModelType.REASONING,
        )

    async def summarize(self, text: str, max_length: int = 200) -> BrainResponse:
        prompt = f"""Summarize the following text in {max_length} words or less.
Focus on key points and actionable information.

Text:
{text}

Summary:"""

        return await self.think(
            prompt=prompt,
            agent_type="researcher",
            task_type=ModelType.GENERAL,
            temperature=0.3,
        )

    async def extract_entities(self, text: str) -> BrainResponse:
        prompt = f"""Extract key entities from this text:

Text: {text}

Extract and categorize:
- Technical terms
- Tools/Technologies
- Concepts
- Actions/Tasks
- People/Organizations

Return as JSON:"""

        return await self.think(
            prompt=prompt,
            agent_type="researcher",
            task_type=ModelType.GENERAL,
            temperature=0.2,
        )

    def clear_history(self):
        self.conversation_history = []

    def get_status(self) -> Dict:
        return {
            "current_model": self.current_model,
            "available_models": self.list_models(),
            "history_length": len(self.conversation_history),
            "ollama_host": settings.OLLAMA_HOST,
        }


brain = Brain()


if __name__ == "__main__":
    async def test_brain():
        print("Testing Brain...")
        print(f"Status: {brain.get_status()}")

        print("\nTesting basic thinking...")
        response = await brain.think(
            "What is the best way to optimize Python code for performance?",
            agent_type="advisor",
        )
        print(f"Response: {response.content[:500]}...")
        print(f"Model: {response.model}")
        print(f"Time: {response.generation_time:.2f}s")

    asyncio.run(test_brain())
