from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False)

def get_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> dict:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_active_user(current_user: dict = Depends(get_current_user)) -> dict:
    return current_user

def get_current_active_contributor(current_user: dict = Depends(get_current_active_user)) -> dict:
    sub = current_user.get("sub", {})
    role = current_user.get("role") or (sub.get("role") if isinstance(sub, dict) else None)
    is_admin = current_user.get("is_admin") or current_user.get("is_superuser") or (sub.get("is_admin") if isinstance(sub, dict) else False)
    
    if role in ["contributor", "admin", "superuser", "super_admin"] or is_admin:
        return current_user
        
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="The user doesn't have enough privileges (contributor access required)",
    )

def get_current_active_superuser(current_user: dict = Depends(get_current_active_user)) -> dict:
    sub = current_user.get("sub", {})
    role = current_user.get("role") or (sub.get("role") if isinstance(sub, dict) else None)
    is_admin = current_user.get("is_admin") or current_user.get("is_superuser") or (sub.get("is_admin") if isinstance(sub, dict) else False)
    
    if isinstance(sub, dict):
        if sub.get("is_admin") is False or sub.get("role") == "contributor":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The user doesn't have enough privileges (admin access required)",
            )
            
    if role in ["admin", "superuser", "super_admin"] or is_admin:
        if role == "contributor" and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The user doesn't have enough privileges (admin access required)",
            )
        return current_user
        
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="The user doesn't have enough privileges (admin access required)",
    )

# Alias for admin route compatibility
get_current_active_admin = get_current_active_superuser
