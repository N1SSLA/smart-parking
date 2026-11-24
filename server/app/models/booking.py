import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey, DateTime, Enum, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base

class BookingStatus(str, enum.Enum):
    plan = "plan"                # Забронировано, но машина еще не заехала
    in_progress = "in_progress"  # Машина на парковке
    archived = "archived"        # Машина выехала или бронь отменена

class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Внешние ключи
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    spot_id: Mapped[int] = mapped_column(ForeignKey("spots.id"))

    # Время по плану
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    price: Mapped[float] = mapped_column(Float, default=0.0)

    # Фактическое время (заполняется при заезде/выезде)
    actual_start_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Статус брони
    status: Mapped[BookingStatus] = mapped_column(
        Enum(BookingStatus), 
        default=BookingStatus.plan
    )

    # Связи
    user: Mapped["User"] = relationship(back_populates="bookings")
    spot: Mapped["Spot"] = relationship(back_populates="bookings")