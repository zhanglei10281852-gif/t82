from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta
from app.database import get_db
from app import models, schemas
from app.auth import verify_password, create_access_token, get_current_user, hash_password, require_admin
from app.config import settings

router = APIRouter()


@router.get("/users", response_model=List[schemas.UserResponse])
def list_users(
    role: models.UserRole = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    query = db.query(models.User)
    if role:
        query = query.filter(models.User.role == role)
    return query.all()


@router.post("/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user


@router.post("/register", response_model=schemas.UserResponse)
def register(user_create: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.username == user_create.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = models.User(
        username=user_create.username,
        password_hash=hash_password(user_create.password),
        role=user_create.role,
        full_name=user_create.full_name,
        phone=user_create.phone
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
