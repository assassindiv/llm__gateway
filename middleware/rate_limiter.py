from fastapi import HTTPException,Security
from fastapi.security import APIKeyHeader
import redis
import redis_client

api_key_header=APIKeyHeader(name="x-api-key",auto_error=False)
RATE_LIMIT=30

async def rate_limit(api_key: str = Security(api_key_header)):
    if not api_key: 
        raise HTTPException(status_code=401, detail="API key missing")
    key=f"rate_limit:{api_key}"
    current= await redis_client.redis_client.incr(key)

    if current==1:
        await redis_client.redis_client.expire(key,60)
    
    if current>RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")