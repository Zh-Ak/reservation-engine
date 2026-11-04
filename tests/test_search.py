from tests.conftest import days_from_today


async def search(client, **params):
    query = {"city": "budapest", "check_in": days_from_today(10), "check_out": days_from_today(12), "guests": 2}
    query.update(params)
    return await client.get("/search/availability", params=query)


async def test_search_counts_free_rooms_and_prices_the_stay(client, make_user, make_hotel):
    hotel = await make_hotel(rooms=2, price="80.00")
    response = await search(client)
    assert response.status_code == 200
    [result] = response.json()
    assert result["available_rooms"] == 2
    assert result["nights"] == 2
    assert result["total_price"] == "160.00"

    anna, _ = await make_user("client")
    await client.post(
        "/bookings",
        json={"room_type_id": hotel["room_type_id"], "start_date": days_from_today(11),
              "end_date": days_from_today(13), "guest_count": 1},
        headers=anna,
    )
    [result] = (await search(client)).json()
    assert result["available_rooms"] == 1


async def test_search_filters_by_capacity_and_city(client, make_hotel):
    await make_hotel(capacity=2, city="Budapest")
    assert (await search(client, guests=3)).json() == []
    assert (await search(client, city="Vienna")).json() == []
    assert len((await search(client, city="  BUDAPEST ")).json()) == 1


async def test_search_rejects_bad_dates(client):
    assert (await search(client, check_in=days_from_today(5), check_out=days_from_today(5))).status_code == 422
    assert (await search(client, check_in=days_from_today(-1), check_out=days_from_today(2))).status_code == 422