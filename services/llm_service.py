# services/llm_service.py
from openai import AsyncOpenAI
from pydantic import BaseModel,field_validator
import anthropic
from config import GROQ_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY

# One client per provider — created once at startup
_groq_client = AsyncOpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)
_openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
_anthropic_client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)


async def generate_response(messages: list[dict], model: str, provider: str):
    if provider in ("groq", "openai"):
        return await _call_openai_compatible(_groq_client if provider == "groq" else _openai_client,
                                              messages, model)
    elif provider == "anthropic":
        return await _call_anthropic(messages, model)
    else:
        raise ValueError(f"Unknown provider: {provider}")


async def _call_openai_compatible(client, messages: list[dict], model: str):
    
    response = await client.chat.completions.create(
        model=model,
        messages=messages
    )
    # Normalize to a common shape
    return {
        "reply": response.choices[0].message.content,
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens,
    }


async def _call_anthropic(messages: list[dict], model: str):
    system_prompt = None
    filtered = []
    for m in messages:
        if m["role"] == "system":
            system_prompt = m["content"]
        else:
            filtered.append(m)

    kwargs = dict(model=model, max_tokens=1024, messages=filtered)
    if system_prompt:
        kwargs["system"] = system_prompt
        
    response = await _anthropic_client.messages.create(**kwargs)
    return {
        "reply": response.content[0].text,
        "prompt_tokens": response.usage.input_tokens,
        "completion_tokens": response.usage.output_tokens,
        "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
    }