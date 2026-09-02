# Reservation Engine

A backend system for hotel/accommodation booking, focused on demonstrating
correct handling of concurrency, data consistency, and scalable API design.

## Status

Early development. Project skeleton only — no functional endpoints yet
beyond a basic health check.

## Motivation

This project intentionally focuses on the hardest problem in a booking
platform: safely preventing double-booking of the same resource under
concurrent requests, using database-enforced consistency guarantees rather
than relying solely on application-level checks.

## Tech stack

- Python, FastAPI (async)
- PostgreSQL, SQLAlchemy 2.0 (async)
- Poetry for dependency management

## Architecture

Layered: routes → services → repositories → database, with authorization
and business logic kept out of the routes layer, and consistency guarantees
enforced at the database level wherever correctness is non-negotiable.

## Running locally

```bash
poetry install
poetry run uvicorn app.main:app --reload
```

Then visit `http://localhost:8000/health`.