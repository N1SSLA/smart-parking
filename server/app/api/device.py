from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.user import User
from app.models.booking import Booking, BookingStatus
from app.schemas import GateIn, GateResult
from app.deps import check_device_key

router = APIRouter(dependencies=[Depends(check_device_key)])


@router.post("/in", response_model=GateResult)
async def gate_in(data: GateIn, db: AsyncSession = Depends(get_db)):
    user = await db.scalar(select(User).where(User.rfid_uid == data.card_uid))
    if user is None:
        return GateResult(allow=False, reason="Unknown card")

    now = datetime.now(timezone.utc)
    booking = await db.scalar(
        select(Booking).where(
            Booking.user_id == user.id,
            Booking.status == BookingStatus.plan,
            Booking.start_time <= now,
            Booking.end_time >= now,
        ).order_by(Booking.start_time)
    )
    if booking is None:
        return GateResult(allow=False, reason="No active booking")

    occupied = await db.scalar(
        select(Booking).where(
            Booking.spot_id == booking.spot_id,
            Booking.status == BookingStatus.in_progress,
            Booking.id != booking.id,
        )
    )
    if occupied:
        return GateResult(allow=False, reason="Spot is occupied")

    booking.status = BookingStatus.in_progress
    booking.actual_start_time = now
    await db.commit()
    return GateResult(allow=True, reason="Welcome")


@router.post("/out", response_model=GateResult)
async def gate_out(data: GateIn, db: AsyncSession = Depends(get_db)):
    user = await db.scalar(select(User).where(User.rfid_uid == data.card_uid))
    if user is None:
        return GateResult(allow=False, reason="Unknown card")

    now = datetime.now(timezone.utc)
    booking = await db.scalar(
        select(Booking).where(
            Booking.user_id == user.id,
            Booking.status == BookingStatus.in_progress,
        ).order_by(Booking.actual_start_time.desc())
    )
    if booking is None:
        return GateResult(allow=False, reason="No open session")

    fine = 0.0
    if now > booking.end_time:
        over = (now - booking.end_time).total_seconds() / 3600
        fine = round(over * 200.0, 2)
        user.balance -= fine

    booking.status = BookingStatus.archived
    booking.actual_end_time = now
    await db.commit()
    return GateResult(allow=True, reason="Bye", fine=fine)