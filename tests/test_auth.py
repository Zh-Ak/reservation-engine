async def test_register_returns_user_without_password(client):
    response = await client.post(
        "/users/register",
        json={"name": "Anna", "surname": "Kis", "email": "Anna@X.com", "password": "secret123", "role": "client"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "anna@x.com"
    assert body["role"] == "client"
    assert "password" not in body and "password_hash" not in body


async def test_register_duplicate_email_is_case_insensitive(client, make_user):
    await make_user("client", email="anna@x.com")
    response = await client.post(
        "/users/register",
        json={"name": "A", "surname": "B", "email": "ANNA@x.com", "password": "secret123", "role": "client"},
    )
    assert response.status_code == 409


async def test_cannot_register_as_moderator(client):
    response = await client.post(
        "/users/register",
        json={"name": "A", "surname": "B", "email": "m@x.com", "password": "secret123", "role": "moderator"},
    )
    assert response.status_code == 422


async def test_login_wrong_password_and_unknown_email_look_the_same(client, make_user):
    await make_user("client", email="anna@x.com")
    wrong_password = await client.post("/auth/login", json={"email": "anna@x.com", "password": "nope-nope"})
    unknown_email = await client.post("/auth/login", json={"email": "ghost@x.com", "password": "nope-nope"})
    assert wrong_password.status_code == unknown_email.status_code == 401
    assert wrong_password.json() == unknown_email.json()
    assert wrong_password.headers["www-authenticate"] == "Bearer"


async def test_me_requires_a_valid_token(client, make_user):
    headers, user = await make_user("client")
    assert (await client.get("/users/me", headers=headers)).json()["id"] == user["id"]
    assert (await client.get("/users/me")).status_code == 401

    tampered = headers["Authorization"][:-2] + ("aa" if not headers["Authorization"].endswith("aa") else "bb")
    assert (await client.get("/users/me", headers={"Authorization": tampered})).status_code == 401