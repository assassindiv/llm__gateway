# middleware/auth.py
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
import database
import redis_client

api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    if not api_key:
        raise HTTPException(status_code=401, detail="API key missing")

    # Check Redis cache first
    redis_key = f"apikey_valid:{api_key}"
    cached = await redis_client.redis_client.get(redis_key)
    if cached:
        return  # ✅ skip DB entirely

    # Only hit DB if not cached
    async with database.pool.acquire() as conn:
        result = await conn.fetchrow(
            "SELECT id FROM api_keys WHERE key=$1", api_key
        )

    if not result:
        raise HTTPException(status_code=403, detail="Invalid API key")

    # Cache valid key for 5 minutes
    await redis_client.redis_client.set(redis_key, "1", ex=300)