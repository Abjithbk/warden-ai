from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.api.deps import get_current_user
from backend.core.security import create_access_token
from backend.db.session import get_db
from backend.models.user import User
from backend.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserOut
from backend.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    return auth_service.register_user(db, body.email, body.password)


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = auth_service.authenticate_user(db, body.email, body.password)
    return TokenResponse(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user