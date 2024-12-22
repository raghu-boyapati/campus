from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .studentSchema import StudentResponse
from .postSchema import PostResponse


class CommentBase(BaseModel):
    student_id: int = Field(..., description="student identifier")
    post_id: int = Field(..., description="post identifier")
    parent_comment_id: Optional[int] = Field(
        None, description="parent comment identifier")
    content: str = Field(..., description="comment content")
    vote_count: Optional[int] = Field(None, description="count of votes")


class CommentCreate(CommentBase):
    pass


class CommentUpdate(BaseModel):
    student_id: Optional[int] = None
    post_id: Optional[int] = None
    parent_comment_id: Optional[int] = None
    content: str = Field(..., description="comment content update")


class CommentResponse(CommentBase):
    comment_id: int
    created_at: datetime
    updated_at: datetime
    students: StudentResponse = None
    posts: PostResponse = None

    class Config:
        orm_data = True
