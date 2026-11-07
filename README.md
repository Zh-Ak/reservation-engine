# Reservation Engine

A hotel booking API (FastAPI, PostgreSQL) that guarantees a room is never double-booked,
even when many requests arrive at the same moment. The guarantee lives in the database,
not in application code.

## Highlights

- **No double bookings, proven by a test.** A PostgreSQL exclusion constraint on
  `(room_instance_id, daterange(start_date, end_date))` for confirmed bookings. The booking
  service tries free rooms one by one inside savepoints and moves on when the constraint
  rejects one. A test sends 15 parallel booking requests for 3 rooms: exactly 3 succeed,
  the other 12 get a clean `409`. Without the constraint, all 15 succeed.
- **Price snapshot.** Each booking stores the price agreed at booking time, so later price
  changes never affect existing bookings.
- **Role-based access and ownership checks.** Providers manage only their own properties and
  rooms; clients see only their own bookings. Other users' resources return `404`, so ids
  cannot be probed.
- **Layered architecture.** Routes (HTTP) → services (business rules, transactions) →
  repositories (queries). One transaction per service call; one central error handler.
- **22 tests against real PostgreSQL**, including a concurrency test.

## Quick start

```bash
cp .env.example .env        # then set SECRET_KEY (generate one with: openssl rand -hex 32)
docker compose up --build
```

Open http://localhost:8000/docs. The database runs in Docker and is reachable from your
machine on port `5433`.

## Running tests

The tests need a separate, empty PostgreSQL database (they delete all data between tests).

```bash
docker compose up -d db
docker compose exec db createdb -U postgres reservation_test
export TEST_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/reservation_test
poetry install
poetry run pytest
```

## API overview

| Endpoint | Who |
| --- | --- |
| `POST /users/register`, `POST /auth/login` | Anyone |
| `GET /users/me` | Logged-in users |
| `POST /properties`, `GET /properties/mine`, `PATCH` / `DELETE /properties/{id}` | Providers (own properties) |
| `POST /properties/{id}/room-types`, `PATCH` / `DELETE /room-types/{id}` | Providers (own properties) |
| `POST /room-types/{id}/rooms`, `GET /room-types/{id}/rooms`, `DELETE /rooms/{id}` | Providers (own rooms) |
| `GET /properties/{id}/bookings` | Providers (own properties) |
| `GET /properties/{id}`, `GET /properties/{id}/room-types` | Anyone |
| `GET /search/availability?city=&check_in=&check_out=&guests=` | Anyone |
| `POST /bookings`, `GET /bookings/mine`, `GET /bookings/{id}`, `POST /bookings/{id}/cancel` | Clients |
| `GET /health` | Anyone (checks the database) |

## Design decisions

| Decision | Why |
| --- | --- |
| Exclusion constraint instead of application checks or locks | Checking availability in code is always racy; the constraint is correct for every code path and only blocks real conflicts |
| Room types (what is sold) vs physical rooms (what is occupied) | Makes "no overlapping bookings per room" enforceable by the database |
| Half-open stays `[check_in, check_out)` | A guest can check in on the day another checks out; matches PostgreSQL's `daterange` |
| Soft deletes (`deleted_at`) | Keeps history and keeps past bookings pointing at real rows |
| JWT plus a database lookup per request | Stateless token verification, but deleted users lose access immediately |
| `404` instead of `403` for other users' resources | Does not reveal which ids exist |

## What I would add next

- Idempotency keys for booking requests (safe retries after network errors)
- A transactional outbox for booking notifications
- Refresh tokens
- Payments with a `pending` booking state
- Caching for search results and rate limiting on login
- CI that runs the tests on every push

## Tech stack

Python 3.13, FastAPI, SQLAlchemy 2.0 (async), asyncpg, Alembic, PostgreSQL 16, Pydantic v2,
PyJWT, bcrypt, pytest, Docker.