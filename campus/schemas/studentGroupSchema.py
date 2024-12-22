from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from ..schemas.studentSchema import StudentResponse
from ..schemas.groupSchema import GroupResponse


class StudentGroupBase(BaseModel):
    student_id: int = Field(...,
                            description="student id for group subscription")
    group_id: int = Field(..., description="group id for group subscription")
    is_subscribed: bool = Field(
        None, description="student is subscribed to a group")


class StudentGroupResponse(StudentGroupBase):
    student_group_id: int
    is_subscribed: bool
    created_at: datetime
    updated_at: datetime

    students: StudentResponse = None
    groups: GroupResponse = None

    class Config:
        orm_mode = True
