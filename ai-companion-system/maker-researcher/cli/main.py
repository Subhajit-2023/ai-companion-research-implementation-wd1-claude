#!/usr/bin/env python3
"""
Maker-Researcher CLI - Command-line interface for the autonomous AI system
"""
import asyncio
import argparse
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings, ensure_directories
from agents.orchestrator import orchestrator
from core.task_queue import task_queue
from core.workflow import workflow_manager
from services.research import research_service
from services.document_processor import document_processor
from services.code_service import code_service
from services.debugger import debugger_service
from services.monitor import monitor_service
from services.optimizer import optimizer_service


class CLI:
    def __init__(self):
        self.running = True

    def print_header(self):
        print("\n" + "=" * 60)
        print(f"  {settings.APP_NAME} v{settings.APP_VERSION}")
        print("  Autonomous AI Research and Development System")
        print("=" * 60 + "\n")

    def print_help(self):
        help_text = """
Available Commands:
  chat <message>        - Chat with the AI assistant
  research <query>      - Perform comprehensive research
  code <description>    - Generate code
  analyze <file>        - Analyze a code file
  debug <error>         - Debug an error
  optimize              - Get optimization suggestions

  task create <title>   - Create a new task
  task list             - List all tasks
  task status <id>      - Get task status
  task cancel <id>      - Cancel a task

  approve list          - List pending approvals
  approve <id>          - Approve a change
  reject <id> [reason]  - Reject a change

  doc add <path>        - Process a document/ebook
  doc list              - List processed documents
  doc search <query>    - Search knowledge base

  metrics               - Show system metrics
  health                - Show health status
  status                - Show overall status

  help                  - Show this help
  exit / quit           - Exit the CLI
"""
        print(help_text)

    async def handle_chat(self, message: str):
        print("\nThinking...")
        result = await orchestrator.process_message(message)

        print(f"\n[{result['agent'].upper()}]")
        print("-" * 40)
        print(result['response'])
        print("-" * 40)

        if result.get('actions'):
            print(f"\nActions taken: {len(result['actions'])}")

    async def handle_research(self, query: str):
        print(f"\nResearching: {query}")
        print("This may take a moment...")

        session = await research_service.comprehensive_research(
            query,
            include_papers=True,
            include_code=True,
        )

        print(f"\n{'=' * 60}")
        print(f"Research Session: {session.id}")
        print(f"{'=' * 60}")
        print(f"Web Results: {len(session.results)}")
        print(f"Academic Papers: {len(session.papers)}")
        print(f"Code Examples: {len(session.code_examples)}")

        if session.results:
            print(f"\n--- Top Web Results ---")
            for r in session.results[:3]:
                print(f"  - {r.title[:60]}")
                print(f"    {r.url}")

        if session.papers:
            print(f"\n--- Top Papers ---")
            for p in session.papers[:3]:
                print(f"  - {p.title[:60]}")
                print(f"    Authors: {', '.join(p.authors[:2])} | Year: {p.year}")

        if session.code_examples:
            print(f"\n--- Top Repositories ---")
            for c in session.code_examples[:3]:
                print(f"  - {c.repo_name} ({c.stars} stars)")
                print(f"    {c.url}")

    async def handle_code_generate(self, description: str):
        print(f"\nGenerating code for: {description}")

        result = await code_service.generate_code(description)

        if result:
            print(f"\n{'=' * 60}")
            print("Generated Code:")
            print(f"{'=' * 60}")
            print(result.modified)
            print(f"\nConfidence: {result.confidence:.0%}")
        else:
            print("Code generation failed.")

    async def handle_analyze(self, file_path: str):
        print(f"\nAnalyzing: {file_path}")

        analysis = await code_service.analyze_file(file_path)

        if analysis:
            print(f"\n{'=' * 60}")
            print(f"Analysis: {analysis.file_path}")
            print(f"{'=' * 60}")
            print(f"Language: {analysis.language}")
            print(f"Lines of Code: {analysis.loc}")
            print(f"Functions: {len(analysis.functions)}")
            print(f"Classes: {len(analysis.classes)}")
            print(f"Complexity Score: {analysis.complexity_score:.1f}/10")

            if analysis.issues:
                print(f"\nIssues ({len(analysis.issues)}):")
                for issue in analysis.issues[:5]:
                    print(f"  - [{issue.get('severity', 'info')}] {issue.get('message', '')[:60]}")

            if analysis.suggestions:
                print(f"\nSuggestions:")
                for s in analysis.suggestions[:3]:
                    print(f"  - {s[:80]}")
        else:
            print("Analysis failed. File not found or unsupported.")

    async def handle_debug(self, error_text: str):
        print("\nAnalyzing error...")

        analysis = await debugger_service.analyze_error(error_text)

        print(f"\n{'=' * 60}")
        print("Debug Analysis")
        print(f"{'=' * 60}")
        print(f"Error Type: {analysis['error_info']['type']}")
        print(f"Message: {analysis['error_info']['message']}")

        if analysis['error_info'].get('file'):
            print(f"File: {analysis['error_info']['file']}")
            print(f"Line: {analysis['error_info']['line']}")

        print(f"\nAnalysis:")
        print(analysis['analysis'][:1000])

    async def handle_optimize(self):
        print("\nCollecting metrics and analyzing...")

        metrics = monitor_service.collect_system_metrics()
        current = {
            "memory_percent": metrics.memory_percent,
            "gpu_percent": metrics.gpu_percent,
            "gpu_memory_used_gb": metrics.gpu_memory_used_gb,
        }

        profile = await optimizer_service.analyze_performance(current)
        suggestions = await optimizer_service.suggest_optimizations(current)

        print(f"\n{'=' * 60}")
        print("Optimization Analysis")
        print(f"{'=' * 60}")

        print(f"\nCurrent System:")
        print(f"  Memory: {metrics.memory_percent:.1f}%")
        if metrics.gpu_percent:
            print(f"  GPU: {metrics.gpu_percent:.1f}%")
        if metrics.gpu_memory_used_gb:
            print(f"  VRAM: {metrics.gpu_memory_used_gb:.1f}GB")

        if profile.bottlenecks:
            print(f"\nBottlenecks:")
            for b in profile.bottlenecks:
                print(f"  - {b}")

        if profile.recommendations:
            print(f"\nRecommendations:")
            for r in profile.recommendations[:5]:
                print(f"  - {r[:80]}")

        if suggestions:
            print(f"\nSuggestions:")
            for s in suggestions[:5]:
                print(f"  [{s.priority}] {s.title}")
                print(f"      {s.expected_benefit}")

    async def handle_task_create(self, args: list):
        if not args:
            print("Usage: task create <title>")
            return

        title = " ".join(args)
        print(f"\nWhat should this task do? (enter description)")
        description = input("> ").strip()

        print("Category (research/code/debug/optimize/advise):")
        category = input("> ").strip() or "advise"

        task = await orchestrator.create_and_queue_task(
            title=title,
            description=description,
            category=category,
        )

        print(f"\nTask created: {task.id}")
        print(f"Title: {task.title}")
        print(f"Status: {task.status.value}")

    async def handle_task_list(self):
        tasks = list(task_queue.tasks.values())

        print(f"\n{'=' * 60}")
        print(f"Tasks ({len(tasks)})")
        print(f"{'=' * 60}")

        for task in tasks[-10:]:
            status_icon = {
                "pending": ".",
                "in_progress": "*",
                "completed": "+",
                "failed": "x",
                "awaiting_approval": "?",
            }.get(task.status.value, " ")

            print(f"  [{status_icon}] {task.id}: {task.title[:40]}")

        stats = task_queue.get_stats()
        print(f"\nTotal: {stats['total_tasks']} | Running: {stats['running_tasks']} | Completed: {stats['completed_tasks']}")

    async def handle_approve_list(self):
        pending = workflow_manager.get_pending_requests()

        print(f"\n{'=' * 60}")
        print(f"Pending Approvals ({len(pending)})")
        print(f"{'=' * 60}")

        for request in pending:
            print(f"\n  ID: {request.id}")
            print(f"  Task: {request.task_id}")
            print(f"  Summary: {request.summary[:60]}")
            print(f"  Changes: {len(request.changes)}")

        if not pending:
            print("  No pending approvals")

    async def handle_approve(self, request_id: str):
        success = workflow_manager.approve(request_id)
        if success:
            print(f"Approved: {request_id}")
        else:
            print(f"Failed to approve: {request_id}")

    async def handle_reject(self, request_id: str, reason: str = ""):
        success = workflow_manager.reject(request_id, reason)
        if success:
            print(f"Rejected: {request_id}")
        else:
            print(f"Failed to reject: {request_id}")

    async def handle_doc_add(self, file_path: str):
        print(f"\nProcessing: {file_path}")

        doc = await document_processor.process_document(file_path)

        if doc:
            print(f"\n{'=' * 60}")
            print(f"Document Processed")
            print(f"{'=' * 60}")
            print(f"ID: {doc.id}")
            print(f"Title: {doc.title}")
            print(f"Author: {doc.author}")
            print(f"Pages/Chapters: {doc.total_pages}")
            print(f"Chunks: {doc.total_chunks}")
        else:
            print("Failed to process document.")

    async def handle_doc_list(self):
        docs = document_processor.list_documents()
        stats = document_processor.get_stats()

        print(f"\n{'=' * 60}")
        print(f"Knowledge Base ({stats['total_documents']} documents)")
        print(f"{'=' * 60}")

        for doc in docs:
            print(f"  [{doc['id']}] {doc['title'][:40]} ({doc['file_type']})")

        print(f"\nTotal chunks: {stats['total_chunks']}")
        print(f"By type: {stats['by_type']}")

    async def handle_doc_search(self, query: str):
        print(f"\nSearching: {query}")

        results = await document_processor.search(query, n_results=5)

        print(f"\n{'=' * 60}")
        print(f"Search Results ({len(results)})")
        print(f"{'=' * 60}")

        for r in results:
            print(f"\n  Document: {r['metadata'].get('document_title', 'Unknown')}")
            print(f"  Content: {r['content'][:200]}...")

    async def handle_metrics(self):
        report = monitor_service.get_full_report()

        print(f"\n{'=' * 60}")
        print("System Metrics")
        print(f"{'=' * 60}")

        sys_info = report.get('system', {}).get('current', {})
        print(f"\nSystem:")
        print(f"  CPU: {sys_info.get('cpu_percent', 0):.1f}%")
        print(f"  Memory: {sys_info.get('memory_percent', 0):.1f}% ({sys_info.get('memory_used_gb', 0):.1f}GB)")
        if sys_info.get('gpu_percent'):
            print(f"  GPU: {sys_info.get('gpu_percent', 0):.1f}%")
        if sys_info.get('gpu_memory_used_gb'):
            print(f"  VRAM: {sys_info.get('gpu_memory_used_gb', 0):.1f}GB / {sys_info.get('gpu_memory_total_gb', 0):.1f}GB")
        print(f"  Disk: {sys_info.get('disk_percent', 0):.1f}%")

        comp = report.get('companion', {})
        print(f"\nCompanion System:")
        print(f"  Conversations: {comp.get('conversations', 0)}")
        print(f"  Messages: {comp.get('messages', 0)}")
        print(f"  Images: {comp.get('images_generated', 0)}")

    async def handle_health(self):
        health = monitor_service.get_health_status()

        print(f"\n{'=' * 60}")
        print(f"Health Status: {health['overall'].upper()}")
        print(f"{'=' * 60}")

        if health['issues']:
            print("\nIssues:")
            for issue in health['issues']:
                print(f"  - {issue}")
        else:
            print("\nNo issues detected.")

    async def handle_status(self):
        status = orchestrator.get_status()

        print(f"\n{'=' * 60}")
        print("Maker-Researcher Status")
        print(f"{'=' * 60}")

        print(f"\nOrchestrator:")
        print(f"  Running: {status['running']}")
        print(f"  Context messages: {status['context_messages']}")
        print(f"  Actions taken: {status['actions_taken']}")

        print(f"\nTask Queue:")
        tq = status['task_queue']
        print(f"  Total: {tq['total_tasks']}")
        print(f"  Running: {tq['running_tasks']}")
        print(f"  Completed: {tq['completed_tasks']}")

        print(f"\nPending Approvals: {status['pending_approvals']}")

        brain_status = status['brain_status']
        print(f"\nBrain:")
        print(f"  Model: {brain_status['current_model']}")
        print(f"  History: {brain_status['history_length']} messages")

    async def run_interactive(self):
        self.print_header()
        self.print_help()

        while self.running:
            try:
                user_input = input("\nresearcher> ").strip()

                if not user_input:
                    continue

                parts = user_input.split(maxsplit=1)
                command = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""

                if command in ['exit', 'quit', 'q']:
                    print("\nGoodbye!")
                    self.running = False

                elif command == 'help':
                    self.print_help()

                elif command == 'chat':
                    if args:
                        await self.handle_chat(args)
                    else:
                        print("Usage: chat <message>")

                elif command == 'research':
                    if args:
                        await self.handle_research(args)
                    else:
                        print("Usage: research <query>")

                elif command == 'code':
                    if args:
                        await self.handle_code_generate(args)
                    else:
                        print("Usage: code <description>")

                elif command == 'analyze':
                    if args:
                        await self.handle_analyze(args)
                    else:
                        print("Usage: analyze <file_path>")

                elif command == 'debug':
                    if args:
                        await self.handle_debug(args)
                    else:
                        print("Usage: debug <error_text>")

                elif command == 'optimize':
                    await self.handle_optimize()

                elif command == 'task':
                    task_parts = args.split(maxsplit=1)
                    task_cmd = task_parts[0] if task_parts else ""
                    task_args = task_parts[1].split() if len(task_parts) > 1 else []

                    if task_cmd == 'create':
                        await self.handle_task_create(task_args)
                    elif task_cmd == 'list':
                        await self.handle_task_list()
                    else:
                        print("Usage: task create|list|status|cancel")

                elif command == 'approve':
                    if args == 'list':
                        await self.handle_approve_list()
                    elif args:
                        await self.handle_approve(args)
                    else:
                        print("Usage: approve list|<request_id>")

                elif command == 'reject':
                    if args:
                        parts = args.split(maxsplit=1)
                        request_id = parts[0]
                        reason = parts[1] if len(parts) > 1 else ""
                        await self.handle_reject(request_id, reason)
                    else:
                        print("Usage: reject <request_id> [reason]")

                elif command == 'doc':
                    doc_parts = args.split(maxsplit=1)
                    doc_cmd = doc_parts[0] if doc_parts else ""
                    doc_args = doc_parts[1] if len(doc_parts) > 1 else ""

                    if doc_cmd == 'add':
                        await self.handle_doc_add(doc_args)
                    elif doc_cmd == 'list':
                        await self.handle_doc_list()
                    elif doc_cmd == 'search':
                        await self.handle_doc_search(doc_args)
                    else:
                        print("Usage: doc add|list|search")

                elif command == 'metrics':
                    await self.handle_metrics()

                elif command == 'health':
                    await self.handle_health()

                elif command == 'status':
                    await self.handle_status()

                else:
                    await self.handle_chat(user_input)

            except KeyboardInterrupt:
                print("\n\nInterrupted. Type 'exit' to quit.")
            except Exception as e:
                print(f"\nError: {e}")


def main():
    ensure_directories()

    parser = argparse.ArgumentParser(description="AI Maker-Researcher CLI")
    parser.add_argument('command', nargs='?', help='Command to run')
    parser.add_argument('args', nargs='*', help='Command arguments')
    parser.add_argument('--api', action='store_true', help='Start API server')

    args = parser.parse_args()

    if args.api:
        import uvicorn
        from api.main import app
        uvicorn.run(app, host=settings.BACKEND_HOST, port=settings.BACKEND_PORT)
    else:
        cli = CLI()
        asyncio.run(cli.run_interactive())


if __name__ == "__main__":
    main()
