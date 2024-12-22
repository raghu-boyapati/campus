from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class StudentCommentVoteBase(BaseModel):
    student_id: int = Field(..., description="student_id for comment vote")
    comment_id: int = Field(..., description="comment_id for comment vote")
    vote_value: int = Field(..., description="vote value for comment vote")


class StudentCommentVoteResponse(StudentCommentVoteBase):
    student_comment_vote_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
