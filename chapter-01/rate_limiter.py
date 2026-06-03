# utils/rate_limiter.py
import asyncio
from datetime import datetime, timedelta
from collections import deque

class RateLimiter:
    """Simple rate limiter using token bucket algorithm."""
    
    def __init__(self, max_requests: int, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = deque()
    
    async def acquire(self):
        """Wait until a request slot is available."""
        now = datetime.now()
        
        # Remove expired timestamps
        while self.requests and now - self.requests[0] > timedelta(seconds=self.window_seconds):
            self.requests.popleft()
        
        if len(self.requests) >= self.max_requests:
            # Calculate wait time
            wait_time = (self.requests[0] + timedelta(seconds=self.window_seconds) - now).total_seconds()
            if wait_time > 0:
                await asyncio.sleep(wait_time)
        
        self.requests.append(now)
