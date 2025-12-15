"""
Maker-Researcher API - REST endpoints for the autonomous AI system
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import settings, ensure_directories
from agents.orchestrator import orchestrator
from core.task_queue import task_queue, TaskCategory, TaskPriority
from core.workflow import workflow_manager
from services.research import research_service
from services.document_processor import document_processor
from services.code_service import code_service
from services.debugger import debugger_service
from services.monitor import monitor_service
from services.optimizer import optimizer_service

ensure_directories()

app = FastAPI(
    title="AI Maker-Researcher",
    description="Autonomous AI system for research, development, and system improvement",
    version=settings.APP_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MessageRequest(BaseModel):
    message: str
    context: Optional[List[Dict]] = None


class ResearchRequest(BaseModel):
    query: str
    include_papers: bool = True
    include_code: bool = True
    include_news: bool = False


class CodeRequest(BaseModel):
    description: str
    language: str = "python"
    file_path: Optional[str] = None
    context: Optional[str] = None


class DebugRequest(BaseModel):
    error_text: str
    language: str = "python"
    additional_context: Optional[str] = None


class TaskRequest(BaseModel):
    title: str
    description: str
    category: str
    priority: str = "normal"
    require_approval: bool = False
    input_data: Optional[Dict] = None


class ApprovalRequest(BaseModel):
    request_id: str
    approve: bool
    notes: str = ""


class DocumentRequest(BaseModel):
    file_path: str


class SearchKnowledgeRequest(BaseModel):
    query: str
    n_results: int = 5
    document_ids: Optional[List[str]] = None


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


@app.get("/status")
async def get_status():
    return orchestrator.get_status()


@app.get("/health")
async def health_check():
    return monitor_service.get_health_status()


@app.post("/chat")
async def chat(request: MessageRequest):
    result = await orchestrator.process_message(request.message)
    return result


@app.post("/research")
async def research(request: ResearchRequest):
    session = await research_service.comprehensive_research(
        request.query,
        include_papers=request.include_papers,
        include_code=request.include_code,
        include_news=request.include_news,
    )

    return {
        "session_id": session.id,
        "query": session.query,
        "web_results": len(session.results),
        "papers": len(session.papers),
        "code_examples": len(session.code_examples),
        "formatted": research_service.format_research_for_llm(session),
    }


@app.get("/research/{session_id}")
async def get_research_session(session_id: str):
    session = research_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session.id,
        "query": session.query,
        "results": [{"title": r.title, "url": r.url, "snippet": r.snippet} for r in session.results],
        "papers": [{"title": p.title, "authors": p.authors, "year": p.year} for p in session.papers],
        "code_examples": [{"repo": c.repo_name, "url": c.url} for c in session.code_examples],
    }


@app.post("/code/generate")
async def generate_code(request: CodeRequest):
    result = await code_service.generate_code(
        description=request.description,
        language=request.language,
        context=request.context,
        file_path=request.file_path,
    )

    if not result:
        raise HTTPException(status_code=500, detail="Code generation failed")

    return {
        "code": result.modified,
        "file_path": result.file_path,
        "confidence": result.confidence,
    }


@app.post("/code/analyze")
async def analyze_code(file_path: str):
    analysis = await code_service.analyze_file(file_path)
    if not analysis:
        raise HTTPException(status_code=404, detail="File not found or unsupported")

    return {
        "file_path": analysis.file_path,
        "language": analysis.language,
        "loc": analysis.loc,
        "functions": analysis.functions,
        "classes": analysis.classes,
        "issues": analysis.issues,
        "complexity": analysis.complexity_score,
        "suggestions": analysis.suggestions,
    }


@app.get("/code/project")
async def analyze_project(project_path: Optional[str] = None):
    analysis = await code_service.analyze_project(project_path)
    return analysis


@app.post("/debug")
async def debug_error(request: DebugRequest):
    analysis = await debugger_service.analyze_error(
        request.error_text,
        request.language,
    )

    error_info = debugger_service.parse_error(request.error_text, request.language)
    fixes = await debugger_service.suggest_fix(error_info, request.additional_context)

    return {
        "error_info": analysis["error_info"],
        "analysis": analysis["analysis"],
        "suggested_fixes": [
            {
                "description": f.description,
                "code_change": f.code_change,
                "confidence": f.confidence,
                "risk_level": f.risk_level,
            }
            for f in fixes
        ],
    }


@app.post("/tasks")
async def create_task(request: TaskRequest, background_tasks: BackgroundTasks):
    task = await orchestrator.create_and_queue_task(
        title=request.title,
        description=request.description,
        category=request.category,
        priority=request.priority,
        require_approval=request.require_approval,
    )

    if request.input_data:
        task.input_data = request.input_data

    return {
        "task_id": task.id,
        "title": task.title,
        "status": task.status.value,
        "requires_approval": task.requires_approval,
    }


@app.get("/tasks")
async def list_tasks(status: Optional[str] = None):
    if status:
        from core.task_queue import TaskStatus
        try:
            task_status = TaskStatus(status)
            tasks = task_queue.get_tasks_by_status(task_status)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status")
    else:
        tasks = list(task_queue.tasks.values())

    return {
        "tasks": [t.to_dict() for t in tasks],
        "total": len(tasks),
    }


@app.get("/tasks/{task_id}")
async def get_task(task_id: str):
    task = task_queue.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task.to_dict()


@app.delete("/tasks/{task_id}")
async def cancel_task(task_id: str):
    success = task_queue.cancel_task(task_id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot cancel task")

    return {"success": True, "task_id": task_id}


@app.get("/approvals")
async def list_pending_approvals():
    pending = workflow_manager.get_pending_requests()
    return {
        "pending": [r.to_dict() for r in pending],
        "total": len(pending),
    }


@app.get("/approvals/{request_id}")
async def get_approval_request(request_id: str):
    request = workflow_manager.get_request(request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    return {
        "request": request.to_dict(),
        "preview": workflow_manager.format_approval_request(request),
    }


@app.post("/approvals/{request_id}")
async def process_approval(request_id: str, approval: ApprovalRequest):
    if approval.approve:
        success = workflow_manager.approve(request_id, approval.notes)
    else:
        success = workflow_manager.reject(request_id, approval.notes)

    if not success:
        raise HTTPException(status_code=400, detail="Cannot process approval")

    task_id = workflow_manager.get_request(request_id).task_id
    task = task_queue.get_task(task_id)
    if task and approval.approve:
        task_queue.approve_task(task_id)

    return {
        "success": True,
        "request_id": request_id,
        "action": "approved" if approval.approve else "rejected",
    }


@app.post("/documents")
async def process_document(request: DocumentRequest):
    doc = await document_processor.process_document(request.file_path)
    if not doc:
        raise HTTPException(status_code=400, detail="Failed to process document")

    return {
        "document_id": doc.id,
        "title": doc.title,
        "author": doc.author,
        "pages": doc.total_pages,
        "chunks": doc.total_chunks,
    }


@app.get("/documents")
async def list_documents():
    return {
        "documents": document_processor.list_documents(),
        "stats": document_processor.get_stats(),
    }


@app.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    success = document_processor.delete_document(doc_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")

    return {"success": True}


@app.post("/knowledge/search")
async def search_knowledge(request: SearchKnowledgeRequest):
    results = await document_processor.search(
        request.query,
        n_results=request.n_results,
        document_ids=request.document_ids,
    )

    return {
        "query": request.query,
        "results": results,
        "total": len(results),
    }


@app.get("/metrics")
async def get_metrics():
    return monitor_service.get_full_report()


@app.get("/metrics/system")
async def get_system_metrics():
    metrics = monitor_service.collect_system_metrics()
    return {
        "cpu_percent": metrics.cpu_percent,
        "memory_percent": metrics.memory_percent,
        "memory_used_gb": metrics.memory_used_gb,
        "gpu_percent": metrics.gpu_percent,
        "gpu_memory_used_gb": metrics.gpu_memory_used_gb,
        "disk_percent": metrics.disk_percent,
        "timestamp": metrics.timestamp.isoformat(),
    }


@app.get("/optimize")
async def get_optimizations():
    rtx_opts = await optimizer_service.generate_rtx4060_optimizations()
    return {
        "hardware_optimizations": rtx_opts,
        "improvement_stats": optimizer_service.get_improvement_stats(),
        "pending_suggestions": [
            {"id": s.id, "title": s.title, "priority": s.priority}
            for s in optimizer_service.get_pending_suggestions()
        ],
    }


@app.post("/optimize/analyze")
async def analyze_for_optimization(area: Optional[str] = None):
    metrics = monitor_service.collect_system_metrics()
    current = {
        "avg_response_time": 0,
        "memory_percent": metrics.memory_percent,
        "gpu_percent": metrics.gpu_percent,
        "gpu_memory_used_gb": metrics.gpu_memory_used_gb,
    }

    profile = await optimizer_service.analyze_performance(current, area)
    suggestions = await optimizer_service.suggest_optimizations(current)

    return {
        "profile": {
            "name": profile.name,
            "bottlenecks": profile.bottlenecks,
            "recommendations": profile.recommendations,
        },
        "suggestions": [
            {
                "id": s.id,
                "title": s.title,
                "description": s.description,
                "priority": s.priority,
                "effort": s.implementation_effort,
                "benefit": s.expected_benefit,
            }
            for s in suggestions
        ],
    }


@app.on_event("startup")
async def startup_event():
    await monitor_service.start_monitoring()
    asyncio.create_task(orchestrator.run_task_processor())


@app.on_event("shutdown")
async def shutdown_event():
    orchestrator.stop()
    await monitor_service.stop_monitoring()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.BACKEND_HOST, port=settings.BACKEND_PORT)
