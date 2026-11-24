from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import current_user
from app.models import FamilyProfile, Provider, User
from app.security import hash_password, make_token, recovery_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=12, max_length=200)
    role: str


class LoginIn(BaseModel):
    email: str
    password: str


class RecoverIn(BaseModel):
    email: str


class ResetIn(BaseModel):
    token: str
    password: str = Field(min_length=12, max_length=200)


def _public_user(user: User) -> dict:
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "email_verified": user.email_verified,
        "status": user.status,
    }


@router.post("/register")
def register(body: RegisterIn, db: Session = Depends(get_db)):
    if body.role not in {"family", "provider"}:
        raise HTTPException(status_code=400, detail="Choose a Family or Provider account")
    email = body.email.strip().lower()
    if db.query(User).filter(User.email == email).one_or_none():
        raise HTTPException(status_code=400, detail="That email cannot be registered")
    user = User(
        email=email,
        name=body.name.strip(),
        role=body.role,
        password_hash=hash_password(body.password),
        email_verified=True,
        status="active",
    )
    db.add(user)
    db.flush()
    if body.role == "family":
        db.add(FamilyProfile(user_id=user.id))
    else:
        db.add(
            Provider(
                user_id=user.id,
                display_name=body.name.strip(),
                legal_name=body.name.strip(),
                registration_status="pending",
            )
        )
    db.commit()
    db.refresh(user)
    return {"token": make_token(user.id, user.role), "user": _public_user(user)}


@router.post("/login")
def login(body: LoginIn, db: Session = Depends(get_db)):
    email = body.email.strip().lower()
    user = db.query(User).filter(User.email == email).one_or_none()
    now = datetime.utcnow()
    if user and user.locked_until and user.locked_until > now:
        raise HTTPException(status_code=429, detail="Too many attempts. Try again in 15 minutes.")
    if user is None or not verify_password(body.password, user.password_hash) or user.status != "active":
        if user and user.status == "active":
            user.failed_logins += 1
            if user.failed_logins >= 5:
                user.locked_until = now + timedelta(minutes=15)
                user.failed_logins = 0
            db.commit()
        raise HTTPException(status_code=401, detail="Email or password is incorrect")
    user.failed_logins = 0
    user.locked_until = None
    db.commit()
    return {"token": make_token(user.id, user.role), "user": _public_user(user)}


@router.get("/me")
def me(user: User = Depends(current_user)):
    return _public_user(user)


@router.post("/recover")
def recover(body: RecoverIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email.strip().lower()).one_or_none()
    if user and user.status == "active":
        user.reset_token = recovery_token()
        user.reset_expires = datetime.utcnow() + timedelta(minutes=60)
        db.commit()
    return {"message": "If an account exists for that email, a recovery link is ready for 60 minutes."}


@router.post("/reset")
def reset_password(body: ResetIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.reset_token == body.token).one_or_none()
    now = datetime.utcnow()
    if user is None or user.reset_expires is None or user.reset_expires < now:
        raise HTTPException(status_code=400, detail="That recovery link is invalid or expired")
    user.password_hash = hash_password(body.password)
    user.reset_token = None
    user.reset_expires = None
    user.failed_logins = 0
    user.locked_until = None
    db.commit()
    return {"message": "Password updated. Sign in with the new password. Other sessions are no longer valid after you sign in again."}
