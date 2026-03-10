from pydantic import BaseModel,field_validator
from model_registry import MODEL_REGISTRY
from typing import Literal

class Message(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str

class ChatRequest(BaseModel):
    messages: list[Message]
    model: str

    @field_validator('model')
    @classmethod
    def model_support(cls,v):
        if v not in MODEL_REGISTRY:
            supported_models = list(MODEL_REGISTRY.keys())
            raise ValueError(f"Model '{v}' is not supported. Available models: {supported_models}")
        return v