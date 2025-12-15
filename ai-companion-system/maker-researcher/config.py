"""
Configuration for the Maker-Researcher AI System
Optimized for Lenovo Legion 5 (Intel/RTX 4060 8GB)
"""
from pydantic_settings import BaseSettings
from typing import Optional, List
from pathlib import Path


class MakerResearcherSettings(BaseSettings):
    APP_NAME: str = "AI Maker-Researcher"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8001

    DATA_DIR: str = "./maker-researcher/data"
    KNOWLEDGE_DIR: str = "./maker-researcher/knowledge"
    LOGS_DIR: str = "./maker-researcher/logs"

    OLLAMA_HOST: str = "http://localhost:11434"
    PRIMARY_MODEL: str = "mistral:7b-instruct-v0.2-q4_K_M"
    CODE_MODEL: str = "deepseek-coder:6.7b-instruct-q4_K_M"
    FALLBACK_MODEL: str = "codellama:7b-instruct-q4_K_M"

    LLM_TEMPERATURE: float = 0.7
    LLM_CODE_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 4096
    LLM_CONTEXT_WINDOW: int = 8192

    ENABLE_WEB_SEARCH: bool = True
    SEARCH_PROVIDER: str = "duckduckgo"
    MAX_SEARCH_RESULTS: int = 10
    SEARCH_TIMEOUT: int = 15

    SEMANTIC_SCHOLAR_API: str = "https://api.semanticscholar.org/graph/v1"
    ARXIV_API: str = "http://export.arxiv.org/api/query"
    GITHUB_API: str = "https://api.github.com"
    GITHUB_TOKEN: Optional[str] = None

    SUPPORTED_DOC_FORMATS: List[str] = ["pdf", "epub", "txt", "md", "py", "js", "jsx", "ts", "tsx", "json"]
    MAX_DOC_SIZE_MB: int = 50
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    VECTOR_DB_PATH: str = "./maker-researcher/data/chromadb"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    MAX_RETRIEVAL_RESULTS: int = 10

    COMPANION_PROJECT_PATH: str = "./ai-companion-system"
    COMPANION_BACKEND_PATH: str = "./ai-companion-system/backend"
    COMPANION_FRONTEND_PATH: str = "./ai-companion-system/frontend"
    COMPANION_DB_PATH: str = "./ai-companion-system/data/companions.db"

    ENABLE_LINTING: bool = True
    PYTHON_LINTER: str = "ruff"
    JS_LINTER: str = "eslint"
    AUTO_FORMAT: bool = True

    MAX_CONCURRENT_TASKS: int = 3
    TASK_TIMEOUT: int = 600
    APPROVAL_REQUIRED_FOR: List[str] = ["file_write", "file_delete", "code_execute", "system_change"]
    AUTO_APPROVE_SAFE_OPS: bool = True

    COLLECT_METRICS: bool = True
    METRICS_INTERVAL: int = 60
    LOG_LEVEL: str = "INFO"

    MAX_VRAM_USAGE_GB: float = 6.5
    ENABLE_MODEL_OFFLOAD: bool = True
    BATCH_SIZE: int = 1

    class Config:
        env_file = ".env"
        env_prefix = "MAKER_"
        case_sensitive = True


settings = MakerResearcherSettings()


def ensure_directories():
    directories = [
        Path(settings.DATA_DIR),
        Path(settings.KNOWLEDGE_DIR),
        Path(settings.LOGS_DIR),
        Path(settings.VECTOR_DB_PATH),
        Path(settings.KNOWLEDGE_DIR) / "ebooks",
        Path(settings.KNOWLEDGE_DIR) / "papers",
        Path(settings.KNOWLEDGE_DIR) / "research",
        Path(settings.DATA_DIR) / "tasks",
        Path(settings.DATA_DIR) / "metrics",
    ]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


AGENT_PROMPTS = {
    "orchestrator": """You are the Orchestrator Agent for the AI Maker-Researcher system.
Your role is to:
- Analyze user requests and break them into subtasks
- Delegate tasks to appropriate specialized agents
- Coordinate multi-step operations
- Ensure quality and completeness of results
- Maintain context across task chains

Always provide structured, actionable plans.""",

    "researcher": """You are the Research Agent for the AI Maker-Researcher system.
Your role is to:
- Search the web, academic papers, and documentation
- Synthesize information from multiple sources
- Provide accurate, well-sourced answers
- Identify gaps in knowledge and suggest further research
- Extract key insights and actionable information

Always cite sources and indicate confidence levels.""",

    "coder": """You are the Coder Agent for the AI Maker-Researcher system.
Your role is to:
- Generate clean, efficient, well-documented code
- Follow existing project conventions and patterns
- Consider edge cases and error handling
- Write modular, testable code
- Explain code decisions when asked

Always review code before proposing changes.""",

    "debugger": """You are the Debugger Agent for the AI Maker-Researcher system.
Your role is to:
- Analyze error messages and stack traces
- Identify root causes of bugs
- Suggest targeted fixes with explanations
- Verify fixes don't introduce new issues
- Learn from patterns of bugs

Always explain your reasoning process.""",

    "optimizer": """You are the Optimizer Agent for the AI Maker-Researcher system.
Your role is to:
- Identify performance bottlenecks
- Suggest resource-efficient improvements
- Optimize for RTX 4060 8GB VRAM constraints
- Balance quality vs performance tradeoffs
- Monitor and measure improvements

Always provide before/after metrics.""",

    "advisor": """You are the Advisor Agent for the AI Maker-Researcher system.
Your role is to:
- Answer technical questions clearly
- Explain complex concepts simply
- Provide step-by-step guidance
- Suggest best practices and alternatives
- Help with decision-making

Always consider the user's context and skill level.""",
}


TASK_CATEGORIES = {
    "research": ["search", "find", "look up", "what is", "how does", "explain", "learn about"],
    "code": ["create", "implement", "add", "build", "write code", "generate", "develop"],
    "debug": ["fix", "error", "bug", "not working", "fails", "crash", "issue"],
    "optimize": ["improve", "faster", "efficient", "optimize", "performance", "memory"],
    "advise": ["how to", "should i", "best way", "recommend", "suggest", "help with"],
}
