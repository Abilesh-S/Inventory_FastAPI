import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base
from app.db.database import get_db
from app.core.security import hash_password
from app.models.user import User, RoleEnum


# Separate database used ONLY for pytest
# Your actual application continues to use PostgreSQL.
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Replace the application's PostgreSQL dependency
# with the SQLite test database.
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def admin_token(client, db_session):
    """
    Create an admin directly in the test DB,
    then use the real login API to obtain a JWT.
    """

    admin = User(
        username="testadmin",
        email="admin@test.com",
        hashed_password=hash_password("adminpass123"),
        role=RoleEnum.ADMIN,
    )

    db_session.add(admin)
    db_session.commit()

    response = client.post(
        "/auth/login",
        data={
            "username": "testadmin",
            "password": "adminpass123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"

    return data["access_token"]


@pytest.fixture()
def employee_token(client, admin_token):
    """
    Create an employee using the actual create-user API,
    then login using the actual login API.
    """

    response = client.post(
        "/auth/create-user",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "username": "testemployee",
            "email": "employee@test.com",
            "password": "employeepass123",
            "role": "EMPLOYEE",
        },
    )

    assert response.status_code == 200

    response = client.post(
        "/auth/login",
        data={
            "username": "testemployee",
            "password": "employeepass123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"

    return data["access_token"]


@pytest.fixture()
def admin_headers(admin_token):
    return {
        "Authorization": f"Bearer {admin_token}"
    }


@pytest.fixture()
def employee_headers(employee_token):
    return {
        "Authorization": f"Bearer {employee_token}"
    }


@pytest.fixture()
def sample_product(client, admin_headers):
    response = client.post(
        "/admin/products",
        headers=admin_headers,
        json={
            "name": "Test Widget",
            "sku": "TW-001",
            "price": 99.99,
            "quantity": 0,
        },
    )

    assert response.status_code == 200

    return response.json()