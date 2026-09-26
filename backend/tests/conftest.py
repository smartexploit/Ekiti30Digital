import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime, timedelta
import os
import jwt

from app.main import app
from app.models.base import Base
from app.api.dependencies import get_db
from app.core.config import settings

settings.NEXTAUTH_SECRET = "test-secret-key-123456"

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(autouse=True)
def setup_database():
    if "CLOUDINARY_CLOUD_NAME" not in os.environ:
        os.environ["CLOUDINARY_CLOUD_NAME"] = "ekiti-test"
    if "CLOUDINARY_API_KEY" not in os.environ:
        os.environ["CLOUDINARY_API_KEY"] = "123456789"
    if "CLOUDINARY_API_SECRET" not in os.environ:
        os.environ["CLOUDINARY_API_SECRET"] = "test-secret"
    if "CLOUDINARY_UPLOAD_PRESET" not in os.environ:
        os.environ["CLOUDINARY_UPLOAD_PRESET"] = "ekiti30_member_unsigned"

    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

@pytest.fixture
def make_token():
    def _make_token(email="admin@example.com", role="admin", secret=None, expires_in=None):
        used_secret = secret if secret is not None else settings.NEXTAUTH_SECRET
        if expires_in is not None:
            exp_time = datetime.utcnow() + timedelta(seconds=expires_in)
        else:
            exp_time = datetime.utcnow() + timedelta(hours=1)
        payload = {
            "sub": email,
            "email": email,
            "role": role,
            "iat": datetime.utcnow(),
            "exp": exp_time
        }
        return jwt.encode(payload, used_secret, algorithm="HS256")
    return _make_token

@pytest.fixture
def admin_headers(make_token):
    return {"Authorization": f"Bearer {make_token(role='admin')}"}
