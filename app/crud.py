from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from datetime import datetime, timedelta
from typing import Optional
import uuid

from app import models, schemas, auth
from app.models import EmailVerification


# User CRUD operations
async def get_user_by_email(db: AsyncSession, email: str) -> Optional[models.User]:
    result = await db.execute(
        select(models.User).where(models.User.email == email)
    )
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[models.User]:
    result = await db.execute(
        select(models.User).where(models.User.username == username)
    )
    return result.scalar_one_or_none()


async def get_user_by_public_id(db: AsyncSession, public_id: str) -> Optional[models.User]:
    result = await db.execute(
        select(models.User).where(models.User.public_id == public_id)
    )
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user_data: schemas.UserCreate) -> models.User:
    # Check if user exists
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise ValueError("User with this email already exists")

    existing_username = await get_user_by_username(db, user_data.username)
    if existing_username:
        raise ValueError("User with this username already exists")

    # Create user
    hashed_password = auth.get_password_hash(user_data.password)
    verification_token = str(uuid.uuid4())
    token_expires = datetime.utcnow() + timedelta(hours=24)

    db_user = models.User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        verification_token=verification_token,
        verification_token_expires=token_expires
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return db_user


async def verify_user_email(db: AsyncSession, token: str) -> bool:
    result = await db.execute(
        select(models.User).where(
            models.User.verification_token == token,
            models.User.verification_token_expires > datetime.utcnow()
        )
    )

    user = result.scalar_one_or_none()
    if not user:
        return False

    user.is_verified = True
    user.verification_token = None
    user.verification_token_expires = None

    await db.commit()
    return True


async def update_password(db: AsyncSession, user: models.User, new_password: str) -> None:
    user.hashed_password = auth.get_password_hash(new_password)
    user.reset_token = None
    user.reset_token_expires = None
    await db.commit()


async def create_email_verification(db: AsyncSession, email: str) -> EmailVerification:
    """Создает запись для подтверждения email"""
    # Удаляем старые верификации
    await db.execute(
        delete(EmailVerification).where(EmailVerification.email == email)
    )

    # Создаем новую
    verification = EmailVerification.create_for_email(email)
    db.add(verification)
    await db.commit()
    await db.refresh(verification)
    return verification


async def verify_email_token(db: AsyncSession, token: str) -> bool:
    """Проверяет токен подтверждения email"""
    result = await db.execute(
        select(EmailVerification).where(
            EmailVerification.token == token,
            EmailVerification.expires_at > datetime.utcnow(),
            EmailVerification.is_used is False
        )
    )

    verification = result.scalar_one_or_none()
    if not verification:
        return False

    # Помечаем как использованный
    verification.is_used = True

    # Находим пользователя и активируем его
    result = await db.execute(
        select(models.User).where(models.User.email.is_(verification.email))
    )
    user = result.scalar_one_or_none()

    if user:
        user.is_verified = True
        await db.commit()
        return True

    return False
