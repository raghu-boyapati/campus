from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .studentSchema import StudentResponse
from .groupSchema import GroupResponse


class PostBase(BaseModel):
    student_id: int = Field(..., description="Student identifier")
    group_id: int = Field(..., description="Group identifier")
    description: str = Field(..., max_length=1000,
                             description="Post description")
    details: Optional[str] = Field(None, description="Additional post details")
    image: Optional[str] = Field(None, max_length=255, description="Image URL")
    vote_count: Optional[int] = Field(
        None, description="count of votes for post")


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    student_id: Optional[str] = None
    group_id: Optional[str] = None
    description: Optional[str] = Field(None, max_length=1000)
    details: Optional[str] = None
    image: Optional[str] = Field(None, max_length=255)


class PostResponse(PostBase):
    post_id: int
    created_at: datetime
    updated_at: datetime

    # Optional: Include related data
    students: StudentResponse = None
    groups: GroupResponse = None

    class Config:
        orm_mode = True
