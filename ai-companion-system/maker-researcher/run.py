#!/usr/bin/env python3
"""
Main entry point for the AI Maker-Researcher system
"""
import sys
import asyncio
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import settings, ensure_directories


def run_api():
    import uvicorn
    from api.main import app

    print(f"\n{'=' * 60}")
    print(f"  {settings.APP_NAME} API Server")
    print(f"  Version: {settings.APP_VERSION}")
    print(f"{'=' * 60}")
    print(f"\n  Starting server on http://{settings.BACKEND_HOST}:{settings.BACKEND_PORT}")
    print(f"  API docs: http://localhost:{settings.BACKEND_PORT}/docs")
    print(f"\n{'=' * 60}\n")

    uvicorn.run(
        app,
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        log_level="info",
    )


def run_cli():
    from cli.main import CLI

    cli = CLI()
    asyncio.run(cli.run_interactive())


async def run_task(task_type: str, args: dict):
    from agents.orchestrator import orchestrator

    print(f"\nRunning {task_type} task...")

    if task_type == "research":
        from services.research import research_service
        session = await research_service.comprehensive_research(
            args.get("query", ""),
            include_papers=True,
            include_code=True,
        )
        print(research_service.format_research_for_llm(session))

    elif task_type == "analyze":
        from services.code_service import code_service
        analysis = await code_service.analyze_project(args.get("path"))
        print(f"\nProject Analysis:")
        print(f"  Files: {len(analysis.get('files', []))}")
        print(f"  Total LOC: {analysis.get('total_loc', 0)}")
        print(f"  Issues: {analysis.get('issues_count', 0)}")

    elif task_type == "optimize":
        from services.monitor import monitor_service
        from services.optimizer import optimizer_service

        metrics = monitor_service.collect_system_metrics()
        profile = await optimizer_service.analyze_performance({
            "memory_percent": metrics.memory_percent,
            "gpu_percent": metrics.gpu_percent,
        })

        print(f"\nOptimization Analysis:")
        print(f"  Bottlenecks: {profile.bottlenecks}")
        for rec in profile.recommendations[:5]:
            print(f"  - {rec}")

    elif task_type == "status":
        from services.monitor import monitor_service
        report = monitor_service.get_full_report()
        import json
        print(json.dumps(report, indent=2, default=str))


def main():
    ensure_directories()

    parser = argparse.ArgumentParser(
        description="AI Maker-Researcher - Autonomous AI System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py                    # Start interactive CLI
  python run.py --api              # Start API server
  python run.py research "query"   # Run research task
  python run.py analyze ./path     # Analyze codebase
  python run.py optimize           # Get optimization suggestions
  python run.py status             # Show system status
        """,
    )

    parser.add_argument(
        'command',
        nargs='?',
        choices=['research', 'analyze', 'optimize', 'status'],
        help='Task to run',
    )
    parser.add_argument(
        'args',
        nargs='*',
        help='Task arguments',
    )
    parser.add_argument(
        '--api',
        action='store_true',
        help='Start the API server',
    )
    parser.add_argument(
        '--cli',
        action='store_true',
        help='Start interactive CLI (default)',
    )

    args = parser.parse_args()

    if args.api:
        run_api()
    elif args.command:
        task_args = {}
        if args.command == 'research' and args.args:
            task_args['query'] = ' '.join(args.args)
        elif args.command == 'analyze' and args.args:
            task_args['path'] = args.args[0]

        asyncio.run(run_task(args.command, task_args))
    else:
        run_cli()


if __name__ == "__main__":
    main()
