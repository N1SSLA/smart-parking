from fastapi import FastAPI

from app.api import test

app = FastAPI(
    title="Smart Parking API",
    version="0.1.0",
    description="API для системы бронирования парковочных мест",
)

app.include_router(test.router, prefix="/api/v1/test", tags=["test"])

@app.get("/health")
async def health():
    return {"status": "ok"}