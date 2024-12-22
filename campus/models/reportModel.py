from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from ..database import Base
from datetime import datetime
from sqlalchemy.orm import relationship


class ReportModel(Base):
    __tablename__ = "reports"
    report_id: int = Column(Integer, primary_key=True, autoincrement=True)
    student_id: int = Column(Integer, ForeignKey("students.student_id"))
    post_id: int = Column(Integer, ForeignKey("posts.post_id"))
    comment_id: int = Column(Integer, ForeignKey("comments.comment_id"))
    entity_type: str = Column(String(255))  # if it is a post or comment
    reason: str = Column(String(1000))
    status: str = Column(String(255), default="pending")
    created_at: datetime = Column(DateTime, server_default=func.now())
    updated_at: datetime = Column(
        DateTime, server_default=func.now(), onupdate=func.now())

    posts = relationship("PostModel", back_populates="reports")
    comments = relationship("CommentModel", back_populates="reports")
    students = relationship("StudentModel", back_populates="reports")
