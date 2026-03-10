from openai import AsyncOpenAI
from config import GROQ_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY
import anthropic


client = AsyncOpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)
openai_client = AsyncOpenAI(
    api_key=OPENAI_API_KEY)

anthropic_client = anthropic.AsyncAnthropic(
    api_key=ANTHROPIC_API_KEY)

async def generate_response(messages: list, model: str, provider: str):
    if provider == "openai":
        return await _call_openai_compatible(openai_client, messages, model) 
    elif provider == "groq":
        return await _call_openai_compatible(client, messages, model)
    elif provider == "anthropic":
        return await _call_anthropic(messages, model)
    else:
        raise ValueError(f"Invalid provider: {provider}")




async def _call_openai_compatible(client, messages: list, model: str):
    """Groq and OpenAI share the same SDK interface."""
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

async def _call_anthropic(messages: list, model: str):
    """Anthropic has a different SDK — normalize the response."""
    response = await anthropic_client.messages.create(
        model=model,
        max_tokens=1024,
        messages=messages
    )
    return {
        "reply": response.content[0].text,
        "prompt_tokens": response.usage.input_tokens,
        "completion_tokens": response.usage.output_tokens,
        "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
    }
