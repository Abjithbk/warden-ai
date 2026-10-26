from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.core.security import hash_password, verify_password
from backend.models.user import User


def register_user(db: Session, email: str, password: str) -> User:
    email = email.lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Email already registered")
    user = User(email=email, hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = db.scalar(select(User).where(User.email == email.lower()))
    # Same error for "no such user" and "wrong password" so attackers can't tell which emails exist
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Account is disabled")
    return user