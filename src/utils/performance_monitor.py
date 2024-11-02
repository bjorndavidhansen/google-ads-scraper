# src/utils/performance_monitor.py
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Deque, Dict, Optional
import statistics
import time

@dataclass
class PerformanceStats:
    """Container for performance statistics"""
    avg_time: float = 0.0
    min_time: float = 0.0
    max_time: float = 0.0
    success_rate: float = 0.0
    total_requests: int = 0
    successful_requests: int = 0
    requests_per_minute: float = 0.0
    start_time: datetime = field(default_factory=datetime.now)

class PerformanceMonitor:
    """Monitor and track scraping performance metrics"""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.scrape_times: Deque[float] = deque(maxlen=window_size)
        self.success_history: Deque[bool] = deque(maxlen=window_size)
        self.start_time = datetime.now()
        self.total_requests = 0
        self.successful_requests = 0
        self._last_stats: Optional[PerformanceStats] = None

    def add_scrape(self, duration: float, success: bool) -> None:
        """Record a scraping operation"""
        self.scrape_times.append(duration)
        self.success_history.append(success)
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        self._last_stats = None  # Invalidate cached stats

    def get_stats(self) -> PerformanceStats:
        """Calculate current performance statistics"""
        if self._last_stats:
            return self._last_stats

        if not self.scrape_times:
            return PerformanceStats()

        elapsed = (datetime.now() - self.start_time).total_seconds() / 60
        stats = PerformanceStats(
            avg_time=statistics.mean(self.scrape_times),
            min_time=min(self.scrape_times),
            max_time=max(self.scrape_times),
            success_rate=sum(self.success_history) / len(self.success_history),
            total_requests=self.total_requests,
            successful_requests=self.successful_requests,
            requests_per_minute=self.total_requests / max(1, elapsed),
            start_time=self.start_time
        )
        self._last_stats = stats
        return stats

    def get_stats_dict(self) -> Dict:
        """Get statistics as dictionary"""
        stats = self.get_stats()
        return {
            'avg_time': round(stats.avg_time, 2),
            'min_time': round(stats.min_time, 2),
            'max_time': round(stats.max_time, 2),
            'success_rate': round(stats.success_rate * 100, 1),
            'total_requests': stats.total_requests,
            'successful_requests': stats.successful_requests,
            'requests_per_minute': round(stats.requests_per_minute, 2),
            'uptime_minutes': round(
                (datetime.now() - stats.start_time).total_seconds() / 60, 
                1
            )
        }

    def reset(self) -> None:
        """Reset all metrics"""
        self.scrape_times.clear()
        self.success_history.clear()
        self.start_time = datetime.now()
        self.total_requests = 0
        self.successful_requests = 0
        self._last_stats = None