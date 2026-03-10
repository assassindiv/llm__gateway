from fastapi import APIRouter, Depends, HTTPException
from middleware.auth import verify_api_key
from middleware.rate_limiter import rate_limit
from schemas import ChatRequest
from services.llm_service import generate_response
from model_registry import MODEL_REGISTRY
import database

router = APIRouter()

@router.post("/chat")
async def chat(
    request: ChatRequest,
    _: None = Depends(verify_api_key),
    __: None = Depends(rate_limit),
):

    model_info = MODEL_REGISTRY[request.model]
    provider = model_info["provider"]
    messages = [m.model_dump() for m in request.messages]
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

    return {
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