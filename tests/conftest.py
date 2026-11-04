import datetime
import os

# Point the app at the TEST database before anything from `app` is imported.
os.environ["DATABASE_URL"] = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/reservation_test",
)
os.environ.setdefault("SECRET_KEY", "test-secret-key-0123456789abcdef0123456789abcdef")

import pytest
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from app.db.session import engine
from app.main import app

TABLES = "notification_logs, bookings, room_instances, room_types, properties, users"


@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    """Build the real schema (constraints included) once per test run."""
    command.upgrade(Config("alembic.ini"), "head")


@pytest.fixture(autouse=True)
async def clean_database():
    async with engine.begin() as conn:
        await conn.execute(text(f"TRUNCATE {TABLES} CASCADE"))
    yield


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest.fixture
def make_user(client):
    """make_user("client") -> (auth headers, user json)."""
    counter = 0

    async def _make_user(role: str = "client", email: str | None = None):
        nonlocal counter
        counter += 1
        email = email or f"{role}{counter}@example.com"
        response = await client.post(
            "/users/register",
            json={"name": "Test", "surname": "User", "email": email, "password": "secret123", "role": role},
        )
        assert response.status_code == 201, response.text
        login = await client.post("/auth/login", json={"email": email, "password": "secret123"})
        token = login.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}, response.json()

    return _make_user


@pytest.fixture
def make_hotel(client, make_user):
    """A provider with one property, one room type and `rooms` physical rooms."""

    async def _make_hotel(rooms: int = 1, price: str = "100.00", capacity: int = 2, city: str = "Budapest"):
        headers, _ = await make_user("provider")
        prop = await client.post(
            "/properties",
            json={"name": "Hotel Danube", "country": "Hungary", "city": city, "address": "Main st 1"},
            headers=headers,
        )
        room_type = await client.post(
            f"/properties/{prop.json()['id']}/room-types",
            json={"name": "Double", "price": price, "capacity": capacity},
            headers=headers,
        )
        room_type_id = room_type.json()["id"]
        for number in range(rooms):
            await client.post(
                f"/room-types/{room_type_id}/rooms", json={"label": f"{101 + number}"}, headers=headers
            )
        return {"provider_headers": headers, "property_id": prop.json()["id"], "room_type_id": room_type_id}

    return _make_hotel


def days_from_today(days: int) -> str:
    return (datetime.date.today() + datetime.timedelta(days=days)).isoformat()