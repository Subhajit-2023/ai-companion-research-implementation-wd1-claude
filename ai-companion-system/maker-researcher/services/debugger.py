"""
Debugger Service - Error analysis, bug detection, and fix suggestions
"""
import asyncio
import re
import traceback
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import settings
from core.brain import brain, ModelType


@dataclass
class ErrorInfo:
    error_type: str
    message: str
    file_path: Optional[str]
    line_number: Optional[int]
    stack_trace: str
    context_code: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class BugReport:
    id: str
    title: str
    description: str
    error_info: Optional[ErrorInfo]
    severity: str
    status: str
    root_cause: str
    suggested_fixes: List[Dict]
    related_files: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class FixSuggestion:
    description: str
    code_change: str
    file_path: str
    confidence: float
    risk_level: str
    explanation: str


class DebuggerService:
    def __init__(self):
        self.error_patterns = self._init_error_patterns()
        self.bug_history: List[BugReport] = []
        self.fix_success_rate: Dict[str, float] = {}
        self.data_dir = Path(settings.DATA_DIR) / "debug"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._load_history()

    def _init_error_patterns(self) -> Dict[str, Dict]:
        return {
            "python": {
                "traceback": r"Traceback \(most recent call last\):",
                "file_line": r'File "([^"]+)", line (\d+)',
                "error_type": r"(\w+Error|\w+Exception): (.+)$",
                "syntax_error": r"SyntaxError: (.+)",
                "import_error": r"(Import|Module)Error: (.+)",
                "type_error": r"TypeError: (.+)",
                "attribute_error": r"AttributeError: (.+)",
                "key_error": r"KeyError: (.+)",
                "index_error": r"IndexError: (.+)",
                "value_error": r"ValueError: (.+)",
            },
            "javascript": {
                "error_type": r"(\w+Error): (.+)",
                "at_line": r"at .+ \(([^)]+):(\d+):(\d+)\)",
                "syntax_error": r"SyntaxError: (.+)",
                "type_error": r"TypeError: (.+)",
                "reference_error": r"ReferenceError: (.+)",
                "range_error": r"RangeError: (.+)",
            },
        }

    def _load_history(self):
        history_file = self.data_dir / "bug_history.json"
        if history_file.exists():
            try:
                with open(history_file, "r") as f:
                    data = json.load(f)
                    self.fix_success_rate = data.get("success_rates", {})
            except Exception:
                pass

    def _save_history(self):
        history_file = self.data_dir / "bug_history.json"
        try:
            data = {
                "success_rates": self.fix_success_rate,
                "total_bugs": len(self.bug_history),
                "updated_at": datetime.utcnow().isoformat(),
            }
            with open(history_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving debug history: {e}")

    def parse_error(self, error_text: str, language: str = "python") -> ErrorInfo:
        patterns = self.error_patterns.get(language, self.error_patterns["python"])

        error_type = "Unknown"
        message = error_text
        file_path = None
        line_number = None
        stack_trace = error_text
        context_code = ""

        if language == "python":
            type_match = re.search(patterns["error_type"], error_text, re.MULTILINE)
            if type_match:
                error_type = type_match.group(1)
                message = type_match.group(2)

            file_matches = re.findall(patterns["file_line"], error_text)
            if file_matches:
                file_path, line_str = file_matches[-1]
                line_number = int(line_str)

                if Path(file_path).exists():
                    context_code = self._get_code_context(file_path, line_number)

        elif language == "javascript":
            type_match = re.search(patterns["error_type"], error_text)
            if type_match:
                error_type = type_match.group(1)
                message = type_match.group(2)

            line_match = re.search(patterns["at_line"], error_text)
            if line_match:
                file_path = line_match.group(1)
                line_number = int(line_match.group(2))

                if Path(file_path).exists():
                    context_code = self._get_code_context(file_path, line_number)

        return ErrorInfo(
            error_type=error_type,
            message=message,
            file_path=file_path,
            line_number=line_number,
            stack_trace=stack_trace,
            context_code=context_code,
        )

    def _get_code_context(self, file_path: str, line_number: int, context_lines: int = 5) -> str:
        try:
            with open(file_path, "r") as f:
                lines = f.readlines()

            start = max(0, line_number - context_lines - 1)
            end = min(len(lines), line_number + context_lines)

            context = []
            for i in range(start, end):
                prefix = ">>> " if i == line_number - 1 else "    "
                context.append(f"{i+1:4d}{prefix}{lines[i].rstrip()}")

            return "\n".join(context)

        except Exception:
            return ""

    async def analyze_error(self, error_text: str, language: str = "python") -> Dict:
        error_info = self.parse_error(error_text, language)

        prompt = f"""Analyze this {language} error and provide debugging guidance:

Error Type: {error_info.error_type}
Error Message: {error_info.message}
File: {error_info.file_path or 'Unknown'}
Line: {error_info.line_number or 'Unknown'}

Stack Trace:
{error_info.stack_trace[:2000]}

Code Context:
{error_info.context_code}

Provide:
1. Root cause analysis
2. Step-by-step debugging approach
3. Specific fix suggestions
4. Prevention tips

Analysis:"""

        response = await brain.think(
            prompt=prompt,
            agent_type="debugger",
            task_type=ModelType.REASONING,
        )

        return {
            "error_info": {
                "type": error_info.error_type,
                "message": error_info.message,
                "file": error_info.file_path,
                "line": error_info.line_number,
            },
            "analysis": response.content,
            "confidence": 0.8 if not response.error else 0.0,
        }

    async def suggest_fix(
        self,
        error_info: ErrorInfo,
        additional_context: Optional[str] = None,
    ) -> List[FixSuggestion]:
        if not error_info.file_path or not error_info.context_code:
            return []

        prompt = f"""Suggest specific code fixes for this error:

Error: {error_info.error_type}: {error_info.message}
File: {error_info.file_path}
Line: {error_info.line_number}

Code:
{error_info.context_code}

{f"Additional context: {additional_context}" if additional_context else ""}

Provide 2-3 specific fix suggestions with:
1. What to change
2. The exact code modification
3. Why this fixes the issue
4. Confidence level (high/medium/low)

Fixes:"""

        response = await brain.think(
            prompt=prompt,
            agent_type="debugger",
            task_type=ModelType.CODE,
        )

        if response.error:
            return []

        return self._parse_fix_suggestions(response.content, error_info.file_path)

    def _parse_fix_suggestions(self, content: str, file_path: str) -> List[FixSuggestion]:
        suggestions = []

        sections = re.split(r"\n(?=\d+\.|Fix \d+|Option \d+)", content)

        for section in sections:
            if not section.strip():
                continue

            code_match = re.search(r"```[\w]*\n(.*?)```", section, re.DOTALL)
            code_change = code_match.group(1).strip() if code_match else ""

            confidence = 0.5
            if "high" in section.lower():
                confidence = 0.8
            elif "medium" in section.lower():
                confidence = 0.6
            elif "low" in section.lower():
                confidence = 0.3

            risk = "low"
            if "risk" in section.lower() or "careful" in section.lower():
                risk = "medium"
            if "major" in section.lower() or "significant" in section.lower():
                risk = "high"

            description = section.split("\n")[0].strip()
            description = re.sub(r"^\d+\.\s*|^Fix\s*\d+[:.]\s*|^Option\s*\d+[:.]\s*", "", description)

            if code_change or description:
                suggestions.append(FixSuggestion(
                    description=description[:200],
                    code_change=code_change,
                    file_path=file_path,
                    confidence=confidence,
                    risk_level=risk,
                    explanation=section[:500],
                ))

        return suggestions[:3]

    async def analyze_logs(
        self,
        log_content: str,
        log_type: str = "application",
    ) -> Dict:
        prompt = f"""Analyze these {log_type} logs for issues:

{log_content[:5000]}

Identify:
1. Error patterns
2. Warning signs
3. Performance issues
4. Anomalies
5. Recommendations

Analysis:"""

        response = await brain.think(
            prompt=prompt,
            agent_type="debugger",
            task_type=ModelType.REASONING,
        )

        errors_found = []
        warnings_found = []

        for line in log_content.splitlines():
            if any(level in line.lower() for level in ["error", "exception", "critical", "fatal"]):
                errors_found.append(line[:200])
            elif any(level in line.lower() for level in ["warning", "warn"]):
                warnings_found.append(line[:200])

        return {
            "analysis": response.content,
            "errors_count": len(errors_found),
            "warnings_count": len(warnings_found),
            "sample_errors": errors_found[:5],
            "sample_warnings": warnings_found[:5],
        }

    async def diagnose_issue(
        self,
        description: str,
        symptoms: List[str],
        affected_files: Optional[List[str]] = None,
    ) -> BugReport:
        import uuid
        bug_id = str(uuid.uuid4())[:8]

        context = ""
        if affected_files:
            for file_path in affected_files[:3]:
                if Path(file_path).exists():
                    with open(file_path, "r") as f:
                        content = f.read()[:1000]
                    context += f"\n\nFile: {file_path}\n```\n{content}\n```"

        prompt = f"""Diagnose this software issue:

Description: {description}

Symptoms:
{chr(10).join(f"- {s}" for s in symptoms)}

{f"Affected code:{context}" if context else ""}

Provide:
1. Likely root causes (ranked by probability)
2. Diagnostic steps to confirm
3. Potential fixes
4. Severity assessment (critical/high/medium/low)

Diagnosis:"""

        response = await brain.think(
            prompt=prompt,
            agent_type="debugger",
            task_type=ModelType.REASONING,
        )

        severity = "medium"
        if any(word in response.content.lower() for word in ["critical", "severe", "crash", "data loss"]):
            severity = "critical"
        elif any(word in response.content.lower() for word in ["high", "important", "breaking"]):
            severity = "high"
        elif any(word in response.content.lower() for word in ["minor", "cosmetic", "low"]):
            severity = "low"

        bug_report = BugReport(
            id=bug_id,
            title=description[:100],
            description=description,
            error_info=None,
            severity=severity,
            status="open",
            root_cause=response.content[:500] if not response.error else "Analysis failed",
            suggested_fixes=[],
            related_files=affected_files or [],
        )

        self.bug_history.append(bug_report)
        return bug_report

    async def verify_fix(
        self,
        original_error: str,
        fix_applied: str,
        test_result: Optional[str] = None,
    ) -> Dict:
        prompt = f"""Verify if this fix properly addresses the error:

Original Error:
{original_error[:1000]}

Fix Applied:
{fix_applied[:1000]}

{f"Test Result: {test_result}" if test_result else ""}

Evaluate:
1. Does the fix address the root cause?
2. Are there any remaining issues?
3. Could this introduce new problems?
4. Is the fix complete?

Verification:"""

        response = await brain.think(
            prompt=prompt,
            agent_type="debugger",
            task_type=ModelType.REASONING,
        )

        is_complete = not any(word in response.content.lower() for word in [
            "incomplete", "partial", "remaining", "still", "doesn't", "won't"
        ])

        has_side_effects = any(word in response.content.lower() for word in [
            "side effect", "might break", "could cause", "potential issue"
        ])

        return {
            "is_fix_complete": is_complete,
            "has_side_effects": has_side_effects,
            "analysis": response.content,
            "recommendation": "Apply fix" if is_complete and not has_side_effects else "Review needed",
        }

    def get_common_errors(self, language: str = "python") -> List[Dict]:
        common = {
            "python": [
                {"error": "IndentationError", "cause": "Mixed tabs/spaces or incorrect indentation", "fix": "Use consistent 4-space indentation"},
                {"error": "ImportError", "cause": "Module not installed or wrong path", "fix": "pip install module or check PYTHONPATH"},
                {"error": "AttributeError", "cause": "Accessing non-existent attribute", "fix": "Check object type and available attributes"},
                {"error": "TypeError", "cause": "Wrong type in operation", "fix": "Verify types match expected"},
                {"error": "KeyError", "cause": "Dictionary key doesn't exist", "fix": "Use .get() or check key existence"},
            ],
            "javascript": [
                {"error": "TypeError", "cause": "Undefined is not a function/object", "fix": "Check variable initialization"},
                {"error": "ReferenceError", "cause": "Variable not defined", "fix": "Declare variable before use"},
                {"error": "SyntaxError", "cause": "Invalid syntax", "fix": "Check brackets, quotes, semicolons"},
                {"error": "RangeError", "cause": "Value out of range", "fix": "Validate input ranges"},
            ],
        }
        return common.get(language, common["python"])

    def get_stats(self) -> Dict:
        return {
            "total_bugs_analyzed": len(self.bug_history),
            "fix_success_rates": self.fix_success_rate,
            "by_severity": {
                "critical": len([b for b in self.bug_history if b.severity == "critical"]),
                "high": len([b for b in self.bug_history if b.severity == "high"]),
                "medium": len([b for b in self.bug_history if b.severity == "medium"]),
                "low": len([b for b in self.bug_history if b.severity == "low"]),
            },
        }


debugger_service = DebuggerService()


if __name__ == "__main__":
    async def test_debugger():
        print("Testing Debugger Service...")

        test_error = """Traceback (most recent call last):
  File "test.py", line 10, in <module>
    result = process_data(data)
  File "test.py", line 5, in process_data
    return data['key']
KeyError: 'key'"""

        print("\nAnalyzing error...")
        analysis = await debugger_service.analyze_error(test_error)
        print(f"Error type: {analysis['error_info']['type']}")
        print(f"Analysis preview: {analysis['analysis'][:300]}...")

        print("\nCommon Python errors:")
        for error in debugger_service.get_common_errors()[:3]:
            print(f"  - {error['error']}: {error['cause']}")

    asyncio.run(test_debugger())
