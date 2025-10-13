# models.py
# Default User model and an AbstractUser for inheritance (like Django's AbstractUser).
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, String, Boolean


class AbstractUser(SQLModel):
    """
    Base fields for user. This is meant to be inherited by a concrete User model.
    Developers can extend this class to add more fields.
    """

    username: str = Field(
        index=True,
        nullable=False,
        sa_column=Column(String, unique=True, nullable=False),
    )
    email: str = Field(
        index=True,
        nullable=False,
        sa_column=Column(String, unique=True, nullable=False),
    )
    hashed_password: str = Field(nullable=False)
    is_active: bool = Field(
        default=True, nullable=False, sa_column=Column(Boolean, default=True)
    )
    is_superuser: bool = Field(
        default=False, nullable=False, sa_column=Column(Boolean, default=False)
    )


class User(AbstractUser, table=True):
    """
    Default concrete User model used by the admin package.
    If the project wants to customize the user, they can subclass AbstractUser
    and register their custom model instead of this one.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
