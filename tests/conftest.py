import pytest
from contextlib import asynccontextmanager
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database import Base, get_db
from app.config import settings

# Use in-memory SQLite database for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with test database."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    @asynccontextmanager
    async def test_lifespan(_app):
        yield

    original_lifespan = app.router.lifespan_context
    app.dependency_overrides[get_db] = override_get_db
    app.router.lifespan_context = test_lifespan
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    app.router.lifespan_context = original_lifespan


@pytest.fixture
def test_user_data():
    """Sample user data for testing."""
    return {"telegram_id": "test_user_123", "display_name": "Test User"}


@pytest.fixture
def another_user_data():
    """Another sample user data for testing."""
    return {"telegram_id": "test_user_456", "display_name": "Another Test User"}


@pytest.fixture
def create_test_user(client, test_user_data):
    """Fixture that creates a user and returns the response."""
    response = client.post("/user", json=test_user_data)
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def get_auth_token(client, test_user_data, create_test_user):
    """Fixture that creates a user and returns an auth token."""
    response = client.post(f"/user/token?telegram_id={test_user_data['telegram_id']}")
    assert response.status_code == 200
    return response.json()["access_token"]
