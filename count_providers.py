from model_registry import MODEL_REGISTRY


provider_names = {info["provider"] for info in MODEL_REGISTRY.values()}

print(f"Models supported: {len(MODEL_REGISTRY)}")
print(f"Providers supported: {len(provider_names)}")
print(f"Provider list: {', '.join(sorted(provider_names))}")
