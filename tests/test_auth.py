from tests.conftest import auth_header


def test_register_user(client):
    response = client.post("/auth/register", json={
        "email": "new@test.com",
        "full_name": "New User",
        "password": "pass123",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new@test.com"
    assert data["role"] == "SELLER"
    assert "hashed_password" not in data


def test_register_duplicate_email(client, session):
    client.post("/auth/register", json={
        "email": "dup@test.com", "full_name": "Dup", "password": "p",
    })
    response = client.post("/auth/register", json={
        "email": "dup@test.com", "full_name": "Dup2", "password": "p",
    })
    assert response.status_code == 400


def test_login_success(client):
    client.post("/auth/register", json={
        "email": "login@test.com", "full_name": "Login", "password": "pass123",
    })
    response = client.post("/auth/login", data={
        "username": "login@test.com", "password": "pass123",
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_bad_password(client):
    client.post("/auth/register", json={
        "email": "bad@test.com", "full_name": "Bad", "password": "pass123",
    })
    response = client.post("/auth/login", data={
        "username": "bad@test.com", "password": "wrong",
    })
    assert response.status_code == 401


def test_get_me(client, seller_token):
    response = client.get("/auth/me", headers=auth_header(seller_token))
    assert response.status_code == 200
    assert response.json()["email"] == "seller@test.com"


def test_create_admin_requires_admin(client, seller_token):
    response = client.post("/auth/create-admin", json={
        "email": "new_admin@test.com", "full_name": "New", "password": "p",
    }, headers=auth_header(seller_token))
    assert response.status_code == 403


def test_create_admin_success(client, admin_token):
    response = client.post("/auth/create-admin", json={
        "email": "admin2@test.com", "full_name": "Admin2", "password": "p",
    }, headers=auth_header(admin_token))
    assert response.status_code == 201
    assert response.json()["role"] == "ADMIN"
