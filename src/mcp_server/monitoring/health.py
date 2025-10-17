"""
Health Check System for Regen Python MCP Server
Provides comprehensive health monitoring including Regen Network connectivity,
dependency status, and performance metrics.
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import logging

import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class HealthStatus(BaseModel):
    """Health status model for health check responses."""
    status: str  # "healthy", "degraded", "unhealthy"
    timestamp: str
    version: str
    uptime_seconds: float
    dependencies: Dict[str, Dict[str, Any]]
    performance_metrics: Dict[str, Any]
    error_details: Optional[List[str]] = None


@dataclass
class DependencyCheck:
    """Represents a single dependency health check."""
    name: str
    status: str  # "healthy", "unhealthy", "timeout"
    response_time_ms: Optional[float] = None
    error_message: Optional[str] = None
    last_check: Optional[datetime] = None


class HealthChecker:
    """
    Comprehensive health check system for the Regen Python MCP server.
    
    Features:
    - Regen Network connectivity validation
    - Performance metrics reporting
    - Dependency status monitoring
    - Periodic health checks with caching
    """

    def __init__(
        self, 
        regen_endpoints: Optional[List[str]] = None,
        check_interval: int = 30,
        timeout: float = 5.0
    ):
        """
        Initialize the health checker.
        
        Args:
            regen_endpoints: List of Regen Network endpoints to check
            check_interval: Interval between health checks in seconds
            timeout: Timeout for health check requests in seconds
        """
        self.regen_endpoints = regen_endpoints or [
            "https://regen-api.polkachu.com",
            "https://regen.api.m.stavr.tech:443",
            "https://regen-rpc.polkachu.com"
        ]
        self.check_interval = check_interval
        self.timeout = timeout
        self.start_time = time.time()
        self.version = "1.0.0"
        
        # Health state tracking
        self.last_health_check: Optional[HealthStatus] = None
        self.dependency_status: Dict[str, DependencyCheck] = {}
        self.performance_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0,
            "last_error": None,
            "error_count_24h": 0
        }
        
        # Background task for periodic checks
        self._check_task: Optional[asyncio.Task] = None
        self._running = False

    async def start_monitoring(self) -> None:
        """Start background health monitoring."""
        if self._running:
            return
            
        self._running = True
        self._check_task = asyncio.create_task(self._periodic_health_check())
        logger.info("Health monitoring started")

    async def stop_monitoring(self) -> None:
        """Stop background health monitoring."""
        self._running = False
        if self._check_task:
            self._check_task.cancel()
            try:
                await self._check_task
            except asyncio.CancelledError:
                pass
        logger.info("Health monitoring stopped")

    async def get_health_status(self, force_check: bool = False) -> HealthStatus:
        """
        Get current health status.
        
        Args:
            force_check: If True, perform fresh health check instead of using cached result
            
        Returns:
            HealthStatus object with comprehensive health information
        """
        # Use cached result if recent and not forcing check
        if (not force_check and 
            self.last_health_check and 
            (datetime.utcnow() - datetime.fromisoformat(self.last_health_check.timestamp.replace('Z', '+00:00'))) 
            < timedelta(seconds=self.check_interval)):
            return self.last_health_check

        # Perform fresh health check
        await self._perform_health_check()
        return self.last_health_check

    async def _perform_health_check(self) -> None:
        """Perform a comprehensive health check."""
        start_time = time.time()
        
        try:
            # Check Regen Network endpoints
            await self._check_regen_endpoints()
            
            # Determine overall status
            overall_status = self._calculate_overall_status()
            
            # Update performance metrics
            check_duration = time.time() - start_time
            self._update_performance_metrics(check_duration, success=True)
            
            # Collect error details if any
            error_details = self._collect_error_details()
            
            # Create health status
            self.last_health_check = HealthStatus(
                status=overall_status,
                timestamp=datetime.utcnow().isoformat() + "Z",
                version=self.version,
                uptime_seconds=time.time() - self.start_time,
                dependencies=self._format_dependency_status(),
                performance_metrics=self.performance_metrics.copy(),
                error_details=error_details if error_details else None
            )
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            self._update_performance_metrics(time.time() - start_time, success=False)
            
            # Create unhealthy status
            self.last_health_check = HealthStatus(
                status="unhealthy",
                timestamp=datetime.utcnow().isoformat() + "Z",
                version=self.version,
                uptime_seconds=time.time() - self.start_time,
                dependencies={},
                performance_metrics=self.performance_metrics.copy(),
                error_details=[f"Health check system failure: {str(e)}"]
            )

    async def _check_regen_endpoints(self) -> None:
        """Check connectivity to all Regen Network endpoints."""
        tasks = []
        for endpoint in self.regen_endpoints:
            task = asyncio.create_task(self._check_single_endpoint(endpoint))
            tasks.append(task)
        
        # Wait for all checks to complete
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _check_single_endpoint(self, endpoint: str) -> None:
        """Check a single Regen Network endpoint."""
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Try to get node info or health endpoint
                health_url = f"{endpoint}/health" if "/rpc" not in endpoint else f"{endpoint}/health"
                response = await client.get(health_url)
                
                response_time = (time.time() - start_time) * 1000  # Convert to ms
                
                if response.status_code == 200:
                    self.dependency_status[endpoint] = DependencyCheck(
                        name=endpoint,
                        status="healthy",
                        response_time_ms=response_time,
                        last_check=datetime.utcnow()
                    )
                else:
                    self.dependency_status[endpoint] = DependencyCheck(
                        name=endpoint,
                        status="unhealthy",
                        response_time_ms=response_time,
                        error_message=f"HTTP {response.status_code}",
                        last_check=datetime.utcnow()
                    )
                    
        except asyncio.TimeoutError:
            self.dependency_status[endpoint] = DependencyCheck(
                name=endpoint,
                status="timeout",
                error_message=f"Timeout after {self.timeout}s",
                last_check=datetime.utcnow()
            )
        except Exception as e:
            self.dependency_status[endpoint] = DependencyCheck(
                name=endpoint,
                status="unhealthy",
                error_message=str(e),
                last_check=datetime.utcnow()
            )

    def _calculate_overall_status(self) -> str:
        """Calculate overall health status based on dependencies."""
        if not self.dependency_status:
            return "unhealthy"
        
        healthy_count = sum(1 for dep in self.dependency_status.values() if dep.status == "healthy")
        total_count = len(self.dependency_status)
        
        # At least 50% of endpoints must be healthy
        if healthy_count >= total_count * 0.5:
            if healthy_count == total_count:
                return "healthy"
            else:
                return "degraded"
        else:
            return "unhealthy"

    def _format_dependency_status(self) -> Dict[str, Dict[str, Any]]:
        """Format dependency status for health response."""
        formatted = {}
        for endpoint, check in self.dependency_status.items():
            formatted[endpoint] = {
                "status": check.status,
                "response_time_ms": check.response_time_ms,
                "error_message": check.error_message,
                "last_check": check.last_check.isoformat() + "Z" if check.last_check else None
            }
        return formatted

    def _collect_error_details(self) -> List[str]:
        """Collect error details from unhealthy dependencies."""
        errors = []
        for endpoint, check in self.dependency_status.items():
            if check.status != "healthy" and check.error_message:
                errors.append(f"{endpoint}: {check.error_message}")
        return errors

    def _update_performance_metrics(self, duration: float, success: bool) -> None:
        """Update performance metrics based on health check result."""
        self.performance_metrics["total_requests"] += 1
        
        if success:
            self.performance_metrics["successful_requests"] += 1
        else:
            self.performance_metrics["failed_requests"] += 1
            self.performance_metrics["last_error"] = datetime.utcnow().isoformat() + "Z"
        
        # Update average response time (simple moving average)
        current_avg = self.performance_metrics["average_response_time"]
        total_requests = self.performance_metrics["total_requests"]
        new_avg = ((current_avg * (total_requests - 1)) + duration) / total_requests
        self.performance_metrics["average_response_time"] = new_avg

    async def _periodic_health_check(self) -> None:
        """Background task for periodic health checks."""
        while self._running:
            try:
                await self._perform_health_check()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Periodic health check failed: {e}")
                await asyncio.sleep(self.check_interval)

    def update_tool_metrics(self, tool_name: str, success: bool, duration: float) -> None:
        """
        Update metrics for individual tool usage.
        
        Args:
            tool_name: Name of the tool that was executed
            success: Whether the tool execution was successful
            duration: Execution duration in seconds
        """
        # This can be extended to track per-tool metrics
        self._update_performance_metrics(duration, success)

    async def validate_regen_connectivity(self) -> bool:
        """
        Quick connectivity validation for Regen Network.
        
        Returns:
            True if at least one endpoint is reachable
        """
        await self._check_regen_endpoints()
        healthy_count = sum(1 for dep in self.dependency_status.values() if dep.status == "healthy")
        return healthy_count > 0