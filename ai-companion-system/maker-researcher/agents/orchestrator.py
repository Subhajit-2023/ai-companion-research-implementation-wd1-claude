"""
Orchestrator - Central coordinator for all agents and tasks
"""
import asyncio
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json
import re
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import settings, TASK_CATEGORIES
from core.brain import brain, ModelType, BrainResponse
from core.task_queue import task_queue, Task, TaskCategory, TaskPriority, TaskResult, TaskStatus
from core.workflow import workflow_manager, ApprovalStatus
from services.research import research_service
from services.document_processor import document_processor
from services.code_service import code_service
from services.debugger import debugger_service
from services.monitor import monitor_service
from services.optimizer import optimizer_service


@dataclass
class AgentAction:
    agent: str
    action: str
    params: Dict
    result: Optional[Any] = None
    status: str = "pending"
    error: Optional[str] = None


@dataclass
class ConversationContext:
    messages: List[Dict] = field(default_factory=list)
    current_task: Optional[Task] = None
    actions_taken: List[AgentAction] = field(default_factory=list)
    session_id: str = ""


class Orchestrator:
    def __init__(self):
        self.context = ConversationContext()
        self.running = False
        self._register_task_handlers()

        self.agent_capabilities = {
            "researcher": ["search", "find", "look up", "research", "papers", "information"],
            "coder": ["create", "implement", "write", "generate", "code", "build"],
            "debugger": ["fix", "debug", "error", "bug", "issue", "crash"],
            "optimizer": ["optimize", "improve", "faster", "efficient", "performance"],
            "advisor": ["explain", "help", "how to", "guide", "recommend"],
        }

    def _register_task_handlers(self):
        task_queue.register_handler(TaskCategory.RESEARCH, self._handle_research_task)
        task_queue.register_handler(TaskCategory.CODE, self._handle_code_task)
        task_queue.register_handler(TaskCategory.DEBUG, self._handle_debug_task)
        task_queue.register_handler(TaskCategory.OPTIMIZE, self._handle_optimize_task)
        task_queue.register_handler(TaskCategory.ADVISE, self._handle_advise_task)
        task_queue.register_handler(TaskCategory.SYSTEM, self._handle_system_task)

    def _classify_intent(self, message: str) -> str:
        message_lower = message.lower()

        for category, keywords in TASK_CATEGORIES.items():
            if any(kw in message_lower for kw in keywords):
                return category

        return "advise"

    def _select_agent(self, intent: str) -> str:
        agent_map = {
            "research": "researcher",
            "code": "coder",
            "debug": "debugger",
            "optimize": "optimizer",
            "advise": "advisor",
        }
        return agent_map.get(intent, "advisor")

    async def process_message(self, message: str) -> Dict:
        self.context.messages.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.utcnow().isoformat(),
        })

        intent = self._classify_intent(message)
        agent = self._select_agent(intent)

        planning_response = await brain.reason_step_by_step(
            problem=f"User request: {message}\nIntent: {intent}\nAgent: {agent}",
            agent_type="orchestrator",
        )

        actions = self._extract_actions(planning_response.content, intent)

        results = []
        for action in actions:
            action_result = await self._execute_action(action)
            results.append(action_result)

        response = await self._synthesize_response(message, results, agent)

        self.context.messages.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.utcnow().isoformat(),
        })

        return {
            "response": response,
            "intent": intent,
            "agent": agent,
            "actions": [
                {"action": a.action, "status": a.status, "result": str(a.result)[:200] if a.result else None}
                for a in actions
            ],
        }

    def _extract_actions(self, plan: str, intent: str) -> List[AgentAction]:
        actions = []

        if intent == "research":
            actions.append(AgentAction(
                agent="researcher",
                action="search",
                params={"query": plan[:200]},
            ))

        elif intent == "code":
            actions.append(AgentAction(
                agent="coder",
                action="generate",
                params={"description": plan[:500]},
            ))

        elif intent == "debug":
            actions.append(AgentAction(
                agent="debugger",
                action="analyze",
                params={"error": plan[:500]},
            ))

        elif intent == "optimize":
            actions.append(AgentAction(
                agent="optimizer",
                action="analyze",
                params={"area": "general"},
            ))

        else:
            actions.append(AgentAction(
                agent="advisor",
                action="advise",
                params={"question": plan[:500]},
            ))

        return actions

    async def _execute_action(self, action: AgentAction) -> AgentAction:
        action.status = "running"

        try:
            if action.agent == "researcher":
                if action.action == "search":
                    result = await research_service.comprehensive_research(
                        action.params.get("query", ""),
                        include_papers=True,
                        include_code=True,
                    )
                    action.result = research_service.format_research_for_llm(result)

            elif action.agent == "coder":
                if action.action == "generate":
                    result = await code_service.generate_code(
                        description=action.params.get("description", ""),
                        language=action.params.get("language", "python"),
                    )
                    action.result = result.modified if result else "Code generation failed"

                elif action.action == "analyze":
                    result = await code_service.analyze_file(action.params.get("file", ""))
                    action.result = result

            elif action.agent == "debugger":
                if action.action == "analyze":
                    result = await debugger_service.analyze_error(
                        action.params.get("error", ""),
                        action.params.get("language", "python"),
                    )
                    action.result = result

            elif action.agent == "optimizer":
                if action.action == "analyze":
                    metrics = monitor_service.collect_system_metrics()
                    result = await optimizer_service.analyze_performance({
                        "avg_response_time": 0,
                        "memory_percent": metrics.memory_percent,
                        "gpu_percent": metrics.gpu_percent,
                    })
                    action.result = result

            elif action.agent == "advisor":
                response = await brain.think(
                    prompt=action.params.get("question", ""),
                    agent_type="advisor",
                )
                action.result = response.content

            action.status = "completed"

        except Exception as e:
            action.status = "failed"
            action.error = str(e)

        self.context.actions_taken.append(action)
        return action

    async def _synthesize_response(
        self,
        original_message: str,
        results: List[AgentAction],
        agent: str,
    ) -> str:
        context_parts = []
        for action in results:
            if action.result:
                result_str = str(action.result)
                if len(result_str) > 2000:
                    result_str = result_str[:2000] + "..."
                context_parts.append(f"[{action.agent}:{action.action}] {result_str}")

        context = "\n\n".join(context_parts)

        prompt = f"""Based on the following information, provide a helpful response to the user.

User's request: {original_message}

Information gathered:
{context}

Provide a clear, actionable response that directly addresses the user's needs.
If code is involved, format it properly.
If there are next steps, list them clearly.

Response:"""

        response = await brain.think(
            prompt=prompt,
            agent_type=agent,
        )

        return response.content if not response.error else "I encountered an issue processing your request. Please try again."

    async def create_and_queue_task(
        self,
        title: str,
        description: str,
        category: str,
        priority: str = "normal",
        require_approval: bool = False,
    ) -> Task:
        cat_map = {
            "research": TaskCategory.RESEARCH,
            "code": TaskCategory.CODE,
            "debug": TaskCategory.DEBUG,
            "optimize": TaskCategory.OPTIMIZE,
            "advise": TaskCategory.ADVISE,
            "system": TaskCategory.SYSTEM,
        }

        pri_map = {
            "low": TaskPriority.LOW,
            "normal": TaskPriority.NORMAL,
            "high": TaskPriority.HIGH,
            "urgent": TaskPriority.URGENT,
        }

        task = task_queue.create_task(
            title=title,
            description=description,
            category=cat_map.get(category, TaskCategory.ADVISE),
            priority=pri_map.get(priority, TaskPriority.NORMAL),
            requires_approval=require_approval,
        )

        await task_queue.enqueue(task)
        return task

    async def _handle_research_task(self, task: Task) -> TaskResult:
        query = task.input_data.get("query", task.description)

        session = await research_service.comprehensive_research(
            query,
            include_papers=True,
            include_code=True,
        )

        summary = research_service.format_research_for_llm(session)

        return TaskResult(
            success=True,
            data=summary,
            artifacts=[f"research_session_{session.id}"],
        )

    async def _handle_code_task(self, task: Task) -> TaskResult:
        description = task.input_data.get("description", task.description)
        language = task.input_data.get("language", "python")
        file_path = task.input_data.get("file_path")

        if file_path:
            change = await code_service.modify_code(file_path, description)
        else:
            change = await code_service.generate_code(description, language)

        if not change:
            return TaskResult(success=False, error="Code generation failed")

        if task.requires_approval:
            from core.workflow import ChangeType
            proposed = workflow_manager.propose_change(
                task_id=task.id,
                change_type=ChangeType.FILE_MODIFY if file_path else ChangeType.FILE_CREATE,
                title=f"Code: {description[:50]}",
                description=description,
                file_path=change.file_path,
                original_content=change.original,
                new_content=change.modified,
            )

            request = workflow_manager.create_approval_request(
                task_id=task.id,
                changes=[proposed],
            )

            return TaskResult(
                success=True,
                data={
                    "code": change.modified,
                    "approval_request_id": request.id,
                    "status": request.status.value,
                },
            )

        return TaskResult(success=True, data={"code": change.modified})

    async def _handle_debug_task(self, task: Task) -> TaskResult:
        error_text = task.input_data.get("error", task.description)
        language = task.input_data.get("language", "python")

        analysis = await debugger_service.analyze_error(error_text, language)

        error_info = debugger_service.parse_error(error_text, language)
        fixes = await debugger_service.suggest_fix(error_info)

        return TaskResult(
            success=True,
            data={
                "analysis": analysis,
                "suggested_fixes": [
                    {"description": f.description, "confidence": f.confidence}
                    for f in fixes
                ],
            },
        )

    async def _handle_optimize_task(self, task: Task) -> TaskResult:
        area = task.input_data.get("area", "general")

        metrics = monitor_service.collect_system_metrics()
        current = {
            "avg_response_time": 0,
            "memory_percent": metrics.memory_percent,
            "gpu_percent": metrics.gpu_percent,
            "gpu_memory_used_gb": metrics.gpu_memory_used_gb,
        }

        profile = await optimizer_service.analyze_performance(current, area)
        suggestions = await optimizer_service.suggest_optimizations(current)

        return TaskResult(
            success=True,
            data={
                "profile": {
                    "bottlenecks": profile.bottlenecks,
                    "recommendations": profile.recommendations,
                },
                "suggestions": [
                    {"title": s.title, "priority": s.priority, "effort": s.implementation_effort}
                    for s in suggestions
                ],
            },
        )

    async def _handle_advise_task(self, task: Task) -> TaskResult:
        question = task.input_data.get("question", task.description)

        response = await brain.think(
            prompt=question,
            agent_type="advisor",
        )

        return TaskResult(
            success=not response.error,
            data=response.content if not response.error else None,
            error=response.error,
        )

    async def _handle_system_task(self, task: Task) -> TaskResult:
        action = task.input_data.get("action", "status")

        if action == "status":
            return TaskResult(
                success=True,
                data=monitor_service.get_full_report(),
            )

        elif action == "health":
            return TaskResult(
                success=True,
                data=monitor_service.get_health_status(),
            )

        return TaskResult(success=False, error=f"Unknown system action: {action}")

    async def run_task_processor(self):
        self.running = True
        await monitor_service.start_monitoring()

        while self.running:
            try:
                task = await task_queue.dequeue()
                if task:
                    await task_queue.execute_task(task)
                else:
                    await asyncio.sleep(1)
            except Exception as e:
                print(f"Task processor error: {e}")
                await asyncio.sleep(5)

    def stop(self):
        self.running = False

    def get_status(self) -> Dict:
        return {
            "running": self.running,
            "context_messages": len(self.context.messages),
            "actions_taken": len(self.context.actions_taken),
            "task_queue": task_queue.get_stats(),
            "pending_approvals": len(workflow_manager.get_pending_requests()),
            "brain_status": brain.get_status(),
        }

    def clear_context(self):
        self.context = ConversationContext()


orchestrator = Orchestrator()


if __name__ == "__main__":
    async def test_orchestrator():
        print("Testing Orchestrator...")

        print("\n1. Processing a research request...")
        result = await orchestrator.process_message(
            "Research the best practices for optimizing LLM inference on RTX 4060"
        )
        print(f"Intent: {result['intent']}")
        print(f"Agent: {result['agent']}")
        print(f"Response preview: {result['response'][:300]}...")

        print("\n2. Getting status...")
        status = orchestrator.get_status()
        print(f"Status: {json.dumps(status, indent=2, default=str)}")

    asyncio.run(test_orchestrator())
