import hashlib
import json
import time

from fastapi import APIRouter, Depends, HTTPException, Response
from middleware.auth import verify_api_key
from middleware.rate_limiter import rate_limit
from schemas import ChatRequest
from services.llm_service import generate_response
from model_registry import MODEL_REGISTRY
from redis_client import redis_client
from config import CACHE_TTL_SECONDS
import database

router = APIRouter()
_fallback_cache: dict[str, tuple[float, dict]] = {}

@router.post("/chat")
async def chat(
    request: ChatRequest,
    response: Response,
    _: None = Depends(verify_api_key),
    __: None = Depends(rate_limit),
):

    model_info = MODEL_REGISTRY[request.model]
    provider = model_info["provider"]
    messages = [m.model_dump() for m in request.messages]

    cache_source = {
        "model": request.model,
        "messages": messages,
    }
    cache_key = "chat_cache:" + hashlib.sha256(
        json.dumps(cache_source, sort_keys=True).encode("utf-8")
    ).hexdigest()

    now = time.time()
    fallback_hit = _fallback_cache.get(cache_key)
    if fallback_hit and fallback_hit[0] > now:
        response.headers["X-Cache"] = "HIT-MEM"
        return fallback_hit[1]

    try:
        cached_payload = await redis_client.get(cache_key)
        if cached_payload:
            response.headers["X-Cache"] = "HIT-REDIS"
            return json.loads(cached_payload)
    except Exception:
        # Keep request fast even if Redis is temporarily unavailable.
        pass

    try:
        result = await generate_response(messages, request.model, provider)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Provider error: {str(e)}")

    # 3. Cost calculation 
    cost = (
        result["prompt_tokens"] * model_info["input_per_token"] +
        result["completion_tokens"] * model_info["output_per_token"]
    )
    last_user_message = next(
        (m["content"] for m in reversed(messages) if m["role"] == "user"),
        ""
    )


    # 4. DB insert
    async with database.pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO requests
            (message, model, provider, response, prompt_tokens, completion_tokens, total_tokens, cost)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """,
            last_user_message,
            request.model,
            provider,               
            result["reply"],       
            result["prompt_tokens"],
            result["completion_tokens"],
            result["total_tokens"],
            cost,
        )

    response_payload = {
        "response": result["reply"],
        "model": request.model,     
        "provider": provider,     
        "usage": {
            "prompt_tokens": result["prompt_tokens"],
            "completion_tokens": result["completion_tokens"],
            "total_tokens": result["total_tokens"],
            "cost_usd": round(cost, 8),
        }
    }

    try:
        await redis_client.set(cache_key, json.dumps(response_payload), ex=CACHE_TTL_SECONDS)
    except Exception:
        pass

    _fallback_cache[cache_key] = (now + CACHE_TTL_SECONDS, response_payload)
    response.headers["X-Cache"] = "MISS"

    return response_payload