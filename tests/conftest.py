import sys
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import app
from database import get_db
from models import Base

# In-memory SQLite for testing: ultra-fast and completely isolated from tasks.db
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Create fresh database tables before each test and drop them after."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """FastAPI TestClient with overridden database dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def auth_headers(client):
    """Helper fixture: Creates a user, logs in, and returns bearer auth headers."""
    client.post("/auth/signup", json={
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "password123"
    })
    login_resp = client.post("/auth/login", json={
        "username": "testuser",
        "password": "password123"
    })
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def second_user_headers(client):
    """Helper fixture: Creates a second user for testing user isolation."""
    client.post("/auth/signup", json={
        "username": "seconduser",
        "email": "seconduser@example.com",
        "password": "password123"
    })
    login_resp = client.post("/auth/login", json={
        "username": "seconduser",
        "password": "password123"
    })
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
