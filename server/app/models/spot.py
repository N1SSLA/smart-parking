from typing import List
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base

class Spot(Base):
    __tablename__ = "spots"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Название места (например, "A1", "B2")
    name: Mapped[str] = mapped_column(String(10), unique=True) 

    # Связь с бронями
    bookings: Mapped[List["Booking"]] = relationship(back_populates="spot")