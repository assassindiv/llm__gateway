from fastapi import FastAPI
from routers.chat import router as chat_router
from database import init_db, close_db
from model_registry import MODEL_REGISTRY

app = FastAPI()

@app.on_event("startup")
async def startup():
    await init_db()

@app.on_event("shutdown")
async def shutdown():
    await close_db()

@app.get("/")
def hello():
    return {"message": "hello"}

@app.get("/models")
def list_models():
    return {
        model:{"provider": info["provider"]} 
        for model, info in MODEL_REGISTRY.items()
    }

app.include_router(chat_router)