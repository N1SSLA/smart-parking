from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api import test, auth, spots, bookings
from app.db import engine, Base
from app.models import User, Spot, Booking 

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="Smart Parking API",
    version="0.1.0",
    description="API для системы бронирования парковочных мест",
    lifespan=lifespan 
)

app.include_router(test.router, prefix="/api/v1/test", tags=["test"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(spots.router, prefix="/api/v1/spots", tags=["spots"])
app.include_router(bookings.router, prefix="/api/v1/bookings", tags=["bookings"])

@app.get("/health")
async def health():
    return {"status": "ok"}