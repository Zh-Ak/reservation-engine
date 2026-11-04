import asyncio

from tests.conftest import days_from_today


async def test_parallel_requests_never_double_book(client, make_user, make_hotel):
    hotel = await make_hotel(rooms=3)
    users = [await make_user("client") for _ in range(15)]
    body = {
        "room_type_id": hotel["room_type_id"],
        "start_date": days_from_today(30),
        "end_date": days_from_today(33),
        "guest_count": 1,
    }

    responses = await asyncio.gather(
        *(client.post("/bookings", json=body, headers=headers) for headers, _ in users)
    )
    statuses = sorted(r.status_code for r in responses)
    created = [r.json() for r in responses if r.status_code == 201]

    assert statuses.count(201) == 3  # exactly one booking per physical room
    assert statuses.count(409) == 12  # everyone else gets a clean "not available"
    assert len({b["room_instance_id"] for b in created}) == 3