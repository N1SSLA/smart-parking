from typing import Optional, List
from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    
    # RFID-метка (может быть не привязана)
    rfid_uid: Mapped[Optional[str]] = mapped_column(String(50), unique=True, nullable=True, index=True)
    
    balance: Mapped[float] = mapped_column(Float, default=0.0)

    # Связь с бронями
    bookings: Mapped[List["Booking"]] = relationship(back_populates="user")