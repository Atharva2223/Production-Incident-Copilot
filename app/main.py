from fastapi import FastAPI

from app.api.routes import router


app = FastAPI(
    title="Production Incident Copilot API",
    description="AI-powered incident analysis over production logs",
    version="1.0.0",
)

app.include_router(router)