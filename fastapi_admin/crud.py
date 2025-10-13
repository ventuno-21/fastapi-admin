# Basic CRUD helpers for dynamic models and User-specific functions.
from typing import Any, Optional, List
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import User
from .security import hash_password


async def get_user_by_username_or_email(
    db: AsyncSession, username_or_email: str
) -> Optional[User]:
    """
    Return a user by username or email.
    """
    q = select(User).where(
        (User.username == username_or_email) | (User.email == username_or_email)
    )
    res = await db.execute(q)
    return res.scalars().first()


async def get_user(db: AsyncSession, user_id: int) -> Optional[User]:
    q = select(User).where(User.id == user_id)
    res = await db.execute(q)
    return res.scalars().first()


async def create_user(
    db: AsyncSession,
    username: str,
    email: str,
    password: str,
    is_superuser: bool = False,
) -> User:
    """
    Create and return a new User (commits and refreshes).
    """
    hashed = hash_password(password)
    user = User(
        username=username,
        email=email,
        hashed_password=hashed,
        is_superuser=is_superuser,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


# Generic helpers for dynamic models (list/find/create/update/delete)
async def list_model(
    db: AsyncSession, model: Any, limit: int = 100, offset: int = 0
) -> List[Any]:
    q = select(model).offset(offset).limit(limit)
    res = await db.execute(q)
    return res.scalars().all()


async def get_model_instance(
    db: AsyncSession, model: Any, pk_name: str, pk_value: Any
) -> Optional[Any]:
    q = select(model).where(getattr(model, pk_name) == pk_value)
    res = await db.execute(q)
    return res.scalars().first()


async def create_model_instance(db: AsyncSession, model: Any, data: dict) -> Any:
    obj = model(**data)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def update_model_instance(db: AsyncSession, instance: Any, data: dict) -> Any:
    for k, v in data.items():
        setattr(instance, k, v)  # equals instance.k = v
    db.add(instance)
    await db.commit()
    await db.refresh(instance)
    return instance


async def delete_model_instance(db: AsyncSession, instance: Any) -> None:
    await db.delete(instance)
    await db.commit()
