from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class Group(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: str = Field(..., min_length=2, max_length=1000)
    is_default: bool


class GroupCreate(Group):
    pass


class GroupUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, min_length=2, max_length=1000)
    is_default: Optional[bool] = None


class GroupResponse(Group):
    group_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Updated from orm_mode
