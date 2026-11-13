Пока только test

В планах сделать следующие эндпоинты:

http://localhost:8000/docs#/test
http://localhost:8000/health

auth -- для авторизации/регистрации


Базовый URL: `http://localhost:8000`


# Аутентификация

@ POST /api/v1/auth/register
Регистрация пользователя.
- Body: `{ "login": "string", "password": "string" }`
- 201: создан
- 409: логин занят

@ POST /api/v1/auth/login
Логин, выдать JWT.
- Body: `{ "login": "string", "password": "string" }`
- 200: `{ "access_token": "...", "user": { ... } }`

# Парковочные места

@ GET /api/v1/spots
Список мест с текущим статусом.
- Auth: Bearer JWT
- 200: `[{ "id": 1, "status": "free" }, ...]`

## Бронирования

@ POST /api/v1/bookings
Создать бронь.
- Auth: Bearer JWT
- Body: `{ "spot_id": 1, "start": "2026-11-15T10:00:00", "end": "2026-11-15T12:00:00" }`
- 201: бронь создана
- 409: место занято
- 402: недостаточно средств

@ POST /api/v1/bookings/{id}/cancel
Отменить бронь.
- Auth: Bearer JWT
- 200: отменена (возврат по правилам)

## Шлагбаум (для Raspberry Pi)

@ POST /device/v1/gate/in
Приложили карту на въезде.
- Header: `X-Device-Key: <device_key>`
- Body: `{ "card_uid": "string" }`
- 200: `{ "allow": true/false, "reason": "..." }`

@ POST /device/v1/gate/out
Приложили карту на выезде.
- Header: `X-Device-Key: <device_key>`
- Body: `{ "card_uid": "string" }`
- 200: `{ "allow": true/false, "fine": 0 }`