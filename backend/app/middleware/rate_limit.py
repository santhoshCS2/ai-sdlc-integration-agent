from fastapi import Request, HTTPException
import time

class RateLimiter:
    def __init__(self):
        self.requests = {}

    async def check_rate_limit(self, request: Request):
        # Very simple rate limiter for demonstration
        # In production, use Redis or similar
        client_ip = request.client.host
        current_time = time.time()
        
        if client_ip in self.requests:
            last_request_time = self.requests[client_ip]
            if current_time - last_request_time < 1.0: # 1 request per second
                raise HTTPException(status_code=429, detail="Too many requests")
        
        self.requests[client_ip] = current_time

rate_limiter = RateLimiter()
