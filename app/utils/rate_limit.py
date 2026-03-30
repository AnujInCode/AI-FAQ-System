from fastapi import Request, HTTPException
import time

# Simple token bucket / sliding window IP tracker for MVP
# In production, use Redis-backed rate limiting like `slowapi` or an API Gateway
RATE_LIMIT_DURATION = 60
MAX_REQUESTS = 15
ip_tracker = {}

async def check_rate_limit(request: Request):
    """Enforces basic rate limiting per IP address to prevent abuse."""
    client_ip = request.client.host if request.client else "unknown"
    current_time = time.time()
    
    if client_ip not in ip_tracker:
        ip_tracker[client_ip] = []
        
    # Remove timestamps older than RATE_LIMIT_DURATION
    ip_tracker[client_ip] = [t for t in ip_tracker[client_ip] if current_time - t < RATE_LIMIT_DURATION]
    
    if len(ip_tracker[client_ip]) >= MAX_REQUESTS:
        # Rate limit exceeded
        raise HTTPException(
            status_code=429, 
            detail="Too many requests. Please slow down and try again later."
        )
        
    ip_tracker[client_ip].append(current_time)
    return client_ip
