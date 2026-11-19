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
Список мест (не возвращает статус или брони мест, только полный список мест).
- Auth: Bearer JWT
- 200: `[{ "id": 1, "name" }, ...]`


@ GET /api/v1/spots/{spot_id}/bookings

Список броней на конкретное место (только занятые интервалы времени, без персональных данных водителей).
- Auth: Bearer JWT
- Path: spot_id — ID парковочного места

Возвращает только брони со статусами plan и in_progress, у которых end_time >= текущего момента.

- 200: [{ "start_time": "2026-11-20T10:00:00Z", "end_time": "2026-11-20T12:00:00Z" }, ...]
- 404: Место с указанным spot_id не найдено
- 401: Невалидный или отсутствующий JWT


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


@ GET /api/v1/bookings/my

Список броней текущего пользователя (активные + история).

- Auth: Bearer JWT
- 200: [{ "id": 1, "spot_id": 1, "spot_name": "A1", "start_time": "...", "end_time": "...", "status": "plan", "actual_start_time": null, "actual_end_time": null }, ...]
- 401: Невалидный или отсутствующий JWT