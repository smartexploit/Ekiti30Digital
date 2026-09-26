import os
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.models.base import get_db
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)

def get_current_admin_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Fail-closed check if secret key/NextAuth secret is missing
    secret = getattr(settings, "NEXTAUTH_SECRET", None) or os.getenv("NEXTAUTH_SECRET") or os.getenv("JWT_SECRET_KEY") or os.getenv("SECRET_KEY")
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service misconfigured"
        )

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        role = payload.get("role") or payload.get("user_role") or "admin"
        
        if role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The user doesn't have enough privileges",
            )
            
        class AdminUser:
            email = payload.get("email", "admin@example.com")
            is_admin = True
            is_superuser = True

        return AdminUser()

    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
