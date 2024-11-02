# src/utils/rate_limiter.py
import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

@dataclass
class RateLimiterConfig:
    """Configuration for rate limiting"""
    max_requests: int = field(default=10)
    time_window: int = field(default=60)
    min_delay: float = field(default=0.1)
    burst_size: int = field(default=3)

    def __post_init__(self):
        """Validate configuration values"""
        if self.max_requests <= 0:
            raise ValueError("max_requests must be positive")
        if self.time_window <= 0:
            raise ValueError("time_window must be positive")
        if self.min_delay < 0:
            raise ValueError("min_delay cannot be negative")
        if self.burst_size < 0:
            raise ValueError("burst_size cannot be negative")

class RateLimiter:
    """Async rate limiter using token bucket algorithm"""

    def __init__(self, config: RateLimiterConfig):
        self.config = config
        self.tokens = float(config.max_requests)  # Use float for better precision
        self.last_update = time.monotonic()
        self.lock = asyncio.Lock()
        self.request_history: Dict[str, float] = {}  # Use monotonic time
        self._closed = False

    async def acquire(self, key: Optional[str] = None) -> None:
        """Acquire a token for making a request"""
        if self._closed:
            raise RuntimeError("Rate limiter is closed")

        try:
            async with self.lock:
                await self._refill_tokens()
                
                while self.tokens <= 0:
                    delay = self._calculate_delay()
                    await asyncio.sleep(delay)
                    await self._refill_tokens()
                
                self.tokens -= 1
                if key is not None:
                    self.request_history[key] = time.monotonic()
                    
        except Exception as e:
            logger.error(f"Error acquiring token: {str(e)}")
            raise

    async def _refill_tokens(self) -> None:
        """Refill tokens based on elapsed time"""
        try:
            now = time.monotonic()
            time_passed = now - self.last_update
            
            token_increment = time_passed * (
                self.config.max_requests / self.config.time_window
            )
            
            self.tokens = min(
                float(self.config.max_requests + self.config.burst_size),
                self.tokens + token_increment
            )
            self.last_update = now
            
        except Exception as e:
            logger.error(f"Error refilling tokens: {str(e)}")
            raise

    def _calculate_delay(self) -> float:
        """Calculate delay needed before next token"""
        try:
            tokens_needed = 1
            token_generation_rate = self.config.max_requests / self.config.time_window
            delay = max(
                tokens_needed / token_generation_rate,
                self.config.min_delay
            )
            return delay
            
        except Exception as e:
            logger.error(f"Error calculating delay: {str(e)}")
            raise

    def get_request_count(self, window_seconds: Optional[int] = None) -> int:
        """Get number of requests in time window"""
        try:
            if not window_seconds:
                window_seconds = self.config.time_window
                
            now = time.monotonic()
            count = sum(
                1 for timestamp in self.request_history.values()
                if (now - timestamp) <= window_seconds
            )
            return count
            
        except Exception as e:
            logger.error(f"Error getting request count: {str(e)}")
            raise

    async def __aenter__(self):
        """Async context manager entry"""
        if self._closed:
            raise RuntimeError("Cannot enter closed rate limiter")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

    async def close(self) -> None:
        """Close rate limiter and cleanup resources"""
        if not self._closed:
            try:
                async with self.lock:
                    self.cleanup_history()
                    self._closed = True
            except Exception as e:
                logger.error(f"Error closing rate limiter: {str(e)}")
                raise

    def cleanup_history(self, max_age: int = 3600) -> None:
        """Clean up old request history entries"""
        try:
            now = time.monotonic()
            self.request_history = {
                k: v for k, v in self.request_history.items()
                if (now - v) <= max_age
            }
        except Exception as e:
            logger.error(f"Error cleaning history: {str(e)}")
            raise