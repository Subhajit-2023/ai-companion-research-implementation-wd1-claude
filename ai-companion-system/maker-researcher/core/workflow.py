"""
Workflow Manager - Human-in-the-Loop system for the Maker-Researcher
"""
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path
import difflib
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import settings


class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    AUTO_APPROVED = "auto_approved"


class ChangeType(Enum):
    FILE_CREATE = "file_create"
    FILE_MODIFY = "file_modify"
    FILE_DELETE = "file_delete"
    CODE_EXECUTE = "code_execute"
    CONFIG_CHANGE = "config_change"
    SYSTEM_COMMAND = "system_command"
    SAFE_READ = "safe_read"
    SAFE_SEARCH = "safe_search"


class RiskLevel(Enum):
    SAFE = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    CRITICAL = 5


@dataclass
class ProposedChange:
    id: str
    change_type: ChangeType
    title: str
    description: str
    risk_level: RiskLevel
    file_path: Optional[str] = None
    original_content: Optional[str] = None
    new_content: Optional[str] = None
    diff: Optional[str] = None
    command: Optional[str] = None
    rationale: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "change_type": self.change_type.value,
            "title": self.title,
            "description": self.description,
            "risk_level": self.risk_level.value,
            "file_path": self.file_path,
            "diff": self.diff,
            "command": self.command,
            "rationale": self.rationale,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class ApprovalRequest:
    id: str
    task_id: str
    changes: List[ProposedChange]
    status: ApprovalStatus = ApprovalStatus.PENDING
    summary: str = ""
    impact_analysis: str = ""
    rollback_plan: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    reviewed_at: Optional[datetime] = None
    reviewer_notes: str = ""
    auto_approve_eligible: bool = False

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "task_id": self.task_id,
            "changes": [c.to_dict() for c in self.changes],
            "status": self.status.value,
            "summary": self.summary,
            "impact_analysis": self.impact_analysis,
            "rollback_plan": self.rollback_plan,
            "created_at": self.created_at.isoformat(),
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "reviewer_notes": self.reviewer_notes,
            "auto_approve_eligible": self.auto_approve_eligible,
        }


class WorkflowManager:
    def __init__(self):
        self.approval_requests: Dict[str, ApprovalRequest] = {}
        self.change_history: List[Dict] = []
        self.feedback_log: List[Dict] = []
        self.approval_callbacks: List[Callable] = []
        self.data_dir = Path(settings.DATA_DIR) / "workflow"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._load_history()

        self.risk_rules = {
            ChangeType.FILE_DELETE: RiskLevel.HIGH,
            ChangeType.FILE_CREATE: RiskLevel.LOW,
            ChangeType.FILE_MODIFY: RiskLevel.MEDIUM,
            ChangeType.CODE_EXECUTE: RiskLevel.HIGH,
            ChangeType.CONFIG_CHANGE: RiskLevel.MEDIUM,
            ChangeType.SYSTEM_COMMAND: RiskLevel.CRITICAL,
            ChangeType.SAFE_READ: RiskLevel.SAFE,
            ChangeType.SAFE_SEARCH: RiskLevel.SAFE,
        }

        self.critical_paths = [
            "config.py",
            ".env",
            "database",
            "auth",
            "security",
            "main.py",
            "__init__.py",
        ]

    def _load_history(self):
        history_file = self.data_dir / "history.json"
        if history_file.exists():
            try:
                with open(history_file, "r") as f:
                    data = json.load(f)
                    self.change_history = data.get("changes", [])
                    self.feedback_log = data.get("feedback", [])
            except Exception as e:
                print(f"Error loading workflow history: {e}")

    def _save_history(self):
        history_file = self.data_dir / "history.json"
        try:
            data = {
                "changes": self.change_history[-1000:],
                "feedback": self.feedback_log[-500:],
                "updated_at": datetime.utcnow().isoformat(),
            }
            with open(history_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving workflow history: {e}")

    def assess_risk(
        self,
        change_type: ChangeType,
        file_path: Optional[str] = None,
        content_diff_size: int = 0,
    ) -> RiskLevel:
        base_risk = self.risk_rules.get(change_type, RiskLevel.MEDIUM)

        if file_path:
            for critical in self.critical_paths:
                if critical in file_path.lower():
                    if base_risk.value < RiskLevel.HIGH.value:
                        base_risk = RiskLevel.HIGH
                    break

        if content_diff_size > 500:
            if base_risk.value < RiskLevel.HIGH.value:
                base_risk = RiskLevel(min(base_risk.value + 1, 5))

        return base_risk

    def create_diff(self, original: str, modified: str) -> str:
        if not original:
            original = ""
        if not modified:
            modified = ""

        diff = difflib.unified_diff(
            original.splitlines(keepends=True),
            modified.splitlines(keepends=True),
            fromfile="original",
            tofile="modified",
            lineterm="",
        )
        return "".join(diff)

    def propose_change(
        self,
        task_id: str,
        change_type: ChangeType,
        title: str,
        description: str,
        file_path: Optional[str] = None,
        original_content: Optional[str] = None,
        new_content: Optional[str] = None,
        command: Optional[str] = None,
        rationale: str = "",
    ) -> ProposedChange:
        change_id = str(uuid.uuid4())[:8]

        diff = None
        diff_size = 0
        if original_content is not None and new_content is not None:
            diff = self.create_diff(original_content, new_content)
            diff_size = len(diff)

        risk_level = self.assess_risk(change_type, file_path, diff_size)

        change = ProposedChange(
            id=change_id,
            change_type=change_type,
            title=title,
            description=description,
            risk_level=risk_level,
            file_path=file_path,
            original_content=original_content,
            new_content=new_content,
            diff=diff,
            command=command,
            rationale=rationale,
        )

        return change

    def create_approval_request(
        self,
        task_id: str,
        changes: List[ProposedChange],
        summary: str = "",
        impact_analysis: str = "",
    ) -> ApprovalRequest:
        request_id = str(uuid.uuid4())[:8]

        max_risk = max(c.risk_level.value for c in changes) if changes else 1
        auto_eligible = max_risk <= RiskLevel.LOW.value and settings.AUTO_APPROVE_SAFE_OPS

        rollback_plan = self._generate_rollback_plan(changes)

        request = ApprovalRequest(
            id=request_id,
            task_id=task_id,
            changes=changes,
            summary=summary or f"Approval request with {len(changes)} change(s)",
            impact_analysis=impact_analysis,
            rollback_plan=rollback_plan,
            auto_approve_eligible=auto_eligible,
        )

        self.approval_requests[request_id] = request

        if auto_eligible:
            self.auto_approve(request_id)

        self._save_history()
        return request

    def _generate_rollback_plan(self, changes: List[ProposedChange]) -> str:
        rollback_steps = []
        for i, change in enumerate(changes, 1):
            if change.change_type == ChangeType.FILE_CREATE:
                rollback_steps.append(f"{i}. Delete created file: {change.file_path}")
            elif change.change_type == ChangeType.FILE_MODIFY:
                rollback_steps.append(f"{i}. Restore original content of: {change.file_path}")
            elif change.change_type == ChangeType.FILE_DELETE:
                rollback_steps.append(f"{i}. Restore deleted file: {change.file_path}")
            elif change.change_type == ChangeType.CONFIG_CHANGE:
                rollback_steps.append(f"{i}. Revert config change: {change.title}")

        if not rollback_steps:
            return "No rollback actions needed."

        return "\n".join(rollback_steps)

    def approve(self, request_id: str, notes: str = "") -> bool:
        request = self.approval_requests.get(request_id)
        if not request or request.status != ApprovalStatus.PENDING:
            return False

        request.status = ApprovalStatus.APPROVED
        request.reviewed_at = datetime.utcnow()
        request.reviewer_notes = notes

        self._record_change(request, "approved")
        self._save_history()

        for callback in self.approval_callbacks:
            try:
                callback(request, ApprovalStatus.APPROVED)
            except Exception as e:
                print(f"Callback error: {e}")

        return True

    def reject(self, request_id: str, notes: str = "") -> bool:
        request = self.approval_requests.get(request_id)
        if not request or request.status != ApprovalStatus.PENDING:
            return False

        request.status = ApprovalStatus.REJECTED
        request.reviewed_at = datetime.utcnow()
        request.reviewer_notes = notes

        self._record_feedback(request, "rejected", notes)
        self._save_history()

        for callback in self.approval_callbacks:
            try:
                callback(request, ApprovalStatus.REJECTED)
            except Exception as e:
                print(f"Callback error: {e}")

        return True

    def auto_approve(self, request_id: str) -> bool:
        request = self.approval_requests.get(request_id)
        if not request or not request.auto_approve_eligible:
            return False

        request.status = ApprovalStatus.AUTO_APPROVED
        request.reviewed_at = datetime.utcnow()
        request.reviewer_notes = "Auto-approved (safe operation)"

        self._record_change(request, "auto_approved")
        self._save_history()
        return True

    def _record_change(self, request: ApprovalRequest, action: str):
        record = {
            "request_id": request.id,
            "task_id": request.task_id,
            "action": action,
            "changes_count": len(request.changes),
            "timestamp": datetime.utcnow().isoformat(),
            "summary": request.summary,
        }
        self.change_history.append(record)

    def _record_feedback(self, request: ApprovalRequest, action: str, notes: str):
        record = {
            "request_id": request.id,
            "action": action,
            "notes": notes,
            "changes": [c.to_dict() for c in request.changes],
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.feedback_log.append(record)

    def get_pending_requests(self) -> List[ApprovalRequest]:
        return [
            r for r in self.approval_requests.values()
            if r.status == ApprovalStatus.PENDING
        ]

    def get_request(self, request_id: str) -> Optional[ApprovalRequest]:
        return self.approval_requests.get(request_id)

    def get_request_by_task(self, task_id: str) -> List[ApprovalRequest]:
        return [
            r for r in self.approval_requests.values()
            if r.task_id == task_id
        ]

    def register_callback(self, callback: Callable):
        self.approval_callbacks.append(callback)

    def is_safe_operation(self, change_type: ChangeType) -> bool:
        return change_type in [ChangeType.SAFE_READ, ChangeType.SAFE_SEARCH]

    def requires_approval(self, change_type: ChangeType, file_path: Optional[str] = None) -> bool:
        if self.is_safe_operation(change_type):
            return False

        risk = self.assess_risk(change_type, file_path)
        return risk.value >= RiskLevel.MEDIUM.value

    def format_change_preview(self, change: ProposedChange) -> str:
        preview = f"""
{'='*60}
PROPOSED CHANGE: {change.title}
{'='*60}
Type: {change.change_type.value}
Risk Level: {change.risk_level.name} ({change.risk_level.value}/5)
File: {change.file_path or 'N/A'}

Description:
{change.description}

Rationale:
{change.rationale or 'Not provided'}
"""
        if change.diff:
            preview += f"""
Diff:
{'-'*40}
{change.diff[:2000]}{'...(truncated)' if len(change.diff) > 2000 else ''}
{'-'*40}
"""
        if change.command:
            preview += f"""
Command to execute:
{change.command}
"""
        return preview

    def format_approval_request(self, request: ApprovalRequest) -> str:
        output = f"""
{'#'*60}
APPROVAL REQUEST: {request.id}
{'#'*60}
Task: {request.task_id}
Status: {request.status.value}
Created: {request.created_at.isoformat()}
Auto-approve eligible: {request.auto_approve_eligible}

SUMMARY:
{request.summary}

IMPACT ANALYSIS:
{request.impact_analysis or 'Not provided'}

ROLLBACK PLAN:
{request.rollback_plan}

CHANGES ({len(request.changes)}):
"""
        for change in request.changes:
            output += self.format_change_preview(change)

        output += f"""
{'#'*60}
To approve: approve {request.id}
To reject: reject {request.id} [reason]
{'#'*60}
"""
        return output

    def get_stats(self) -> Dict:
        status_counts = {}
        for request in self.approval_requests.values():
            status = request.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            "total_requests": len(self.approval_requests),
            "pending_count": len(self.get_pending_requests()),
            "by_status": status_counts,
            "total_changes_recorded": len(self.change_history),
            "total_feedback_recorded": len(self.feedback_log),
        }


workflow_manager = WorkflowManager()


if __name__ == "__main__":
    print("Testing Workflow Manager...")

    change = workflow_manager.propose_change(
        task_id="test-123",
        change_type=ChangeType.FILE_MODIFY,
        title="Update config setting",
        description="Change LLM temperature from 0.7 to 0.8",
        file_path="config.py",
        original_content="LLM_TEMPERATURE = 0.7",
        new_content="LLM_TEMPERATURE = 0.8",
        rationale="Improve creativity in responses",
    )

    print(f"Created change: {change.id}")
    print(f"Risk level: {change.risk_level.name}")

    request = workflow_manager.create_approval_request(
        task_id="test-123",
        changes=[change],
        summary="Update LLM temperature setting",
    )

    print(f"\nApproval request: {request.id}")
    print(workflow_manager.format_approval_request(request))

    print(f"\nStats: {workflow_manager.get_stats()}")
