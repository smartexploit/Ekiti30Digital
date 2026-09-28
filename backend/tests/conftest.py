import pytest
import os
os.environ["SECRET_KEY"] = "your-very-secure-and-sufficiently-long-secret-key-for-testing-purposes-32bytes"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.session import get_db
from app.models.contributor import ContributorAccount
from app.db.base import Base
import jwt

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function", autouse=True)
def db_session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # Seed default test users
    admin_user = ContributorAccount(
        email="admin@example.com",
        full_name="Admin User",
        hashed_password="hashed_password_placeholder",
        is_active=True,
        is_admin=True,
        is_superuser=True,
        role="admin"
    )
    superuser = ContributorAccount(
        email="superuser@example.com",
        full_name="Super User",
        hashed_password="hashed_password_placeholder",
        is_active=True,
        is_admin=True,
        is_superuser=True,
        role="admin"
    )
    contributor_user = ContributorAccount(
        email="contributor@example.com",
        full_name="Contributor User",
        hashed_password="hashed_password_placeholder",
        is_active=True,
        is_admin=False,
        role="contributor"
    )
    contributor_user2 = ContributorAccount(
        email="user2@example.com",
        full_name="Contributor Two",
        hashed_password="hashed_password_placeholder",
        is_active=True,
        is_admin=False,
        role="contributor"
    )
    db.add_all([admin_user, superuser, contributor_user, contributor_user2])
    db.commit()
    
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def override_get_db(db_session):
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def client(override_get_db):
    with TestClient(app) as c:
        yield c

@pytest.fixture
def make_token():
    def _make_token(sub: str = "contributor@example.com", role: str = "contributor", is_admin: bool = False):
        secret = os.getenv("SECRET_KEY", "your-very-secure-and-sufficiently-long-secret-key-for-testing-purposes-32bytes")
        payload = {"sub": sub, "email": sub, "role": role, "is_admin": is_admin}
        return jwt.encode(payload, secret, algorithm="HS256")
    return _make_token

@pytest.fixture
def admin_token_headers(client, make_token):
    token = make_token(sub="admin@example.com", role="admin", is_admin=True)
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def superuser_token_headers(client, make_token):
    token = make_token(sub="superuser@example.com", role="admin", is_admin=True)
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def contributor_token_headers(client, make_token):
    token = make_token(sub="contributor@example.com", role="contributor", is_admin=False)
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def normal_user_token_headers(contributor_token_headers):
    return contributor_token_headers

@pytest.fixture
def auth_headers(contributor_token_headers):
    return contributor_token_headers

@pytest.fixture
def admin_headers(admin_token_headers):
    return admin_token_headers
