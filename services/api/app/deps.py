from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import FamilyProfile, Provider, User
from app.security import read_token

bearer = HTTPBearer(auto_error=False)


def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Sign in required")
    payload = read_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Session expired")
    user = db.get(User, int(payload["sub"]))
    if user is None or user.status != "active":
        raise HTTPException(status_code=401, detail="Account is not active")
    return user


def require_family(user: User = Depends(current_user), db: Session = Depends(get_db)) -> tuple[User, FamilyProfile]:
    if user.role != "family" or user.family is None:
        raise HTTPException(status_code=403, detail="Family account required")
    if not user.email_verified:
        raise HTTPException(status_code=403, detail="Verify email before this action")
    return user, user.family


def require_provider(user: User = Depends(current_user)) -> tuple[User, Provider]:
    if user.role != "provider" or user.provider is None:
        raise HTTPException(status_code=403, detail="Provider account required")
    return user, user.provider


def require_admin(user: User = Depends(current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin account required")
    return user
