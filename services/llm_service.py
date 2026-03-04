from openai import AsyncOpenAI
from config import GROQ_API_KEY

client = AsyncOpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

async def generate_response(message: str, model: str):
    response = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": message}
        ]
    )
    return response