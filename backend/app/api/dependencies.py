from fastapi import Depends
from sqlalchemy.orm import Session
from app.models.base import SessionLocal
from app.core.auth import require_admin, AdminUser

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(admin: AdminUser = Depends(require_admin)):
    return {"email": admin.email, "role": "admin"}
