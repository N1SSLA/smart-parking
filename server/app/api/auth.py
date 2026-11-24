from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.user import User
from app.schemas import RegisterIn, LoginIn, TokenOut, UserOut, CardIn, TopUpIn
from app.security import hash_password, verify_password, create_access_token
from app.deps import get_current_user

router = APIRouter()


@router.post(
    "/register", 
    status_code=201, 
    response_model=UserOut, 
    summary="Регистрация водителя",
    description=(
        "Создаёт пользователя с балансом 0. "
        "Вызывается один раз при первом запуске Android-приложения. "
        "409 — логин занят."
    ),   
)
async def register(data: RegisterIn, db: AsyncSession = Depends(get_db)):
    exists = await db.scalar(select(User).where(User.login == data.login))
    if exists:
        raise HTTPException(status_code=409, detail="Login already taken")
    user = User(login=data.login, hashed_password=hash_password(data.password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post(
    "/login",
    response_model=TokenOut,
    summary="Вход, выдача JWT",
    description=(
        "Аутентифицирует пользователя и возвращает JWT (живёт 24 ч). "
        "Токен нужен для всех защищённых запросов в заголовке "
        "`Authorization: Bearer <token>`. 401 — неверные логин/пароль."
    ),
)
async def login(data: LoginIn, db: AsyncSession = Depends(get_db)):
    user = await db.scalar(select(User).where(User.login == data.login))
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return TokenOut(
        access_token=create_access_token(user.id),
        user=UserOut.model_validate(user),
    )




@router.post(
    "/me/card",
    response_model=UserOut,
    summary="Привязать RFID/NFC-карту",
    description=(
        "Привязывает карту (UID) к текущему пользователю. "
        "Вызывается из Android после регистрации/логина, когда водитель получил карту. "
        "Без привязки шлагбаум не идентифицирует водителя и отвечает `Unknown card`. "
        "409 — карта уже привязана к другому пользователю."
    ),
)
async def bind_card(
    data: CardIn,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    taken = await db.scalar(select(User).where(User.rfid_uid == data.card_uid, User.id != user.id))
    if taken:
        raise HTTPException(status_code=409, detail="Card already bound")
    user.rfid_uid = data.card_uid
    await db.commit()
    await db.refresh(user)
    return user


@router.post(
    "/me/topup",
    response_model=UserOut,
    summary="Пополнить баланс (заглушка)",
    description=(
        "Увеличивает баланс на `amount` (0 < amount ≤ 10000). "
        "Вызывается с экрана «Пополнить баланс» перед бронированием. "
        "Без пополнения `POST /api/v1/bookings` вернёт 402 при нулевом балансе."
    ),
)
async def topup(
    data: TopUpIn,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    user.balance += data.amount
    await db.commit()
    await db.refresh(user)
    return user