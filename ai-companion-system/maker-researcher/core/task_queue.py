"""
Task Queue - Manages async tasks for the Maker-Researcher system
"""
import uuid
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import settings


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


class TaskCategory(Enum):
    RESEARCH = "research"
    CODE = "code"
    DEBUG = "debug"
    OPTIMIZE = "optimize"
    ADVISE = "advise"
    SYSTEM = "system"


@dataclass
class TaskResult:
    success: bool
    data: Any = None
    error: Optional[str] = None
    artifacts: List[str] = field(default_factory=list)
    metrics: Dict = field(default_factory=dict)


@dataclass
class Task:
    id: str
    title: str
    description: str
    category: TaskCategory
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.NORMAL
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    parent_task_id: Optional[str] = None
    subtasks: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    input_data: Dict = field(default_factory=dict)
    result: Optional[TaskResult] = None
    requires_approval: bool = False
    approval_reason: str = ""
    assigned_agent: str = "orchestrator"
    retry_count: int = 0
    max_retries: int = 3
    timeout: int = 600
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category.value,
            "status": self.status.value,
            "priority": self.priority.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "parent_task_id": self.parent_task_id,
            "subtasks": self.subtasks,
            "dependencies": self.dependencies,
            "input_data": self.input_data,
            "result": {
                "success": self.result.success,
                "data": str(self.result.data)[:1000] if self.result else None,
                "error": self.result.error if self.result else None,
            } if self.result else None,
            "requires_approval": self.requires_approval,
            "approval_reason": self.approval_reason,
            "assigned_agent": self.assigned_agent,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Task":
        task = cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            category=TaskCategory(data["category"]),
            status=TaskStatus(data["status"]),
            priority=TaskPriority(data["priority"]),
            parent_task_id=data.get("parent_task_id"),
            subtasks=data.get("subtasks", []),
            dependencies=data.get("dependencies", []),
            input_data=data.get("input_data", {}),
            requires_approval=data.get("requires_approval", False),
            approval_reason=data.get("approval_reason", ""),
            assigned_agent=data.get("assigned_agent", "orchestrator"),
            metadata=data.get("metadata", {}),
        )
        if data.get("created_at"):
            task.created_at = datetime.fromisoformat(data["created_at"])
        return task


class TaskQueue:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self.running_tasks: Dict[str, Task] = {}
        self.completed_tasks: List[str] = []
        self.max_concurrent = settings.MAX_CONCURRENT_TASKS
        self.task_handlers: Dict[TaskCategory, Callable] = {}
        self.data_dir = Path(settings.DATA_DIR) / "tasks"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._load_persisted_tasks()

    def _load_persisted_tasks(self):
        task_file = self.data_dir / "tasks.json"
        if task_file.exists():
            try:
                with open(task_file, "r") as f:
                    data = json.load(f)
                    for task_data in data.get("tasks", []):
                        task = Task.from_dict(task_data)
                        self.tasks[task.id] = task
                        if task.status == TaskStatus.COMPLETED:
                            self.completed_tasks.append(task.id)
            except Exception as e:
                print(f"Error loading tasks: {e}")

    def _persist_tasks(self):
        task_file = self.data_dir / "tasks.json"
        try:
            data = {
                "tasks": [t.to_dict() for t in self.tasks.values()],
                "updated_at": datetime.utcnow().isoformat(),
            }
            with open(task_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error persisting tasks: {e}")

    def create_task(
        self,
        title: str,
        description: str,
        category: TaskCategory,
        priority: TaskPriority = TaskPriority.NORMAL,
        input_data: Optional[Dict] = None,
        requires_approval: bool = False,
        approval_reason: str = "",
        parent_task_id: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
        assigned_agent: str = "orchestrator",
    ) -> Task:
        task_id = str(uuid.uuid4())[:8]

        task = Task(
            id=task_id,
            title=title,
            description=description,
            category=category,
            priority=priority,
            input_data=input_data or {},
            requires_approval=requires_approval,
            approval_reason=approval_reason,
            parent_task_id=parent_task_id,
            dependencies=dependencies or [],
            assigned_agent=assigned_agent,
        )

        self.tasks[task_id] = task

        if parent_task_id and parent_task_id in self.tasks:
            self.tasks[parent_task_id].subtasks.append(task_id)

        self._persist_tasks()
        return task

    async def enqueue(self, task: Task):
        priority_value = -task.priority.value
        await self.queue.put((priority_value, task.created_at.timestamp(), task.id))
        task.status = TaskStatus.PENDING
        self._persist_tasks()

    async def dequeue(self) -> Optional[Task]:
        if self.queue.empty():
            return None

        _, _, task_id = await self.queue.get()
        task = self.tasks.get(task_id)

        if task and self._can_execute(task):
            return task

        return None

    def _can_execute(self, task: Task) -> bool:
        if len(self.running_tasks) >= self.max_concurrent:
            return False

        for dep_id in task.dependencies:
            dep_task = self.tasks.get(dep_id)
            if dep_task and dep_task.status != TaskStatus.COMPLETED:
                return False

        if task.requires_approval and task.status != TaskStatus.APPROVED:
            return False

        return True

    def register_handler(self, category: TaskCategory, handler: Callable):
        self.task_handlers[category] = handler

    async def execute_task(self, task: Task) -> TaskResult:
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.utcnow()
        self.running_tasks[task.id] = task
        self._persist_tasks()

        try:
            handler = self.task_handlers.get(task.category)
            if not handler:
                raise ValueError(f"No handler for category: {task.category}")

            result = await asyncio.wait_for(
                handler(task),
                timeout=task.timeout
            )

            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            self.completed_tasks.append(task.id)

        except asyncio.TimeoutError:
            task.result = TaskResult(success=False, error="Task timed out")
            task.status = TaskStatus.FAILED

        except Exception as e:
            task.result = TaskResult(success=False, error=str(e))

            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.PENDING
                await self.enqueue(task)
            else:
                task.status = TaskStatus.FAILED

        finally:
            if task.id in self.running_tasks:
                del self.running_tasks[task.id]
            self._persist_tasks()

        return task.result

    def request_approval(self, task: Task, reason: str):
        task.status = TaskStatus.AWAITING_APPROVAL
        task.requires_approval = True
        task.approval_reason = reason
        self._persist_tasks()

    def approve_task(self, task_id: str) -> bool:
        task = self.tasks.get(task_id)
        if task and task.status == TaskStatus.AWAITING_APPROVAL:
            task.status = TaskStatus.APPROVED
            self._persist_tasks()
            return True
        return False

    def reject_task(self, task_id: str, reason: str = "") -> bool:
        task = self.tasks.get(task_id)
        if task and task.status == TaskStatus.AWAITING_APPROVAL:
            task.status = TaskStatus.REJECTED
            task.metadata["rejection_reason"] = reason
            self._persist_tasks()
            return True
        return False

    def cancel_task(self, task_id: str) -> bool:
        task = self.tasks.get(task_id)
        if task and task.status in [TaskStatus.PENDING, TaskStatus.AWAITING_APPROVAL]:
            task.status = TaskStatus.CANCELLED
            self._persist_tasks()
            return True
        return False

    def get_task(self, task_id: str) -> Optional[Task]:
        return self.tasks.get(task_id)

    def get_pending_approvals(self) -> List[Task]:
        return [
            t for t in self.tasks.values()
            if t.status == TaskStatus.AWAITING_APPROVAL
        ]

    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        return [t for t in self.tasks.values() if t.status == status]

    def get_task_tree(self, task_id: str) -> Dict:
        task = self.tasks.get(task_id)
        if not task:
            return {}

        tree = task.to_dict()
        tree["subtask_details"] = [
            self.get_task_tree(st_id)
            for st_id in task.subtasks
        ]
        return tree

    def get_stats(self) -> Dict:
        status_counts = {}
        for status in TaskStatus:
            status_counts[status.value] = len(self.get_tasks_by_status(status))

        category_counts = {}
        for task in self.tasks.values():
            cat = task.category.value
            category_counts[cat] = category_counts.get(cat, 0) + 1

        return {
            "total_tasks": len(self.tasks),
            "running_tasks": len(self.running_tasks),
            "completed_tasks": len(self.completed_tasks),
            "by_status": status_counts,
            "by_category": category_counts,
            "queue_size": self.queue.qsize(),
        }

    def cleanup_old_tasks(self, days: int = 7):
        cutoff = datetime.utcnow()
        to_remove = []

        for task_id, task in self.tasks.items():
            if task.completed_at:
                age = (cutoff - task.completed_at).days
                if age > days and task.status in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]:
                    to_remove.append(task_id)

        for task_id in to_remove:
            del self.tasks[task_id]
            if task_id in self.completed_tasks:
                self.completed_tasks.remove(task_id)

        self._persist_tasks()
        return len(to_remove)


task_queue = TaskQueue()


if __name__ == "__main__":
    async def test_task_queue():
        print("Testing Task Queue...")

        task1 = task_queue.create_task(
            title="Research Python optimization",
            description="Find best practices for Python performance",
            category=TaskCategory.RESEARCH,
            priority=TaskPriority.HIGH,
        )
        print(f"Created task: {task1.id} - {task1.title}")

        task2 = task_queue.create_task(
            title="Implement caching",
            description="Add caching to improve performance",
            category=TaskCategory.CODE,
            requires_approval=True,
            approval_reason="Will modify core files",
        )
        print(f"Created task: {task2.id} - {task2.title}")

        print(f"\nStats: {task_queue.get_stats()}")

        pending = task_queue.get_pending_approvals()
        print(f"Pending approvals: {len(pending)}")

    asyncio.run(test_task_queue())
