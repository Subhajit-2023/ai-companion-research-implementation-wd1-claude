"""
Code Service - Code generation, analysis, and modification
"""
import asyncio
import subprocess
import tempfile
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json
import ast
import re
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import settings
from core.brain import brain, ModelType
from core.workflow import workflow_manager, ChangeType, ProposedChange


@dataclass
class CodeAnalysis:
    file_path: str
    language: str
    loc: int
    functions: List[str]
    classes: List[str]
    imports: List[str]
    issues: List[Dict]
    complexity_score: float
    suggestions: List[str]


@dataclass
class CodeChange:
    file_path: str
    original: str
    modified: str
    description: str
    change_type: str
    confidence: float


class CodeService:
    def __init__(self):
        self.supported_languages = {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".json": "json",
            ".md": "markdown",
            ".html": "html",
            ".css": "css",
        }

        self.project_path = Path(settings.COMPANION_PROJECT_PATH)

    async def analyze_file(self, file_path: str) -> Optional[CodeAnalysis]:
        path = Path(file_path)
        if not path.exists():
            return None

        language = self.supported_languages.get(path.suffix, "unknown")

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            return None

        loc = len(content.splitlines())
        functions = []
        classes = []
        imports = []
        issues = []

        if language == "python":
            functions, classes, imports = self._analyze_python(content)
            issues = await self._lint_python(path)
        elif language in ["javascript", "typescript"]:
            functions, classes, imports = self._analyze_javascript(content)
            issues = await self._lint_javascript(path)

        complexity = self._estimate_complexity(content, language)

        suggestions = await self._get_improvement_suggestions(content, language, issues)

        return CodeAnalysis(
            file_path=str(path),
            language=language,
            loc=loc,
            functions=functions,
            classes=classes,
            imports=imports,
            issues=issues,
            complexity_score=complexity,
            suggestions=suggestions,
        )

    def _analyze_python(self, content: str) -> Tuple[List[str], List[str], List[str]]:
        functions = []
        classes = []
        imports = []

        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                elif isinstance(node, ast.AsyncFunctionDef):
                    functions.append(f"async {node.name}")
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}")

        except SyntaxError:
            pass

        return functions, classes, imports

    def _analyze_javascript(self, content: str) -> Tuple[List[str], List[str], List[str]]:
        functions = []
        classes = []
        imports = []

        func_patterns = [
            r"function\s+(\w+)",
            r"const\s+(\w+)\s*=\s*(?:async\s*)?\(",
            r"(\w+)\s*:\s*(?:async\s*)?\(",
        ]

        for pattern in func_patterns:
            matches = re.findall(pattern, content)
            functions.extend(matches)

        class_matches = re.findall(r"class\s+(\w+)", content)
        classes.extend(class_matches)

        import_matches = re.findall(r"import\s+.*?from\s+['\"](.+?)['\"]", content)
        imports.extend(import_matches)

        require_matches = re.findall(r"require\(['\"](.+?)['\"]\)", content)
        imports.extend(require_matches)

        return list(set(functions)), list(set(classes)), list(set(imports))

    async def _lint_python(self, file_path: Path) -> List[Dict]:
        issues = []

        try:
            result = subprocess.run(
                ["python", "-m", "py_compile", str(file_path)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                issues.append({
                    "type": "syntax_error",
                    "message": result.stderr,
                    "severity": "error",
                })
        except Exception:
            pass

        try:
            result = subprocess.run(
                ["ruff", "check", str(file_path), "--output-format=json"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.stdout:
                ruff_issues = json.loads(result.stdout)
                for issue in ruff_issues:
                    issues.append({
                        "type": "lint",
                        "code": issue.get("code", ""),
                        "message": issue.get("message", ""),
                        "line": issue.get("location", {}).get("row", 0),
                        "severity": "warning",
                    })
        except Exception:
            pass

        return issues

    async def _lint_javascript(self, file_path: Path) -> List[Dict]:
        issues = []

        try:
            result = subprocess.run(
                ["npx", "eslint", str(file_path), "-f", "json"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.stdout:
                eslint_results = json.loads(result.stdout)
                for file_result in eslint_results:
                    for msg in file_result.get("messages", []):
                        issues.append({
                            "type": "lint",
                            "code": msg.get("ruleId", ""),
                            "message": msg.get("message", ""),
                            "line": msg.get("line", 0),
                            "severity": "error" if msg.get("severity") == 2 else "warning",
                        })
        except Exception:
            pass

        return issues

    def _estimate_complexity(self, content: str, language: str) -> float:
        loc = len(content.splitlines())
        if loc == 0:
            return 0.0

        nested_depth = 0
        max_depth = 0
        conditionals = 0
        loops = 0

        for line in content.splitlines():
            stripped = line.strip()

            indent = len(line) - len(line.lstrip())
            current_depth = indent // 4 if language == "python" else line.count("{") - line.count("}")
            max_depth = max(max_depth, current_depth)

            if any(kw in stripped for kw in ["if ", "elif ", "else:", "switch", "case"]):
                conditionals += 1
            if any(kw in stripped for kw in ["for ", "while ", "foreach"]):
                loops += 1

        complexity = (
            (conditionals * 0.3) +
            (loops * 0.4) +
            (max_depth * 0.2) +
            (loc / 100 * 0.1)
        )

        return min(10.0, complexity)

    async def _get_improvement_suggestions(
        self,
        content: str,
        language: str,
        issues: List[Dict],
    ) -> List[str]:
        if not issues and len(content) < 100:
            return []

        prompt = f"""Analyze this {language} code and provide 3-5 specific improvement suggestions:

```{language}
{content[:3000]}
```

Known issues:
{json.dumps(issues[:5], indent=2) if issues else 'None detected'}

Provide concise, actionable suggestions:"""

        response = await brain.think(
            prompt=prompt,
            agent_type="coder",
            task_type=ModelType.CODE,
            temperature=0.3,
        )

        if response.error:
            return []

        suggestions = []
        for line in response.content.split("\n"):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith("-")):
                suggestions.append(line.lstrip("0123456789.-) "))

        return suggestions[:5]

    async def generate_code(
        self,
        description: str,
        language: str = "python",
        context: Optional[str] = None,
        file_path: Optional[str] = None,
    ) -> Optional[CodeChange]:
        prompt = f"""Generate {language} code for:

{description}
"""
        if context:
            prompt += f"\nExisting context:\n```{language}\n{context[:2000]}\n```\n"

        if file_path:
            prompt += f"\nTarget file: {file_path}\n"

        prompt += """
Requirements:
- Clean, readable code
- Proper error handling
- Follow best practices
- Match existing code style if context provided

Generate only the code, no explanations:"""

        response = await brain.think(
            prompt=prompt,
            agent_type="coder",
            task_type=ModelType.CODE,
        )

        if response.error:
            return None

        code = self._extract_code_block(response.content, language)

        return CodeChange(
            file_path=file_path or "new_file",
            original=context or "",
            modified=code,
            description=description,
            change_type="generate",
            confidence=0.8,
        )

    def _extract_code_block(self, content: str, language: str) -> str:
        patterns = [
            rf"```{language}\n(.*?)```",
            r"```\n(.*?)```",
            rf"```{language}(.*?)```",
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                return match.group(1).strip()

        return content.strip()

    async def modify_code(
        self,
        file_path: str,
        modification: str,
        preserve_structure: bool = True,
    ) -> Optional[CodeChange]:
        path = Path(file_path)
        if not path.exists():
            return None

        with open(path, "r") as f:
            original = f.read()

        language = self.supported_languages.get(path.suffix, "unknown")

        prompt = f"""Modify this {language} code according to the request:

Request: {modification}

Original code:
```{language}
{original}
```

{"Preserve the overall structure and only make minimal necessary changes." if preserve_structure else ""}

Return the complete modified code:"""

        response = await brain.think(
            prompt=prompt,
            agent_type="coder",
            task_type=ModelType.CODE,
        )

        if response.error:
            return None

        modified = self._extract_code_block(response.content, language)

        return CodeChange(
            file_path=str(path),
            original=original,
            modified=modified,
            description=modification,
            change_type="modify",
            confidence=0.7,
        )

    async def apply_change(
        self,
        change: CodeChange,
        require_approval: bool = True,
    ) -> bool:
        if require_approval:
            proposed = workflow_manager.propose_change(
                task_id="code_change",
                change_type=ChangeType.FILE_MODIFY,
                title=f"Code change: {change.description[:50]}",
                description=change.description,
                file_path=change.file_path,
                original_content=change.original,
                new_content=change.modified,
                rationale=f"Generated code modification with {change.confidence:.0%} confidence",
            )

            request = workflow_manager.create_approval_request(
                task_id="code_change",
                changes=[proposed],
                summary=f"Apply code change to {change.file_path}",
            )

            if request.status.value not in ["approved", "auto_approved"]:
                return False

        try:
            with open(change.file_path, "w") as f:
                f.write(change.modified)
            return True
        except Exception as e:
            print(f"Error applying change: {e}")
            return False

    async def analyze_project(self, project_path: Optional[str] = None) -> Dict:
        path = Path(project_path or settings.COMPANION_PROJECT_PATH)

        analysis = {
            "path": str(path),
            "files": [],
            "total_loc": 0,
            "total_functions": 0,
            "total_classes": 0,
            "issues_count": 0,
            "by_language": {},
        }

        for suffix, language in self.supported_languages.items():
            for file_path in path.rglob(f"*{suffix}"):
                if "node_modules" in str(file_path) or "__pycache__" in str(file_path):
                    continue

                file_analysis = await self.analyze_file(str(file_path))
                if file_analysis:
                    analysis["files"].append({
                        "path": str(file_path),
                        "language": language,
                        "loc": file_analysis.loc,
                        "complexity": file_analysis.complexity_score,
                        "issues": len(file_analysis.issues),
                    })

                    analysis["total_loc"] += file_analysis.loc
                    analysis["total_functions"] += len(file_analysis.functions)
                    analysis["total_classes"] += len(file_analysis.classes)
                    analysis["issues_count"] += len(file_analysis.issues)

                    if language not in analysis["by_language"]:
                        analysis["by_language"][language] = {"files": 0, "loc": 0}
                    analysis["by_language"][language]["files"] += 1
                    analysis["by_language"][language]["loc"] += file_analysis.loc

        return analysis

    async def find_similar_code(
        self,
        code_snippet: str,
        project_path: Optional[str] = None,
    ) -> List[Dict]:
        path = Path(project_path or settings.COMPANION_PROJECT_PATH)
        similar = []

        snippet_lines = set(line.strip() for line in code_snippet.splitlines() if line.strip())

        for suffix in self.supported_languages:
            for file_path in path.rglob(f"*{suffix}"):
                if "node_modules" in str(file_path) or "__pycache__" in str(file_path):
                    continue

                try:
                    with open(file_path, "r") as f:
                        content = f.read()

                    file_lines = set(line.strip() for line in content.splitlines() if line.strip())
                    overlap = len(snippet_lines & file_lines)

                    if overlap > 0:
                        similarity = overlap / max(len(snippet_lines), 1)
                        if similarity > 0.3:
                            similar.append({
                                "file": str(file_path),
                                "similarity": similarity,
                                "matching_lines": overlap,
                            })

                except Exception:
                    continue

        return sorted(similar, key=lambda x: x["similarity"], reverse=True)[:10]


code_service = CodeService()


if __name__ == "__main__":
    async def test_code_service():
        print("Testing Code Service...")

        print("\nAnalyzing project...")
        analysis = await code_service.analyze_project()
        print(f"Total files: {len(analysis['files'])}")
        print(f"Total LOC: {analysis['total_loc']}")
        print(f"Languages: {list(analysis['by_language'].keys())}")

    asyncio.run(test_code_service())
