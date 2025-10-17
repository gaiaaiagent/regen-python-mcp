"""
Performance Monitoring and Metrics Collection for Regen Python MCP Server
Tracks tool usage statistics, response times, error rates, and resource usage.
"""

import time
import asyncio
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, DefaultDict
from dataclasses import dataclass, field
from collections import defaultdict, deque
import logging
import psutil

logger = logging.getLogger(__name__)


@dataclass
class ToolMetrics:
    """Metrics for individual tool execution."""
    tool_name: str
    call_count: int = 0
    success_count: int = 0
    error_count: int = 0
    total_duration: float = 0.0
    min_duration: float = float('inf')
    max_duration: float = 0.0
    last_called: Optional[datetime] = None
    error_rate: float = 0.0
    avg_duration: float = 0.0
    recent_calls: deque = field(default_factory=lambda: deque(maxlen=100))


@dataclass
class SystemMetrics:
    """System resource usage metrics."""
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    disk_usage_percent: float
    network_connections: int
    thread_count: int
    timestamp: datetime


@dataclass
class PerformanceSnapshot:
    """Performance snapshot at a point in time."""
    timestamp: datetime
    active_requests: int
    requests_per_second: float
    avg_response_time: float
    error_rate: float
    memory_usage_mb: float
    cpu_usage_percent: float


class MetricsCollector:
    """
    Comprehensive metrics collection system for performance monitoring.
    
    Features:
    - Tool usage statistics collection
    - Response time tracking across all tools
    - Error rate monitoring and alerting
    - Memory and resource usage profiling
    - Performance trend analysis
    """

    def __init__(
        self,
        enable_system_metrics: bool = True,
        metrics_retention_hours: int = 24,
        snapshot_interval_seconds: int = 60
    ):
        """
        Initialize the metrics collector.
        
        Args:
            enable_system_metrics: Whether to collect system resource metrics
            metrics_retention_hours: How long to retain detailed metrics
            snapshot_interval_seconds: Interval for performance snapshots
        """
        self.enable_system_metrics = enable_system_metrics
        self.metrics_retention_hours = metrics_retention_hours
        self.snapshot_interval_seconds = snapshot_interval_seconds
        
        # Tool-specific metrics
        self.tool_metrics: Dict[str, ToolMetrics] = {}
        
        # Global metrics
        self.global_metrics = {
            "server_start_time": datetime.utcnow(),
            "total_requests": 0,
            "total_errors": 0,
            "total_duration": 0.0,
            "concurrent_requests": 0,
            "peak_concurrent_requests": 0,
            "requests_per_second": 0.0
        }
        
        # Time-series data
        self.performance_snapshots: deque = deque(maxlen=1440)  # 24 hours at 1min intervals
        self.error_log: deque = deque(maxlen=1000)  # Recent errors
        self.system_metrics_history: deque = deque(maxlen=1440)  # 24 hours of system metrics
        
        # Request tracking
        self.active_requests: Dict[str, float] = {}  # request_id -> start_time
        self.recent_response_times: deque = deque(maxlen=1000)  # Recent response times
        
        # Background monitoring
        self._monitoring_task: Optional[asyncio.Task] = None
        self._running = False
        self._lock = threading.Lock()

    async def start_monitoring(self) -> None:
        """Start background metrics collection."""
        if self._running:
            return
            
        self._running = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Metrics collection started")

    async def stop_monitoring(self) -> None:
        """Stop background metrics collection."""
        self._running = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        logger.info("Metrics collection stopped")

    def record_tool_call_start(self, tool_name: str, request_id: str) -> None:
        """
        Record the start of a tool call.
        
        Args:
            tool_name: Name of the tool being called
            request_id: Unique identifier for this request
        """
        with self._lock:
            current_time = time.time()
            self.active_requests[request_id] = current_time
            
            # Update concurrent request metrics
            concurrent_count = len(self.active_requests)
            self.global_metrics["concurrent_requests"] = concurrent_count
            if concurrent_count > self.global_metrics["peak_concurrent_requests"]:
                self.global_metrics["peak_concurrent_requests"] = concurrent_count
            
            # Initialize tool metrics if not exists
            if tool_name not in self.tool_metrics:
                self.tool_metrics[tool_name] = ToolMetrics(tool_name=tool_name)

    def record_tool_call_end(
        self, 
        tool_name: str, 
        request_id: str, 
        success: bool, 
        error_message: Optional[str] = None
    ) -> float:
        """
        Record the completion of a tool call.
        
        Args:
            tool_name: Name of the tool that was called
            request_id: Unique identifier for this request
            success: Whether the call was successful
            error_message: Error message if the call failed
            
        Returns:
            Duration of the call in seconds
        """
        with self._lock:
            if request_id not in self.active_requests:
                logger.warning(f"Request {request_id} not found in active requests")
                return 0.0
            
            # Calculate duration
            start_time = self.active_requests.pop(request_id)
            duration = time.time() - start_time
            
            # Update global metrics
            self.global_metrics["total_requests"] += 1
            self.global_metrics["total_duration"] += duration
            self.global_metrics["concurrent_requests"] = len(self.active_requests)
            
            if not success:
                self.global_metrics["total_errors"] += 1
                self._record_error(tool_name, error_message or "Unknown error", duration)
            
            # Update tool-specific metrics
            tool_metric = self.tool_metrics[tool_name]
            tool_metric.call_count += 1
            tool_metric.total_duration += duration
            tool_metric.last_called = datetime.utcnow()
            
            if success:
                tool_metric.success_count += 1
            else:
                tool_metric.error_count += 1
            
            # Update duration statistics
            tool_metric.min_duration = min(tool_metric.min_duration, duration)
            tool_metric.max_duration = max(tool_metric.max_duration, duration)
            tool_metric.avg_duration = tool_metric.total_duration / tool_metric.call_count
            tool_metric.error_rate = tool_metric.error_count / tool_metric.call_count
            
            # Record recent call
            tool_metric.recent_calls.append({
                "timestamp": datetime.utcnow(),
                "duration": duration,
                "success": success
            })
            
            # Add to recent response times
            self.recent_response_times.append(duration)
            
            # Update requests per second calculation
            self._update_requests_per_second()
            
            return duration

    def _record_error(self, tool_name: str, error_message: str, duration: float) -> None:
        """Record an error occurrence."""
        error_record = {
            "timestamp": datetime.utcnow(),
            "tool_name": tool_name,
            "error_message": error_message,
            "duration": duration
        }
        self.error_log.append(error_record)

    def _update_requests_per_second(self) -> None:
        """Calculate current requests per second."""
        if len(self.recent_response_times) < 2:
            self.global_metrics["requests_per_second"] = 0.0
            return
        
        # Calculate based on recent calls (last minute)
        now = datetime.utcnow()
        minute_ago = now - timedelta(minutes=1)
        
        recent_count = 0
        for tool_metric in self.tool_metrics.values():
            for call in tool_metric.recent_calls:
                if call["timestamp"] > minute_ago:
                    recent_count += 1
        
        self.global_metrics["requests_per_second"] = recent_count / 60.0

    async def _monitoring_loop(self) -> None:
        """Background monitoring loop for collecting snapshots."""
        while self._running:
            try:
                await self._collect_performance_snapshot()
                if self.enable_system_metrics:
                    await self._collect_system_metrics()
                await asyncio.sleep(self.snapshot_interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics monitoring loop error: {e}")
                await asyncio.sleep(self.snapshot_interval_seconds)

    async def _collect_performance_snapshot(self) -> None:
        """Collect a performance snapshot."""
        with self._lock:
            avg_response_time = (
                sum(self.recent_response_times) / len(self.recent_response_times)
                if self.recent_response_times else 0.0
            )
            
            error_rate = (
                self.global_metrics["total_errors"] / max(self.global_metrics["total_requests"], 1)
            )
            
            snapshot = PerformanceSnapshot(
                timestamp=datetime.utcnow(),
                active_requests=len(self.active_requests),
                requests_per_second=self.global_metrics["requests_per_second"],
                avg_response_time=avg_response_time,
                error_rate=error_rate,
                memory_usage_mb=0.0,  # Will be updated by system metrics
                cpu_usage_percent=0.0  # Will be updated by system metrics
            )
            
            self.performance_snapshots.append(snapshot)

    async def _collect_system_metrics(self) -> None:
        """Collect system resource metrics."""
        try:
            # Get current process
            process = psutil.Process()
            
            # Collect metrics
            memory_info = process.memory_info()
            cpu_percent = process.cpu_percent(interval=None)
            
            system_metric = SystemMetrics(
                cpu_percent=cpu_percent,
                memory_mb=memory_info.rss / 1024 / 1024,  # Convert to MB
                memory_percent=process.memory_percent(),
                disk_usage_percent=psutil.disk_usage('/').percent,
                network_connections=len(process.connections()),
                thread_count=process.num_threads(),
                timestamp=datetime.utcnow()
            )
            
            self.system_metrics_history.append(system_metric)
            
            # Update latest snapshot with system metrics
            if self.performance_snapshots:
                latest_snapshot = self.performance_snapshots[-1]
                latest_snapshot.memory_usage_mb = system_metric.memory_mb
                latest_snapshot.cpu_usage_percent = cpu_percent
                
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")

    def get_tool_metrics(self, tool_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get metrics for a specific tool or all tools.
        
        Args:
            tool_name: Optional tool name to get metrics for
            
        Returns:
            Dictionary containing tool metrics
        """
        with self._lock:
            if tool_name:
                if tool_name in self.tool_metrics:
                    metric = self.tool_metrics[tool_name]
                    return {
                        "tool_name": metric.tool_name,
                        "call_count": metric.call_count,
                        "success_count": metric.success_count,
                        "error_count": metric.error_count,
                        "error_rate": metric.error_rate,
                        "avg_duration": metric.avg_duration,
                        "min_duration": metric.min_duration if metric.min_duration != float('inf') else 0,
                        "max_duration": metric.max_duration,
                        "last_called": metric.last_called.isoformat() + "Z" if metric.last_called else None
                    }
                else:
                    return {"error": f"Tool {tool_name} not found"}
            else:
                return {
                    tool_name: {
                        "tool_name": metric.tool_name,
                        "call_count": metric.call_count,
                        "success_count": metric.success_count,
                        "error_count": metric.error_count,
                        "error_rate": metric.error_rate,
                        "avg_duration": metric.avg_duration,
                        "min_duration": metric.min_duration if metric.min_duration != float('inf') else 0,
                        "max_duration": metric.max_duration,
                        "last_called": metric.last_called.isoformat() + "Z" if metric.last_called else None
                    }
                    for tool_name, metric in self.tool_metrics.items()
                }

    def get_global_metrics(self) -> Dict[str, Any]:
        """Get global server metrics."""
        with self._lock:
            uptime = datetime.utcnow() - self.global_metrics["server_start_time"]
            
            return {
                "server_start_time": self.global_metrics["server_start_time"].isoformat() + "Z",
                "uptime_seconds": uptime.total_seconds(),
                "total_requests": self.global_metrics["total_requests"],
                "total_errors": self.global_metrics["total_errors"],
                "error_rate": (
                    self.global_metrics["total_errors"] / max(self.global_metrics["total_requests"], 1)
                ),
                "average_response_time": (
                    self.global_metrics["total_duration"] / max(self.global_metrics["total_requests"], 1)
                ),
                "concurrent_requests": self.global_metrics["concurrent_requests"],
                "peak_concurrent_requests": self.global_metrics["peak_concurrent_requests"],
                "requests_per_second": self.global_metrics["requests_per_second"]
            }

    def get_performance_trend(self, hours: int = 1) -> List[Dict[str, Any]]:
        """
        Get performance trend data for the specified time period.
        
        Args:
            hours: Number of hours of trend data to return
            
        Returns:
            List of performance snapshots
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        trend_data = []
        for snapshot in self.performance_snapshots:
            if snapshot.timestamp > cutoff_time:
                trend_data.append({
                    "timestamp": snapshot.timestamp.isoformat() + "Z",
                    "active_requests": snapshot.active_requests,
                    "requests_per_second": snapshot.requests_per_second,
                    "avg_response_time": snapshot.avg_response_time,
                    "error_rate": snapshot.error_rate,
                    "memory_usage_mb": snapshot.memory_usage_mb,
                    "cpu_usage_percent": snapshot.cpu_usage_percent
                })
        
        return trend_data

    def get_recent_errors(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent errors.
        
        Args:
            limit: Maximum number of errors to return
            
        Returns:
            List of recent error records
        """
        recent_errors = list(self.error_log)[-limit:]
        return [
            {
                "timestamp": error["timestamp"].isoformat() + "Z",
                "tool_name": error["tool_name"],
                "error_message": error["error_message"],
                "duration": error["duration"]
            }
            for error in recent_errors
        ]

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system resource metrics."""
        if not self.enable_system_metrics or not self.system_metrics_history:
            return {"error": "System metrics not available"}
        
        latest_metric = self.system_metrics_history[-1]
        return {
            "timestamp": latest_metric.timestamp.isoformat() + "Z",
            "cpu_percent": latest_metric.cpu_percent,
            "memory_mb": latest_metric.memory_mb,
            "memory_percent": latest_metric.memory_percent,
            "disk_usage_percent": latest_metric.disk_usage_percent,
            "network_connections": latest_metric.network_connections,
            "thread_count": latest_metric.thread_count
        }

    def reset_metrics(self) -> None:
        """Reset all metrics (useful for testing)."""
        with self._lock:
            self.tool_metrics.clear()
            self.global_metrics.update({
                "server_start_time": datetime.utcnow(),
                "total_requests": 0,
                "total_errors": 0,
                "total_duration": 0.0,
                "concurrent_requests": 0,
                "peak_concurrent_requests": 0,
                "requests_per_second": 0.0
            })
            self.performance_snapshots.clear()
            self.error_log.clear()
            self.system_metrics_history.clear()
            self.active_requests.clear()
            self.recent_response_times.clear()