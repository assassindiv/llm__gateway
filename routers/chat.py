from fastapi import APIRouter, Depends , HTTPException
from middleware.auth import verify_api_key
from schemas import ChatRequest
from services.llm_service import generate_response
import database
from middleware.rate_limiter import rate_limit
from model_registry import MODEL_PRICE


router = APIRouter()

@router.post("/chat")
async def chat(request: ChatRequest,
               _: None=Depends(verify_api_key),
               __:None=Depends(rate_limit)
               ):
    
    pricing=MODEL_PRICE.get(request.model,0)
    if not pricing:
        raise HTTPException(status_code=400, detail="Model not supported")

    response = await generate_response(request.message, request.model)

    reply = response.choices[0].message.content
    prompt_tokens = response.usage.prompt_tokens
    completion_tokens = response.usage.completion_tokens
    total_tokens = response.usage.total_tokens

    prompt_cost = prompt_tokens * pricing["input_per_token"]
    completion_cost = completion_tokens * pricing["output_per_token"]
    cost = prompt_cost + completion_cost

    async with database.pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO requests
            (message, model, response, prompt_tokens, completion_tokens, total_tokens, cost)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
            request.message,
            request.model,
            reply,
            prompt_tokens,
            completion_tokens,
            total_tokens,
            cost
        )

    return {
        "response": reply,
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "cost": cost
        }
    }