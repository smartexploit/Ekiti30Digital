import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

import jwt
import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.core.config import settings
from app.models.base import Base
from app.api.dependencies import get_db as get_db_api
from app.main import app as fastapi_app

TEST_SECRET = "test-secret-key-1234567890-32-bytes"
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(autouse=True)
def configure_test_settings(monkeypatch):
    """Isolate and synchronize all security and configuration settings per test."""
    monkeypatch.setattr(settings, "CLOUDINARY_CLOUD_NAME", "ekiti-test")
    monkeypatch.setattr(settings, "CLOUDINARY_UPLOAD_PRESET", "ekiti30_member_unsigned")
    monkeypatch.setattr(settings, "DATABASE_URL", SQLALCHEMY_TEST_DATABASE_URL)
    
    cors_list = ["http://localhost:3000", "*"]
    if hasattr(settings, "cors_origins"):
        monkeypatch.setattr(settings, "cors_origins", cors_list)
    if hasattr(settings, "CORS_ORIGINS"):
        monkeypatch.setattr(settings, "CORS_ORIGINS", cors_list)

    if hasattr(settings, "JWT_SECRET"):
        monkeypatch.setattr(settings, "JWT_SECRET", TEST_SECRET)
    if hasattr(settings, "NEXTAUTH_SECRET"):
        monkeypatch.setattr(settings, "NEXTAUTH_SECRET", TEST_SECRET)
    if hasattr(settings, "ADMIN_JWT_SECRET"):
        monkeypatch.setattr(settings, "ADMIN_JWT_SECRET", TEST_SECRET)

@pytest.fixture(autouse=True)
def setup_test_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(setup_test_database):
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    fastapi_app.dependency_overrides[get_db_api] = _override_get_db

    with TestClient(fastapi_app) as c:
        yield c

    fastapi_app.dependency_overrides.clear()

@pytest.fixture
def make_token():
    def _generator(sub="admin_user", role="admin", secret=TEST_SECRET, expires_in=3600):
        now = datetime.now(timezone.utc)
        payload = {
            "sub": sub,
            "user_id": sub,
            "role": role,
            "is_admin": (role == "admin"),
            "iat": now,
            "exp": now + timedelta(seconds=expires_in),
        }
        return jwt.encode(payload, secret, algorithm="HS256")
    return _generator

@pytest.fixture
def admin_headers(make_token):
    token = make_token(sub="admin_user", role="admin")
    return {"Authorization": f"Bearer {token}"}
