from tests.conftest import days_from_today


def booking_body(room_type_id, start=10, end=13, guests=2):
    return {
        "room_type_id": room_type_id,
        "start_date": days_from_today(start),
        "end_date": days_from_today(end),
        "guest_count": guests,
    }


async def test_booking_freezes_total_price(client, make_user, make_hotel):
    hotel = await make_hotel(price="100.00")
    headers, _ = await make_user("client")
    response = await client.post("/bookings", json=booking_body(hotel["room_type_id"]), headers=headers)
    assert response.status_code == 201
    assert response.json()["total_price"] == "300.00"  # 3 nights x 100

    # A later price change does not touch the existing booking.
    await client.patch(
        f"/room-types/{hotel['room_type_id']}", json={"price": "999.00"}, headers=hotel["provider_headers"]
    )
    again = await client.get(f"/bookings/{response.json()['id']}", headers=headers)
    assert again.json()["total_price"] == "300.00"


async def test_business_rules(client, make_user, make_hotel):
    hotel = await make_hotel(capacity=2)
    headers, _ = await make_user("client")
    past = await client.post("/bookings", json=booking_body(hotel["room_type_id"], start=-2, end=1), headers=headers)
    too_many = await client.post("/bookings", json=booking_body(hotel["room_type_id"], guests=3), headers=headers)
    reversed_dates = await client.post(
        "/bookings", json=booking_body(hotel["room_type_id"], start=5, end=5), headers=headers
    )
    assert past.status_code == too_many.status_code == reversed_dates.status_code == 422


async def test_provider_cannot_book(client, make_hotel):
    hotel = await make_hotel()
    response = await client.post(
        "/bookings", json=booking_body(hotel["room_type_id"]), headers=hotel["provider_headers"]
    )
    assert response.status_code == 403


async def test_overlap_rejected_but_back_to_back_allowed(client, make_user, make_hotel):
    hotel = await make_hotel(rooms=1)
    anna, _ = await make_user("client")
    bob, _ = await make_user("client")

    first = await client.post("/bookings", json=booking_body(hotel["room_type_id"], 10, 13), headers=anna)
    overlap = await client.post("/bookings", json=booking_body(hotel["room_type_id"], 12, 14), headers=bob)
    back_to_back = await client.post("/bookings", json=booking_body(hotel["room_type_id"], 13, 15), headers=bob)

    assert first.status_code == 201
    assert overlap.status_code == 409
    assert back_to_back.status_code == 201  # check-out day 13 = check-in day 13


async def test_second_room_is_used_when_first_is_taken(client, make_user, make_hotel):
    hotel = await make_hotel(rooms=2)
    anna, _ = await make_user("client")
    first = await client.post("/bookings", json=booking_body(hotel["room_type_id"]), headers=anna)
    second = await client.post("/bookings", json=booking_body(hotel["room_type_id"]), headers=anna)
    third = await client.post("/bookings", json=booking_body(hotel["room_type_id"]), headers=anna)
    assert first.status_code == second.status_code == 201
    assert first.json()["room_instance_id"] != second.json()["room_instance_id"]
    assert third.status_code == 409


async def test_cancel_frees_the_room(client, make_user, make_hotel):
    hotel = await make_hotel(rooms=1)
    anna, _ = await make_user("client")
    bob, _ = await make_user("client")
    booking = (await client.post("/bookings", json=booking_body(hotel["room_type_id"]), headers=anna)).json()

    assert (await client.post(f"/bookings/{booking['id']}/cancel", headers=bob)).status_code == 404
    cancelled = await client.post(f"/bookings/{booking['id']}/cancel", headers=anna)
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "cancelled"
    assert cancelled.json()["cancelled_at"] is not None
    assert (await client.post(f"/bookings/{booking['id']}/cancel", headers=anna)).status_code == 409

    rebooked = await client.post("/bookings", json=booking_body(hotel["room_type_id"]), headers=bob)
    assert rebooked.status_code == 201


async def test_cannot_delete_property_with_upcoming_bookings(client, make_user, make_hotel):
    hotel = await make_hotel()
    anna, _ = await make_user("client")
    await client.post("/bookings", json=booking_body(hotel["room_type_id"]), headers=anna)
    response = await client.delete(f"/properties/{hotel['property_id']}", headers=hotel["provider_headers"])
    assert response.status_code == 409


async def test_provider_sees_bookings_of_own_property(client, make_user, make_hotel):
    hotel = await make_hotel()
    anna, _ = await make_user("client")
    await client.post("/bookings", json=booking_body(hotel["room_type_id"]), headers=anna)
    response = await client.get(
        f"/properties/{hotel['property_id']}/bookings", headers=hotel["provider_headers"]
    )
    assert response.status_code == 200
    assert len(response.json()) == 1