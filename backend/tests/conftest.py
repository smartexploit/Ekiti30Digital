import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import jwt

from app.main import app
from app.db.base_class import Base
from app.db.session import get_db
from app.core.config import settings
from app.models.asset import Asset
from app.models.story import Story

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function", autouse=True)
def db_session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def contributor_token():
    payload = {"sub": "test_contributor_id", "role": "contributor", "is_admin": True}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=getattr(settings, "ALGORITHM", "HS256"))
    return token

@pytest.fixture
def admin_token():
    payload = {"sub": "test_admin_id", "role": "admin", "is_admin": True}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=getattr(settings, "ALGORITHM", "HS256"))
    return token

@pytest.fixture
def normal_user_token():
    payload = {"sub": "test_user_id", "role": "contributor", "is_admin": False}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=getattr(settings, "ALGORITHM", "HS256"))
    return token

@pytest.fixture
def contributor_token_headers(contributor_token):
    return {"Authorization": f"Bearer {contributor_token}"}

@pytest.fixture
def admin_token_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}

@pytest.fixture
def normal_user_token_headers(normal_user_token):
    return {"Authorization": f"Bearer {normal_user_token}"}

@pytest.fixture
def make_token():
    """Flexible token factory supporting both calling styles used in tests:
    make_token(role="admin", sub="x", ...) and make_token({"sub": "x", ...}).
    """
    import time

    def _make(payload_dict=None, **kwargs):
        payload = dict(payload_dict) if payload_dict else {}
        payload.update(kwargs)
        payload.setdefault("sub", payload.get("email", "test_user_id"))
        payload.setdefault("email", payload.get("sub", "test_user_id") + "@example.com" if "@" not in payload.get("sub", "") else payload.get("sub"))
        payload.setdefault("role", "contributor")
        payload.setdefault("is_admin", payload.get("role") == "admin")
        now = int(time.time())
        payload.setdefault("iat", now)
        payload.setdefault("exp", now + 3600)
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=getattr(settings, "ALGORITHM", "HS256"))

    return _make

@pytest.fixture
def superuser_token_headers(admin_token_headers):
    return admin_token_headers
