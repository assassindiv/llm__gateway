from pydantic import BaseModel
from typing import Literal

class ChatRequest(BaseModel):
    message: str
    model: Literal["openai/gpt-oss-120b"]