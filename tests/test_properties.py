PROPERTY = {"name": "Hotel", "country": "Hungary", "city": "Budapest", "address": "Main st 1"}


async def test_client_cannot_create_property(client, make_user):
    headers, _ = await make_user("client")
    response = await client.post("/properties", json=PROPERTY, headers=headers)
    assert response.status_code == 403


async def test_provider_can_own_several_properties_in_one_city(client, make_user):
    headers, _ = await make_user("provider")
    first = await client.post("/properties", json=PROPERTY, headers=headers)
    second = await client.post("/properties", json=PROPERTY | {"name": "Hotel 2"}, headers=headers)
    assert first.status_code == second.status_code == 201
    mine = await client.get("/properties/mine", headers=headers)
    assert len(mine.json()) == 2


async def test_other_provider_cannot_edit_my_property(client, make_user):
    owner, _ = await make_user("provider")
    stranger, _ = await make_user("provider")
    prop = (await client.post("/properties", json=PROPERTY, headers=owner)).json()

    response = await client.patch(f"/properties/{prop['id']}", json={"name": "Mine now"}, headers=stranger)
    assert response.status_code == 404

    response = await client.patch(f"/properties/{prop['id']}", json={"name": "Renamed"}, headers=owner)
    assert response.status_code == 200
    assert response.json()["name"] == "Renamed"


async def test_patch_rejects_null_for_required_field(client, make_user):
    owner, _ = await make_user("provider")
    prop = (await client.post("/properties", json=PROPERTY, headers=owner)).json()
    response = await client.patch(f"/properties/{prop['id']}", json={"name": None}, headers=owner)
    assert response.status_code == 422


async def test_deleted_property_disappears(client, make_user):
    owner, _ = await make_user("provider")
    prop = (await client.post("/properties", json=PROPERTY, headers=owner)).json()
    assert (await client.delete(f"/properties/{prop['id']}", headers=owner)).status_code == 204
    assert (await client.get(f"/properties/{prop['id']}")).status_code == 404