from passlib.context import CryptContext
from fastapi import Request, HTTPException
from fastapi_admin.models import User
from typing import Optional
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash the plaintext password.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against the stored hash.
    """
    return pwd_context.verify(plain_password, hashed_password)
