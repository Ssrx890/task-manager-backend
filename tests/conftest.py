import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_session
from app.core.security import get_password_hash
from app.models.user import User


@pytest.fixture(name="session")
def session_fixture():
    """Crea una BD en memoria para cada test."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """TestClient que usa la BD en memoria."""
    def get_session_override():
        yield session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="admin_token")
def admin_token_fixture(client: TestClient, session: Session):
    """Crea un admin y devuelve su token."""
    admin = User(
        email="admin@test.com",
        full_name="Admin Test",
        role="ADMIN",
        hashed_password=get_password_hash("admin123"),
    )
    session.add(admin)
    session.commit()

    response = client.post(
        "/auth/login",
        data={"username": "admin@test.com", "password": "admin123"},
    )
    return response.json()["access_token"]


@pytest.fixture(name="seller_token")
def seller_token_fixture(client: TestClient, session: Session):
    """Crea un vendedor y devuelve su token."""
    seller = User(
        email="seller@test.com",
        full_name="Seller Test",
        role="SELLER",
        hashed_password=get_password_hash("seller123"),
    )
    session.add(seller)
    session.commit()

    response = client.post(
        "/auth/login",
        data={"username": "seller@test.com", "password": "seller123"},
    )
    return response.json()["access_token"]


def auth_header(token: str) -> dict:
    """Helper para construir el header de autenticación."""
    return {"Authorization": f"Bearer {token}"}
