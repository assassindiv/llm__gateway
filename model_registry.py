# model_registry.py

MODEL_REGISTRY = {
    # Groq models
    "llama-3.3-70b-versatile": {
        "provider": "groq",
        "input_per_token":  0.59 / 1_000_000,
        "output_per_token": 0.79 / 1_000_000,
    },
    "llama-3.1-8b-instant": {
        "provider": "groq",
        "input_per_token":  0.05 / 1_000_000,
        "output_per_token": 0.08 / 1_000_000,
    },
    # OpenAI models
    "gpt-4o-mini": {
        "provider": "openai",
        "input_per_token":  0.15 / 1_000_000,
        "output_per_token": 0.60 / 1_000_000,
    },
    "gpt-4o": {
        "provider": "openai",
        "input_per_token":  2.50 / 1_000_000,
        "output_per_token": 10.00 / 1_000_000,
    },
    # Anthropic models
    "claude-3-5-haiku-20241022": {
        "provider": "anthropic",
        "input_per_token":  0.80 / 1_000_000,
        "output_per_token": 4.00 / 1_000_000,
    },
    "claude-3-5-sonnet-20241022": {
        "provider": "anthropic",
        "input_per_token":  3.00 / 1_000_000,
        "output_per_token": 15.00 / 1_000_000,
    },
}