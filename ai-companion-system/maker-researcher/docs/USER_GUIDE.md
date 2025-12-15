# AI Maker-Researcher System - Complete User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
4. [Quick Start](#quick-start)
5. [Core Concepts](#core-concepts)
6. [CLI Reference](#cli-reference)
7. [API Reference](#api-reference)
8. [Research Features](#research-features)
9. [Code Generation & Analysis](#code-generation--analysis)
10. [Debugging Tools](#debugging-tools)
11. [Knowledge Base](#knowledge-base)
12. [Task Management](#task-management)
13. [Approval Workflow](#approval-workflow)
14. [Performance Optimization](#performance-optimization)
15. [Troubleshooting](#troubleshooting)

---

## Introduction

The AI Maker-Researcher is an autonomous AI system designed to assist with research, development, and continuous improvement of software projects. It acts as your personal AI research assistant, capable of:

- **Researching** topics across the web, academic papers, and code repositories
- **Generating** code based on natural language descriptions
- **Analyzing** existing codebases for quality and improvements
- **Debugging** errors with intelligent root cause analysis
- **Learning** from your documents and eBooks
- **Optimizing** system performance for your hardware

### Key Philosophy

The system follows a **Human-in-the-Loop** approach:
- You maintain control over all file modifications
- Changes require your approval before being applied
- Risk levels are assessed for every proposed change
- Rollback plans are provided for safety

---

## System Requirements

### Hardware (Recommended)
- **CPU**: Intel Core i5/i7 or AMD Ryzen 5/7
- **RAM**: 16GB minimum (32GB recommended)
- **GPU**: NVIDIA RTX 4060 8GB or equivalent
- **Storage**: 50GB free space for models and data

### Software
- Python 3.10 or higher
- Ollama (for local LLM inference)
- Node.js 18+ (for frontend)

### Required Models (via Ollama)
```bash
# Primary model for general tasks
ollama pull mistral:7b-instruct-v0.2-q4_K_M

# Code-specialized model
ollama pull deepseek-coder:6.7b-instruct-q4_K_M
```

---

## Installation

### Step 1: Install Dependencies

```bash
cd ai-companion-system/maker-researcher
pip install -r requirements.txt
```

### Step 2: Verify Ollama is Running

```bash
ollama serve
# In another terminal:
ollama list  # Should show your installed models
```

### Step 3: Start the System

**Interactive CLI:**
```bash
python run.py
```

**API Server:**
```bash
python run.py --api
```

---

## Quick Start

### Example 1: Research a Topic

```
researcher> research Python async best practices

Researching: Python async best practices
This may take a moment...

============================================================
Research Session: a1b2c3d4
============================================================
Web Results: 10
Academic Papers: 5
Code Examples: 8

--- Top Web Results ---
  - Real Python: Async IO in Python
    https://realpython.com/async-io-python/
...
```

### Example 2: Generate Code

```
researcher> code Create a FastAPI endpoint for user authentication

Generating code for: Create a FastAPI endpoint for user authentication

============================================================
Generated Code:
============================================================
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
...

Confidence: 85%
```

### Example 3: Debug an Error

```
researcher> debug TypeError: 'NoneType' object is not subscriptable at line 42

Analyzing error...

============================================================
Debug Analysis
============================================================
Error Type: TypeError
Message: 'NoneType' object is not subscriptable

Analysis:
The error indicates you're trying to access an index or key on a variable
that is None. This commonly happens when:
1. A function returns None instead of expected data
2. A dictionary lookup returns None
...
```

---

## Core Concepts

### Agents

The system uses specialized agents for different tasks:

| Agent | Purpose | Triggered By |
|-------|---------|--------------|
| **Orchestrator** | Coordinates all agents, breaks down complex tasks | Complex requests |
| **Researcher** | Web search, paper lookup, code discovery | "research", "find", "look up" |
| **Coder** | Code generation, modification, analysis | "create", "implement", "build" |
| **Debugger** | Error analysis, fix suggestions | "fix", "debug", "error" |
| **Optimizer** | Performance analysis, improvement suggestions | "optimize", "improve", "faster" |
| **Advisor** | General guidance, explanations | "explain", "how to", "help" |

### Task Categories

Tasks are automatically categorized:

- **Research**: Information gathering and synthesis
- **Code**: Generation, modification, or analysis
- **Debug**: Error investigation and fixes
- **Optimize**: Performance improvements
- **Advise**: General questions and guidance
- **System**: Internal system operations

### Risk Levels

Every proposed change has a risk level:

| Level | Description | Approval |
|-------|-------------|----------|
| **Safe** | Read-only operations | Auto-approved |
| **Low** | New files, minor changes | Auto-approved (configurable) |
| **Medium** | Existing file modifications | Manual approval |
| **High** | Config changes, deletions | Manual approval |
| **Critical** | System commands, security files | Manual approval + confirmation |

---

## CLI Reference

### General Commands

| Command | Description | Example |
|---------|-------------|---------|
| `help` | Show all commands | `help` |
| `status` | System status | `status` |
| `health` | Health check | `health` |
| `metrics` | Performance metrics | `metrics` |
| `exit` | Exit CLI | `exit` |

### Research Commands

| Command | Description | Example |
|---------|-------------|---------|
| `research <query>` | Comprehensive research | `research LLM optimization techniques` |
| `chat <message>` | Conversational interaction | `chat What's the best way to...` |

### Code Commands

| Command | Description | Example |
|---------|-------------|---------|
| `code <description>` | Generate code | `code REST API for todo app` |
| `analyze <file>` | Analyze a file | `analyze src/main.py` |

### Debug Commands

| Command | Description | Example |
|---------|-------------|---------|
| `debug <error>` | Analyze error | `debug ImportError: No module named 'xyz'` |

### Task Commands

| Command | Description | Example |
|---------|-------------|---------|
| `task create <title>` | Create new task | `task create Add caching` |
| `task list` | List all tasks | `task list` |

### Document Commands

| Command | Description | Example |
|---------|-------------|---------|
| `doc add <path>` | Add document | `doc add ~/books/python.pdf` |
| `doc list` | List documents | `doc list` |
| `doc search <query>` | Search knowledge | `doc search async patterns` |

### Approval Commands

| Command | Description | Example |
|---------|-------------|---------|
| `approve list` | Pending approvals | `approve list` |
| `approve <id>` | Approve change | `approve a1b2c3` |
| `reject <id> [reason]` | Reject change | `reject a1b2c3 Not needed` |

---

## API Reference

### Base URL
```
http://localhost:8001
```

### Endpoints

#### Chat
```http
POST /chat
Content-Type: application/json

{
  "message": "How do I optimize Python code?"
}
```

#### Research
```http
POST /research
Content-Type: application/json

{
  "query": "machine learning optimization",
  "include_papers": true,
  "include_code": true
}
```

#### Generate Code
```http
POST /code/generate
Content-Type: application/json

{
  "description": "Create a user authentication system",
  "language": "python"
}
```

#### Debug Error
```http
POST /debug
Content-Type: application/json

{
  "error_text": "TypeError: cannot unpack...",
  "language": "python"
}
```

#### System Metrics
```http
GET /metrics/system
```

#### Task Management
```http
GET /tasks
POST /tasks
GET /tasks/{task_id}
DELETE /tasks/{task_id}
```

#### Approvals
```http
GET /approvals
GET /approvals/{request_id}
POST /approvals/{request_id}
```

---

## Research Features

### Web Search
- Uses DuckDuckGo for privacy-respecting search
- Returns top 10 results with snippets
- Automatic relevance scoring

### Academic Papers
- **ArXiv**: Latest preprints in AI, CS, Math, Physics
- **Semantic Scholar**: Citation counts, author info

### Code Discovery
- **GitHub Repositories**: Stars, description, topics
- **Code Search**: Find implementations by keyword

### Comprehensive Research
Combines all sources into a single session:
```
researcher> research transformer architecture optimization

# Returns:
- 10 web articles
- 5 academic papers
- 8 GitHub repositories
- Synthesized summary
```

---

## Code Generation & Analysis

### Generate Code
```
researcher> code Create a rate limiter middleware for Express.js

# Outputs:
- Complete implementation
- Error handling
- Usage examples
- Confidence score
```

### Analyze File
```
researcher> analyze backend/api/main.py

# Shows:
- Lines of code
- Function/class count
- Complexity score (0-10)
- Detected issues
- Improvement suggestions
```

### Project Analysis
Through the API:
```http
GET /code/project?project_path=./my-project
```

Returns aggregate metrics for the entire codebase.

---

## Debugging Tools

### Error Analysis
```
researcher> debug Traceback (most recent call last):
  File "app.py", line 42, in process
    return data['key']
KeyError: 'key'
```

**Output includes:**
1. Error type identification
2. Root cause analysis
3. Step-by-step debugging guide
4. Specific fix suggestions
5. Prevention tips

### Common Error Reference
The system maintains a database of common errors:
- Python: IndentationError, ImportError, TypeError, KeyError
- JavaScript: TypeError, ReferenceError, SyntaxError

---

## Knowledge Base

### Supported Formats
- **PDF**: Books, papers, documentation
- **EPUB**: eBooks
- **Text**: TXT, MD, source code files

### Adding Documents
```
researcher> doc add ~/Documents/python_cookbook.pdf

Processing: python_cookbook.pdf

============================================================
Document Processed
============================================================
ID: abc123
Title: Python Cookbook
Author: David Beazley
Pages: 706
Chunks: 1420
```

### Searching Knowledge
```
researcher> doc search decorator patterns

============================================================
Search Results (5)
============================================================

  Document: Python Cookbook
  Content: Decorators are a powerful pattern for modifying
  function behavior. The @wraps decorator preserves...
```

### Vector Embeddings
- Documents are chunked (1000 chars with 200 overlap)
- Embedded using sentence-transformers
- Stored in ChromaDB for semantic search

---

## Task Management

### Task Lifecycle

```
PENDING -> IN_PROGRESS -> COMPLETED
                      \-> FAILED
                      \-> AWAITING_APPROVAL -> APPROVED -> COMPLETED
                                            \-> REJECTED
```

### Creating Tasks
```
researcher> task create Implement caching layer

What should this task do? (enter description)
> Add Redis caching to reduce database queries

Category (research/code/debug/optimize/advise):
> code

Task created: t1a2b3c4
Title: Implement caching layer
Status: pending
```

### Viewing Tasks
```
researcher> task list

============================================================
Tasks (5)
============================================================
  [+] t1a2b3c4: Implement caching layer
  [*] t2b3c4d5: Research best practices
  [.] t3c4d5e6: Optimize database queries
  [?] t4d5e6f7: Add authentication (awaiting approval)
  [x] t5e6f7g8: Fix login bug (failed)

Total: 5 | Running: 1 | Completed: 1
```

---

## Approval Workflow

### Why Approvals?
Every file modification goes through approval to:
- Prevent unintended changes
- Allow review before applying
- Provide rollback capability

### Viewing Pending Approvals
```
researcher> approve list

============================================================
Pending Approvals (2)
============================================================

  ID: req_a1b2
  Task: Implement caching
  Summary: Add Redis connection pool
  Changes: 2

  ID: req_c3d4
  Task: Fix authentication
  Summary: Update password hashing
  Changes: 1
```

### Reviewing a Change
```
researcher> approve req_a1b2

# Shows:
- File path
- Diff (before/after)
- Risk level
- Rationale
- Rollback plan

To approve: approve req_a1b2
To reject: reject req_a1b2 [reason]
```

### Approving
```
researcher> approve req_a1b2
Approved: req_a1b2
```

### Rejecting
```
researcher> reject req_a1b2 Not the right approach
Rejected: req_a1b2
```

---

## Performance Optimization

### RTX 4060 Optimizations

The system includes specific optimizations for RTX 4060 8GB:

```
researcher> optimize

============================================================
Optimization Analysis
============================================================

Current System:
  Memory: 72.3%
  GPU: 85.2%
  VRAM: 6.1GB

Bottlenecks:
  - GPU memory pressure

Recommendations:
  - Use 4-bit quantized models (q4_K_M)
  - Set context window to 4096
  - Enable model offloading for long sessions
  - Limit concurrent LLM requests to 1
```

### Model Selection Guide

| Model | VRAM | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| mistral:7b-q4_K_M | 4.5GB | Fast | Good | General chat |
| deepseek-coder:6.7b-q4 | 4GB | Fast | Excellent | Code tasks |
| codellama:7b-q4 | 4GB | Fast | Good | Code fallback |

### Memory Tips
- Close other GPU applications
- Use smaller context windows (4096 vs 8192)
- Enable model offloading in config
- Clear CUDA cache periodically

---

## Troubleshooting

### Common Issues

#### "Ollama connection refused"
```bash
# Ensure Ollama is running:
ollama serve

# Check it's accessible:
curl http://localhost:11434/api/tags
```

#### "Model not found"
```bash
# Pull the required model:
ollama pull mistral:7b-instruct-v0.2-q4_K_M
```

#### "Out of GPU memory"
1. Close other applications using GPU
2. Use smaller model quantization (q4 instead of q8)
3. Reduce context window in config
4. Enable model offloading

#### "Search not returning results"
- Check internet connectivity
- DuckDuckGo may have rate limits - wait and retry
- Try more specific search terms

#### "Document processing failed"
- Ensure file format is supported (PDF, EPUB, TXT)
- Check file isn't corrupted
- Verify file size is under 50MB

### Getting Help

1. Check logs in `maker-researcher/logs/`
2. Run health check: `health`
3. View system metrics: `metrics`
4. Check status: `status`

---

## Configuration

Edit `maker-researcher/config.py` to customize:

```python
# Model settings
PRIMARY_MODEL = "mistral:7b-instruct-v0.2-q4_K_M"
LLM_TEMPERATURE = 0.7
LLM_CONTEXT_WINDOW = 8192

# Search settings
MAX_SEARCH_RESULTS = 10
SEARCH_TIMEOUT = 15

# Document settings
MAX_DOC_SIZE_MB = 50
CHUNK_SIZE = 1000

# Approval settings
AUTO_APPROVE_SAFE_OPS = True
APPROVAL_REQUIRED_FOR = ["file_write", "file_delete", "code_execute"]
```

---

## Best Practices

1. **Be specific** in your requests for better results
2. **Review approvals** carefully before accepting
3. **Add relevant documents** to improve knowledge
4. **Monitor performance** during heavy tasks
5. **Use appropriate models** for different task types
6. **Keep tasks focused** - break complex work into steps

---

*Last updated: December 2024*
