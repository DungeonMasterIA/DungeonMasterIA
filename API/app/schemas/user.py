import uuid
from datetime import datetime

from pydantic import ConfigDict
from fastapi_users import schemas


class UserCreate(schemas.BaseUserCreate):
    name: str


class UserUpdate(schemas.BaseUserUpdate):
    name: str | None = None


class UserRead(schemas.BaseUser[uuid.UUID]):
    id: uuid.UUID
    name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
