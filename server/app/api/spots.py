from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.spot import Spot
from app.models.booking import Booking, BookingStatus
from app.models.user import User
from app.schemas import SpotOut, SpotBookingOut
from app.deps import get_current_user

router = APIRouter()


@router.get("", response_model=list[SpotOut])
async def list_spots(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    now = datetime.now(timezone.utc)
    spots = list(await db.scalars(select(Spot).order_by(Spot.id)))
    occupied_ids = set(await db.scalars(
        select(Booking.spot_id).where(
            Booking.status == BookingStatus.in_progress,
        )
    ))
    return [
        SpotOut(id=s.id, name=s.name, is_occupied=s.id in occupied_ids)
        for s in spots
    ]


@router.get("/{spot_id}/bookings", response_model=list[SpotBookingOut])
async def spot_bookings(
    spot_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    spot = await db.get(Spot, spot_id)
    if spot is None:
        raise HTTPException(status_code=404, detail="Spot not found")

    now = datetime.now(timezone.utc)
    rows = await db.scalars(
        select(Booking)
        .where(
            Booking.spot_id == spot_id,
            Booking.status.in_([BookingStatus.plan, BookingStatus.in_progress]),
            Booking.end_time >= now,
        )
        .order_by(Booking.start_time)
    )
    return list(rows)