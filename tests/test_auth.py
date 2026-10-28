def test_signup_success(client):
    res = client.post("/auth/signup", json={
        "username": "anushka",
        "email": "anushka@example.com",
        "password": "strongPassword123"
    })
    assert res.status_code == 201
    data = res.json()
    assert data["username"] == "anushka"
    assert data["email"] == "anushka@example.com"
    assert "id" in data
    assert "password" not in data  # Ensure password hash is never exposed!

def test_signup_duplicate_username(client):
    client.post("/auth/signup", json={
        "username": "unique_user",
        "email": "user1@example.com",
        "password": "password123"
    })
    # Try signup with same username
    res = client.post("/auth/signup", json={
        "username": "unique_user",
        "email": "user2@example.com",
        "password": "password123"
    })
    assert res.status_code == 409
    assert res.json()["detail"] == "Username is already taken"

def test_signup_duplicate_email(client):
    client.post("/auth/signup", json={
        "username": "user_one",
        "email": "same_email@example.com",
        "password": "password123"
    })
    # Try signup with same email
    res = client.post("/auth/signup", json={
        "username": "user_two",
        "email": "same_email@example.com",
        "password": "password123"
    })
    assert res.status_code == 409
    assert res.json()["detail"] == "Email is already registered"

def test_signup_invalid_email(client):
    res = client.post("/auth/signup", json={
        "username": "bademailuser",
        "email": "not-an-email",
        "password": "password123"
    })
    assert res.status_code == 422
    assert any("email" in err["field"] for err in res.json()["errors"])

def test_signup_short_password(client):
    res = client.post("/auth/signup", json={
        "username": "shortpassuser",
        "email": "shortpass@example.com",
        "password": "short"  # < 8 characters
    })
    assert res.status_code == 422
    assert any("password" in err["field"] for err in res.json()["errors"])

def test_login_success(client):
    client.post("/auth/signup", json={
        "username": "loginuser",
        "email": "login@example.com",
        "password": "myPassword123"
    })
    res = client.post("/auth/login", json={
        "username": "loginuser",
        "password": "myPassword123"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client):
    client.post("/auth/signup", json={
        "username": "wrongpassuser",
        "email": "wrongpass@example.com",
        "password": "myPassword123"
    })
    res = client.post("/auth/login", json={
        "username": "wrongpassuser",
        "password": "incorrectPassword"
    })
    assert res.status_code == 401
    assert res.json()["detail"] == "Invalid username or password"

def test_get_current_user_profile(client, auth_headers):
    # auth_headers fixture creates "testuser"
    res = client.get("/auth/me", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["username"] == "testuser"

def test_get_current_user_profile_unauthenticated(client):
    res = client.get("/auth/me")
    assert res.status_code == 401
    assert "missing" in res.json()["detail"].lower()
