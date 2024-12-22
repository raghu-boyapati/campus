from pydantic import BaseModel, Field
from typing import Optional
from ..models.reportModel import ReportModel
from datetime import datetime


class ReportBase(BaseModel):
    student_id: int = Field(...,
                            description="student_id of the student who reported")
    post_id: Optional[int] = Field(
        None, description="post_id of the post reported")
    comment_id: Optional[int] = Field(
        None, description="comment_id of the comment reported")
    entity_type: Optional[str] = Field(None,
                                       description="entity_type of the report - either post or comment")
    reason: str = Field(...,
                        description="reason of the report - either post or comment")
    status: Optional[str] = Field(
        None, description="status of the report - pending, solved")


class ReportResponse(ReportBase):
    report_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
