from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class StudentPostVoteBase(BaseModel):
    student_id: int = Field(..., description="student_id for post vote")
    post_id: int = Field(..., description="post_id for post vote")
    vote_value: int = Field(..., description="vote value for post vote")


class StudentPostVoteResponse(StudentPostVoteBase):
    student_post_vote_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
