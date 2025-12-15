"""
Monitor Service - Data collection, metrics, and system monitoring
"""
import asyncio
import psutil
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import settings

try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False


@dataclass
class SystemMetrics:
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_available_gb: float
    gpu_percent: Optional[float] = None
    gpu_memory_used_gb: Optional[float] = None
    gpu_memory_total_gb: Optional[float] = None
    disk_percent: float = 0.0
    network_bytes_sent: int = 0
    network_bytes_recv: int = 0


@dataclass
class ServiceMetrics:
    name: str
    requests_total: int = 0
    requests_success: int = 0
    requests_failed: int = 0
    avg_response_time: float = 0.0
    last_request_time: Optional[datetime] = None
    errors: List[str] = field(default_factory=list)


@dataclass
class CompanionMetrics:
    conversations_total: int = 0
    messages_total: int = 0
    avg_response_time: float = 0.0
    images_generated: int = 0
    memories_stored: int = 0
    voice_interactions: int = 0
    active_characters: int = 0


class MonitorService:
    def __init__(self):
        self.enabled = settings.COLLECT_METRICS
        self.interval = settings.METRICS_INTERVAL
        self.data_dir = Path(settings.DATA_DIR) / "metrics"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.system_history: List[SystemMetrics] = []
        self.service_metrics: Dict[str, ServiceMetrics] = {}
        self.companion_metrics = CompanionMetrics()
        self.max_history = 1000

        self._load_metrics()
        self._monitoring = False
        self._monitor_task = None

    def _load_metrics(self):
        metrics_file = self.data_dir / "metrics.json"
        if metrics_file.exists():
            try:
                with open(metrics_file, "r") as f:
                    data = json.load(f)

                    for svc_data in data.get("services", {}).values():
                        svc = ServiceMetrics(
                            name=svc_data["name"],
                            requests_total=svc_data.get("requests_total", 0),
                            requests_success=svc_data.get("requests_success", 0),
                            requests_failed=svc_data.get("requests_failed", 0),
                            avg_response_time=svc_data.get("avg_response_time", 0.0),
                        )
                        self.service_metrics[svc.name] = svc

                    comp = data.get("companion", {})
                    self.companion_metrics = CompanionMetrics(
                        conversations_total=comp.get("conversations_total", 0),
                        messages_total=comp.get("messages_total", 0),
                        avg_response_time=comp.get("avg_response_time", 0.0),
                        images_generated=comp.get("images_generated", 0),
                        memories_stored=comp.get("memories_stored", 0),
                        voice_interactions=comp.get("voice_interactions", 0),
                        active_characters=comp.get("active_characters", 0),
                    )

            except Exception as e:
                print(f"Error loading metrics: {e}")

    def _save_metrics(self):
        metrics_file = self.data_dir / "metrics.json"
        try:
            data = {
                "services": {
                    name: {
                        "name": svc.name,
                        "requests_total": svc.requests_total,
                        "requests_success": svc.requests_success,
                        "requests_failed": svc.requests_failed,
                        "avg_response_time": svc.avg_response_time,
                    }
                    for name, svc in self.service_metrics.items()
                },
                "companion": {
                    "conversations_total": self.companion_metrics.conversations_total,
                    "messages_total": self.companion_metrics.messages_total,
                    "avg_response_time": self.companion_metrics.avg_response_time,
                    "images_generated": self.companion_metrics.images_generated,
                    "memories_stored": self.companion_metrics.memories_stored,
                    "voice_interactions": self.companion_metrics.voice_interactions,
                    "active_characters": self.companion_metrics.active_characters,
                },
                "updated_at": datetime.utcnow().isoformat(),
            }
            with open(metrics_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving metrics: {e}")

    def collect_system_metrics(self) -> SystemMetrics:
        cpu_percent = psutil.cpu_percent(interval=0.1)

        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used_gb = memory.used / (1024**3)
        memory_available_gb = memory.available / (1024**3)

        disk = psutil.disk_usage("/")
        disk_percent = disk.percent

        network = psutil.net_io_counters()

        gpu_percent = None
        gpu_memory_used = None
        gpu_memory_total = None

        if GPU_AVAILABLE:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]
                    gpu_percent = gpu.load * 100
                    gpu_memory_used = gpu.memoryUsed / 1024
                    gpu_memory_total = gpu.memoryTotal / 1024
            except Exception:
                pass

        metrics = SystemMetrics(
            timestamp=datetime.utcnow(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_used_gb=memory_used_gb,
            memory_available_gb=memory_available_gb,
            gpu_percent=gpu_percent,
            gpu_memory_used_gb=gpu_memory_used,
            gpu_memory_total_gb=gpu_memory_total,
            disk_percent=disk_percent,
            network_bytes_sent=network.bytes_sent,
            network_bytes_recv=network.bytes_recv,
        )

        self.system_history.append(metrics)
        if len(self.system_history) > self.max_history:
            self.system_history = self.system_history[-self.max_history:]

        return metrics

    def record_service_request(
        self,
        service_name: str,
        success: bool,
        response_time: float,
        error: Optional[str] = None,
    ):
        if service_name not in self.service_metrics:
            self.service_metrics[service_name] = ServiceMetrics(name=service_name)

        svc = self.service_metrics[service_name]
        svc.requests_total += 1
        svc.last_request_time = datetime.utcnow()

        if success:
            svc.requests_success += 1
        else:
            svc.requests_failed += 1
            if error:
                svc.errors.append(f"{datetime.utcnow().isoformat()}: {error[:200]}")
                svc.errors = svc.errors[-50:]

        total = svc.requests_total
        svc.avg_response_time = (
            (svc.avg_response_time * (total - 1) + response_time) / total
        )

    def record_companion_activity(
        self,
        activity_type: str,
        count: int = 1,
        response_time: Optional[float] = None,
    ):
        if activity_type == "conversation":
            self.companion_metrics.conversations_total += count
        elif activity_type == "message":
            self.companion_metrics.messages_total += count
            if response_time:
                total = self.companion_metrics.messages_total
                self.companion_metrics.avg_response_time = (
                    (self.companion_metrics.avg_response_time * (total - 1) + response_time) / total
                )
        elif activity_type == "image":
            self.companion_metrics.images_generated += count
        elif activity_type == "memory":
            self.companion_metrics.memories_stored += count
        elif activity_type == "voice":
            self.companion_metrics.voice_interactions += count
        elif activity_type == "character":
            self.companion_metrics.active_characters = count

    async def start_monitoring(self):
        if self._monitoring:
            return

        self._monitoring = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())

    async def stop_monitoring(self):
        self._monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass

    async def _monitor_loop(self):
        while self._monitoring:
            try:
                self.collect_system_metrics()
                self._save_metrics()
                await asyncio.sleep(self.interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Monitor error: {e}")
                await asyncio.sleep(self.interval)

    def get_system_summary(self) -> Dict:
        if not self.system_history:
            return {}

        latest = self.system_history[-1]
        recent = self.system_history[-10:] if len(self.system_history) >= 10 else self.system_history

        avg_cpu = sum(m.cpu_percent for m in recent) / len(recent)
        avg_memory = sum(m.memory_percent for m in recent) / len(recent)

        return {
            "current": {
                "cpu_percent": latest.cpu_percent,
                "memory_percent": latest.memory_percent,
                "memory_used_gb": round(latest.memory_used_gb, 2),
                "memory_available_gb": round(latest.memory_available_gb, 2),
                "gpu_percent": latest.gpu_percent,
                "gpu_memory_used_gb": round(latest.gpu_memory_used_gb, 2) if latest.gpu_memory_used_gb else None,
                "gpu_memory_total_gb": round(latest.gpu_memory_total_gb, 2) if latest.gpu_memory_total_gb else None,
                "disk_percent": latest.disk_percent,
            },
            "averages": {
                "cpu_percent": round(avg_cpu, 1),
                "memory_percent": round(avg_memory, 1),
            },
            "timestamp": latest.timestamp.isoformat(),
            "samples": len(self.system_history),
        }

    def get_service_summary(self) -> Dict:
        summary = {}
        for name, svc in self.service_metrics.items():
            success_rate = (
                (svc.requests_success / svc.requests_total * 100)
                if svc.requests_total > 0 else 0
            )
            summary[name] = {
                "requests_total": svc.requests_total,
                "success_rate": round(success_rate, 1),
                "avg_response_time_ms": round(svc.avg_response_time * 1000, 2),
                "recent_errors": len(svc.errors),
            }
        return summary

    def get_companion_summary(self) -> Dict:
        return {
            "conversations": self.companion_metrics.conversations_total,
            "messages": self.companion_metrics.messages_total,
            "avg_response_time_ms": round(self.companion_metrics.avg_response_time * 1000, 2),
            "images_generated": self.companion_metrics.images_generated,
            "memories_stored": self.companion_metrics.memories_stored,
            "voice_interactions": self.companion_metrics.voice_interactions,
            "active_characters": self.companion_metrics.active_characters,
        }

    def get_health_status(self) -> Dict:
        status = {
            "overall": "healthy",
            "issues": [],
        }

        if self.system_history:
            latest = self.system_history[-1]

            if latest.cpu_percent > 90:
                status["issues"].append("High CPU usage")
            if latest.memory_percent > 90:
                status["issues"].append("High memory usage")
            if latest.disk_percent > 90:
                status["issues"].append("Low disk space")
            if latest.gpu_memory_used_gb and latest.gpu_memory_total_gb:
                gpu_percent = (latest.gpu_memory_used_gb / latest.gpu_memory_total_gb) * 100
                if gpu_percent > 95:
                    status["issues"].append("GPU memory nearly full")

        for name, svc in self.service_metrics.items():
            if svc.requests_total > 10:
                error_rate = (svc.requests_failed / svc.requests_total) * 100
                if error_rate > 10:
                    status["issues"].append(f"High error rate in {name}")
                if svc.avg_response_time > 30:
                    status["issues"].append(f"Slow response time in {name}")

        if status["issues"]:
            if len(status["issues"]) > 3:
                status["overall"] = "critical"
            else:
                status["overall"] = "degraded"

        return status

    def get_full_report(self) -> Dict:
        return {
            "system": self.get_system_summary(),
            "services": self.get_service_summary(),
            "companion": self.get_companion_summary(),
            "health": self.get_health_status(),
            "generated_at": datetime.utcnow().isoformat(),
        }

    def export_metrics(self, filepath: str):
        report = self.get_full_report()
        report["history"] = [
            {
                "timestamp": m.timestamp.isoformat(),
                "cpu": m.cpu_percent,
                "memory": m.memory_percent,
                "gpu": m.gpu_percent,
            }
            for m in self.system_history[-100:]
        ]

        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)


monitor_service = MonitorService()


if __name__ == "__main__":
    async def test_monitor():
        print("Testing Monitor Service...")

        metrics = monitor_service.collect_system_metrics()
        print(f"\nSystem Metrics:")
        print(f"  CPU: {metrics.cpu_percent}%")
        print(f"  Memory: {metrics.memory_percent}% ({metrics.memory_used_gb:.1f}GB used)")
        if metrics.gpu_percent is not None:
            print(f"  GPU: {metrics.gpu_percent}% ({metrics.gpu_memory_used_gb:.1f}GB VRAM)")
        print(f"  Disk: {metrics.disk_percent}%")

        print("\nHealth Status:")
        health = monitor_service.get_health_status()
        print(f"  Overall: {health['overall']}")
        if health['issues']:
            print(f"  Issues: {', '.join(health['issues'])}")

    asyncio.run(test_monitor())
