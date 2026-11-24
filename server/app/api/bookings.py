from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.booking import Booking, BookingStatus
from app.models.spot import Spot
from app.models.user import User
from app.schemas import BookingCreate, BookingOut
from app.deps import get_current_user

router = APIRouter(
    description="Создание, отмена и история броней текущего пользователя.",
)
PRICE_PER_HOUR = 100.0


def _out(b: Booking) -> BookingOut:
    return BookingOut(
        id=b.id,
        spot_id=b.spot_id,
        spot_name=b.spot.name,
        start_time=b.start_time,
        end_time=b.end_time,
        status=b.status,
        actual_start_time=b.actual_start_time,
        actual_end_time=b.actual_end_time,
    )


@router.post(
    "",
    status_code=201,
    response_model=BookingOut,
    summary="Создать бронь",
    description=(
        "Создаёт бронь на место на интервал (время с точностью 30 мин, `end > start`). "
        "Проверяет пересечение с активными бронями (409) и баланс (402), "
        "списывает `PRICE_PER_HOUR * часы` и сохраняет сумму в `price`. "
        "Статус новой брони — `plan`. "
        "400 — `end <= start` или время не кратно 30 мин; 404 — нет места."
    ),
)
async def create_booking(
    data: BookingCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    spot = await db.get(Spot, data.spot_id)
    if spot is None:
        raise HTTPException(status_code=404, detail="Spot not found")
    if data.end <= data.start:
        raise HTTPException(status_code=400, detail="end must be after start")

    overlap = await db.scalar(
        select(Booking).where(
            Booking.spot_id == data.spot_id,
            Booking.status.in_([BookingStatus.plan, BookingStatus.in_progress]),
            Booking.start_time < data.end,
            Booking.end_time > data.start,
        )
    )
    if overlap:
        raise HTTPException(status_code=409, detail="Spot already booked")

    hours = (data.end - data.start).total_seconds() / 3600
    price = round(hours * PRICE_PER_HOUR, 2)
    if user.balance < price:
        raise HTTPException(status_code=402, detail="Insufficient funds")

    user.balance -= price
    booking = Booking(
        user_id=user.id,
        spot_id=data.spot_id,
        start_time=data.start,
        end_time=data.end,
        price=price,
        status=BookingStatus.plan,
    )
    db.add(booking)
    await db.commit()
    await db.refresh(booking)
    await db.refresh(booking, attribute_names=["spot"])
    return _out(booking)


@router.post(
    "/{booking_id}/cancel",
    response_model=BookingOut,
    summary="Отменить плановую бронь",
    description=(
        "Отменяет **только** бронь в статусе `plan` (ещё не заехали). "
        "Возврат: >10 мин до старта — полная сумма, ≤10 мин — половина. "
        "Статус → `archived`. "
        "400 — бронь уже `in_progress`/`archived` (выезд — только через шлагбаум); "
        "404 — бронь не найдена или чужая."
    ),
)
async def cancel_booking(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    booking = await db.get(Booking, booking_id)
    if booking is None or booking.user_id != user.id:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.status != BookingStatus.plan:
        raise HTTPException(status_code=400, detail="Only planned bookings can be cancelled")

    now = datetime.now(timezone.utc)
    minutes_left = (booking.start_time - now).total_seconds() / 60
    if minutes_left > 10:
        refund = booking.price
    else:
        refund = booking.price / 2
    user.balance += refund

    booking.status = BookingStatus.archived
    await db.commit()
    await db.refresh(booking)
    await db.refresh(booking, attribute_names=["spot"])
    return _out(booking)


@router.get(
    "/my",
    response_model=list[BookingOut],
    summary="Мои брони (активные + история)",
    description=(
        "Возвращает все брони текущего пользователя, сортировка по `start_time desc`. "
        "Включает `plan`, `in_progress` и `archived`. "
        "Вызывается экраном «Мои поездки / История»."
    ),
)
async def my_bookings(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    rows = await db.scalars(
        select(Booking)
        .where(Booking.user_id == user.id)
        .order_by(Booking.start_time.desc())
    )
    bookings = list(rows)
    for b in bookings:
        await db.refresh(b, attribute_names=["spot"])
    return [_out(b) for b in bookings]