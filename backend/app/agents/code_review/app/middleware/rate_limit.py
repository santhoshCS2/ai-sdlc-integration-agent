from fastapi import Request, HTTPException
from collections import defaultdict
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, requests_per_minute=10):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
    
    async def check_rate_limit(self, request: Request):
        client_ip = request.client.host if request.client else "unknown"
        now = datetime.now()
        
        # Clean old requests
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if now - req_time < timedelta(minutes=1)
        ]
        
        # Check limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")
        
        # Add current request
        self.requests[client_ip].append(now)

rate_limiter = RateLimiter(requests_per_minute=10)
