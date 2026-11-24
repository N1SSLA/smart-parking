from datetime import datetime
from pydantic import BaseModel, Field

from app.models.booking import BookingStatus


class RegisterIn(BaseModel):
    login: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=4, max_length=128)


class LoginIn(BaseModel):
    login: str
    password: str


class UserOut(BaseModel):
    id: int
    login: str
    balance: float
    rfid_uid: str | None = None
    model_config = {"from_attributes": True}


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class CardIn(BaseModel):
    card_uid: str = Field(min_length=1, max_length=50)


class TopUpIn(BaseModel):
    amount: float = Field(gt=0, le=10000)


class SpotOut(BaseModel):
    id: int
    name: str
    is_occupied: bool = False
    model_config = {"from_attributes": True}


class SpotBookingOut(BaseModel):
    start_time: datetime
    end_time: datetime
    model_config = {"from_attributes": True}


class BookingCreate(BaseModel):
    spot_id: int
    start: datetime
    end: datetime

    @field_validator("start", "end")
    @classmethod
    def _to_utc(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc)
    
    def _half_hour(cls, v: datetime) -> datetime:
        if v.minute not in (0, 30) or v.second != 0 or v.microsecond != 0:
            raise ValueError("time must be aligned to 30 minutes")
        return v


class BookingOut(BaseModel):
    id: int
    spot_id: int
    spot_name: str
    start_time: datetime
    end_time: datetime
    status: BookingStatus
    actual_start_time: datetime | None
    actual_end_time: datetime | None


class GateIn(BaseModel):
    card_uid: str


class GateResult(BaseModel):
    allow: bool
    reason: str = ""
    fine: float = 0.0