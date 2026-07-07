from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.user import ROLE_USER, User
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


def _auth_response(user: User) -> AuthResponse:
    token = create_access_token(user.id, user.role)
    return AuthResponse(access_token=token, user=UserRead.model_validate(user))


@router.post("/register", response_model=AuthResponse, status_code=201, summary="Create a new account")
def register(body: RegisterRequest, db: Session = Depends(get_db)) -> AuthResponse:
    email = body.email.strip().lower()
    existing = db.scalar(select(User).where(func.lower(User.email) == email))
    if existing:
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    user = User(
        email=email,
        full_name=body.full_name.strip(),
        hashed_password=hash_password(body.password),
        role=ROLE_USER,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _auth_response(user)


@router.post("/login", response_model=AuthResponse, summary="Log in with email and password")
def login(body: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    email = body.email.strip().lower()
    user = db.scalar(select(User).where(func.lower(User.email) == email))
    if not user or not user.is_active or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return _auth_response(user)


@router.get("/me", response_model=UserRead, summary="Current authenticated user")
def me(user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(user)
