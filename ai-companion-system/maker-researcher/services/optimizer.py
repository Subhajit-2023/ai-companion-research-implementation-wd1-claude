"""
Optimizer Service - Self-improvement, performance optimization, and system enhancement
"""
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import settings
from core.brain import brain, ModelType


@dataclass
class OptimizationSuggestion:
    id: str
    category: str
    title: str
    description: str
    expected_benefit: str
    implementation_effort: str
    priority: int
    metrics_affected: List[str]
    code_changes: List[Dict] = field(default_factory=list)
    status: str = "pending"


@dataclass
class PerformanceProfile:
    name: str
    avg_response_time: float
    memory_usage: float
    gpu_usage: Optional[float]
    throughput: float
    bottlenecks: List[str]
    recommendations: List[str]


class OptimizerService:
    def __init__(self):
        self.suggestions: List[OptimizationSuggestion] = []
        self.improvement_history: List[Dict] = []
        self.baseline_metrics: Dict = {}
        self.data_dir = Path(settings.DATA_DIR) / "optimizer"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._load_data()

        self.optimization_areas = [
            "response_time",
            "memory_usage",
            "gpu_efficiency",
            "code_quality",
            "user_experience",
            "model_inference",
            "database_queries",
            "api_performance",
        ]

    def _load_data(self):
        data_file = self.data_dir / "optimizer_data.json"
        if data_file.exists():
            try:
                with open(data_file, "r") as f:
                    data = json.load(f)
                    self.baseline_metrics = data.get("baseline", {})
                    self.improvement_history = data.get("history", [])
            except Exception as e:
                print(f"Error loading optimizer data: {e}")

    def _save_data(self):
        data_file = self.data_dir / "optimizer_data.json"
        try:
            data = {
                "baseline": self.baseline_metrics,
                "history": self.improvement_history[-100:],
                "updated_at": datetime.utcnow().isoformat(),
            }
            with open(data_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving optimizer data: {e}")

    def set_baseline(self, metrics: Dict):
        self.baseline_metrics = {
            **metrics,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._save_data()

    async def analyze_performance(
        self,
        current_metrics: Dict,
        area: Optional[str] = None,
    ) -> PerformanceProfile:
        bottlenecks = []
        recommendations = []

        response_time = current_metrics.get("avg_response_time", 0)
        memory_usage = current_metrics.get("memory_percent", 0)
        gpu_usage = current_metrics.get("gpu_percent")
        throughput = current_metrics.get("requests_per_minute", 0)

        if response_time > 5.0:
            bottlenecks.append("High response latency")
            recommendations.append("Consider response caching or model optimization")

        if memory_usage > 80:
            bottlenecks.append("High memory usage")
            recommendations.append("Implement memory cleanup or reduce batch sizes")

        if gpu_usage and gpu_usage > 90:
            bottlenecks.append("GPU memory pressure")
            recommendations.append("Use model quantization or reduce context window")

        if self.baseline_metrics:
            baseline_rt = self.baseline_metrics.get("avg_response_time", response_time)
            if response_time > baseline_rt * 1.5:
                bottlenecks.append("Performance degradation detected")
                recommendations.append("Review recent changes for performance impact")

        prompt = f"""Analyze these system metrics and suggest optimizations:

Current Metrics:
- Response Time: {response_time:.2f}s
- Memory Usage: {memory_usage:.1f}%
- GPU Usage: {gpu_usage if gpu_usage else 'N/A'}%
- Throughput: {throughput:.1f} req/min

Hardware: RTX 4060 8GB VRAM, Lenovo Legion 5

Focus Area: {area or 'general'}

Detected bottlenecks: {', '.join(bottlenecks) if bottlenecks else 'None'}

Provide 3-5 specific, actionable optimization recommendations for this hardware:"""

        response = await brain.think(
            prompt=prompt,
            agent_type="optimizer",
            task_type=ModelType.REASONING,
        )

        if not response.error:
            for line in response.content.split("\n"):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith("-")):
                    rec = line.lstrip("0123456789.-) ")
                    if rec and rec not in recommendations:
                        recommendations.append(rec)

        return PerformanceProfile(
            name=area or "general",
            avg_response_time=response_time,
            memory_usage=memory_usage,
            gpu_usage=gpu_usage,
            throughput=throughput,
            bottlenecks=bottlenecks,
            recommendations=recommendations[:10],
        )

    async def suggest_optimizations(
        self,
        metrics: Dict,
        code_analysis: Optional[Dict] = None,
    ) -> List[OptimizationSuggestion]:
        import uuid
        suggestions = []

        if metrics.get("avg_response_time", 0) > 3.0:
            suggestions.append(OptimizationSuggestion(
                id=str(uuid.uuid4())[:8],
                category="response_time",
                title="Implement Response Caching",
                description="Add caching layer for frequently requested responses",
                expected_benefit="30-50% reduction in response time for cached requests",
                implementation_effort="medium",
                priority=1,
                metrics_affected=["response_time", "throughput"],
            ))

        if metrics.get("memory_percent", 0) > 75:
            suggestions.append(OptimizationSuggestion(
                id=str(uuid.uuid4())[:8],
                category="memory_usage",
                title="Optimize Memory Management",
                description="Implement aggressive garbage collection and memory pooling",
                expected_benefit="15-25% reduction in memory usage",
                implementation_effort="low",
                priority=2,
                metrics_affected=["memory_usage"],
            ))

        if metrics.get("gpu_memory_used_gb", 0) > 6:
            suggestions.append(OptimizationSuggestion(
                id=str(uuid.uuid4())[:8],
                category="gpu_efficiency",
                title="Use 4-bit Quantized Models",
                description="Switch to q4_K_M quantized models to reduce VRAM usage",
                expected_benefit="40-50% reduction in VRAM usage with minimal quality loss",
                implementation_effort="low",
                priority=1,
                metrics_affected=["gpu_memory", "inference_time"],
            ))

        if code_analysis:
            if code_analysis.get("issues_count", 0) > 10:
                suggestions.append(OptimizationSuggestion(
                    id=str(uuid.uuid4())[:8],
                    category="code_quality",
                    title="Fix Code Quality Issues",
                    description=f"Address {code_analysis['issues_count']} detected code issues",
                    expected_benefit="Improved maintainability and reduced bug risk",
                    implementation_effort="medium",
                    priority=3,
                    metrics_affected=["reliability"],
                ))

            complex_files = [
                f for f in code_analysis.get("files", [])
                if f.get("complexity", 0) > 7
            ]
            if complex_files:
                suggestions.append(OptimizationSuggestion(
                    id=str(uuid.uuid4())[:8],
                    category="code_quality",
                    title="Reduce Code Complexity",
                    description=f"Refactor {len(complex_files)} high-complexity files",
                    expected_benefit="Better maintainability and testability",
                    implementation_effort="high",
                    priority=4,
                    metrics_affected=["maintainability"],
                ))

        self.suggestions = suggestions
        return suggestions

    async def generate_rtx4060_optimizations(self) -> List[Dict]:
        optimizations = [
            {
                "category": "Model Selection",
                "recommendations": [
                    "Use mistral:7b-instruct-v0.2-q4_K_M (4.5GB VRAM)",
                    "Consider deepseek-coder:6.7b-q4_K_M for coding tasks",
                    "Avoid 13B+ models without offloading",
                ],
            },
            {
                "category": "Inference Settings",
                "recommendations": [
                    "Set num_ctx to 4096 (vs 8192) for faster inference",
                    "Use num_predict=1024 for typical responses",
                    "Enable flash_attention if supported",
                    "Set num_gpu=1 to use all GPU layers",
                ],
            },
            {
                "category": "Memory Management",
                "recommendations": [
                    "Set PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512",
                    "Enable model offloading for long sessions",
                    "Clear CUDA cache between major operations",
                    "Use bfloat16 precision when possible",
                ],
            },
            {
                "category": "Concurrent Operations",
                "recommendations": [
                    "Limit concurrent LLM requests to 1",
                    "Queue image generation separately from chat",
                    "Batch similar requests when possible",
                    "Use async processing for non-critical tasks",
                ],
            },
            {
                "category": "Stable Diffusion",
                "recommendations": [
                    "Use SDXL with VAE tiling for large images",
                    "Set --medvram flag in webui arguments",
                    "Use 512x512 for faster generation, upscale later",
                    "Enable attention slicing",
                ],
            },
        ]

        return optimizations

    async def create_optimization_plan(
        self,
        target_area: str,
        current_state: Dict,
        goals: List[str],
    ) -> Dict:
        prompt = f"""Create an optimization plan for {target_area}:

Current State:
{json.dumps(current_state, indent=2)}

Goals:
{chr(10).join(f"- {g}" for g in goals)}

Hardware: Lenovo Legion 5, RTX 4060 8GB VRAM

Create a step-by-step optimization plan with:
1. Priority actions
2. Expected improvements
3. Implementation steps
4. Verification methods

Plan:"""

        response = await brain.think(
            prompt=prompt,
            agent_type="optimizer",
            task_type=ModelType.REASONING,
        )

        return {
            "area": target_area,
            "goals": goals,
            "plan": response.content,
            "created_at": datetime.utcnow().isoformat(),
        }

    async def analyze_improvement_opportunity(
        self,
        description: str,
        context: Optional[str] = None,
    ) -> Dict:
        prompt = f"""Analyze this improvement opportunity:

{description}

{f"Context: {context}" if context else ""}

Evaluate:
1. Feasibility (given RTX 4060 8GB constraints)
2. Expected benefit
3. Implementation complexity
4. Potential risks
5. Alternative approaches

Analysis:"""

        response = await brain.think(
            prompt=prompt,
            agent_type="optimizer",
            task_type=ModelType.REASONING,
        )

        return {
            "description": description,
            "analysis": response.content,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def research_optimization_techniques(
        self,
        topic: str,
    ) -> Dict:
        from services.research import research_service

        session = await research_service.comprehensive_research(
            f"{topic} optimization techniques AI local inference",
            include_papers=True,
            include_code=True,
        )

        summary_prompt = f"""Summarize these research results for optimizing {topic}:

{research_service.format_research_for_llm(session)[:3000]}

Provide:
1. Key techniques discovered
2. Applicable to RTX 4060 8GB setup
3. Implementation recommendations
4. Expected benefits

Summary:"""

        response = await brain.think(
            prompt=summary_prompt,
            agent_type="researcher",
            task_type=ModelType.REASONING,
        )

        return {
            "topic": topic,
            "research_session_id": session.id,
            "sources_count": len(session.results) + len(session.papers),
            "summary": response.content,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def record_improvement(
        self,
        suggestion_id: str,
        before_metrics: Dict,
        after_metrics: Dict,
        success: bool,
    ):
        improvement = {
            "suggestion_id": suggestion_id,
            "before": before_metrics,
            "after": after_metrics,
            "success": success,
            "improvement_percent": {},
            "timestamp": datetime.utcnow().isoformat(),
        }

        for key in before_metrics:
            if key in after_metrics:
                before_val = before_metrics[key]
                after_val = after_metrics[key]
                if isinstance(before_val, (int, float)) and before_val > 0:
                    change = ((after_val - before_val) / before_val) * 100
                    improvement["improvement_percent"][key] = round(change, 2)

        self.improvement_history.append(improvement)

        for suggestion in self.suggestions:
            if suggestion.id == suggestion_id:
                suggestion.status = "applied" if success else "failed"
                break

        self._save_data()

    def get_improvement_stats(self) -> Dict:
        if not self.improvement_history:
            return {"total": 0, "successful": 0, "avg_improvement": {}}

        successful = [i for i in self.improvement_history if i["success"]]

        avg_improvements = {}
        for imp in successful:
            for key, value in imp.get("improvement_percent", {}).items():
                if key not in avg_improvements:
                    avg_improvements[key] = []
                avg_improvements[key].append(value)

        for key in avg_improvements:
            avg_improvements[key] = round(sum(avg_improvements[key]) / len(avg_improvements[key]), 2)

        return {
            "total": len(self.improvement_history),
            "successful": len(successful),
            "success_rate": round(len(successful) / len(self.improvement_history) * 100, 1),
            "avg_improvement": avg_improvements,
        }

    def get_pending_suggestions(self) -> List[OptimizationSuggestion]:
        return [s for s in self.suggestions if s.status == "pending"]


optimizer_service = OptimizerService()


if __name__ == "__main__":
    async def test_optimizer():
        print("Testing Optimizer Service...")

        test_metrics = {
            "avg_response_time": 4.5,
            "memory_percent": 78,
            "gpu_percent": 85,
            "gpu_memory_used_gb": 6.2,
            "requests_per_minute": 10,
        }

        print("\nAnalyzing performance...")
        profile = await optimizer_service.analyze_performance(test_metrics)
        print(f"Bottlenecks: {profile.bottlenecks}")
        print(f"Recommendations: {len(profile.recommendations)}")

        print("\nGenerating RTX 4060 optimizations...")
        rtx_opts = await optimizer_service.generate_rtx4060_optimizations()
        for opt in rtx_opts:
            print(f"\n{opt['category']}:")
            for rec in opt['recommendations'][:2]:
                print(f"  - {rec}")

        print("\nSuggesting optimizations...")
        suggestions = await optimizer_service.suggest_optimizations(test_metrics)
        print(f"Generated {len(suggestions)} suggestions")
        for s in suggestions[:3]:
            print(f"  - [{s.priority}] {s.title}")

    asyncio.run(test_optimizer())
