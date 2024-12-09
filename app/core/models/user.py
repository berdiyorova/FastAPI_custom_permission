from datetime import datetime, timezone

from sqlmodel import SQLModel, Field

from app.core.constants import UserRole
from app.core.database import engine


class UserModel(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str = Field(min_length=3, max_length=100)
    email: str = Field(min_length=8, max_length=100)
    password: str = Field(min_length=8, max_length=100)
    first_name: str | None = Field(default=None, max_length=50)
    last_name: str | None = Field(default=None, max_length=50)
    age: int | None = Field(default=None, gt=0)
    is_active: bool = Field(default=False)
    created_at: datetime | None = Field(default=datetime.now(timezone.utc))
    role: str | None = Field(default=UserRole.USER)


class BlockedToken(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    token: str


async def create_user_table():
    SQLModel.metadata.create_all(bind=engine)
