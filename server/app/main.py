from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api import test, auth, spots, bookings, device
from app.db import engine, Base, SessionLocal
from app.models import User, Spot, Booking 
from app.models.spot import Spot

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with SessionLocal() as db:
        existing = await db.scalar(select(Spot.id).limit(1))
        if existing is None:
            db.add_all([Spot(name=n) for n in ("A1", "A2", "A3", "A4")])
            await db.commit()
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
app.include_router(device.router, prefix="/device/v1/gate", tags=["device"])

@app.get("/health")
async def health():
    return {"status": "ok"}