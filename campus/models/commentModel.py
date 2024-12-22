from sqlalchemy import Column, Integer, String, DateTime, Text, func, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class CommentModel(Base):
    __tablename__ = "comments"
    comment_id = Column(Integer, primary_key=True, nullable=False, index=True)
    student_id = Column(Integer, ForeignKey(
        "students.student_id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.post_id"), nullable=False)
    parent_comment_id = Column(Integer, nullable=True)
    content = Column(Text, nullable=False)
    vote_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(),
                        onupdate=func.now())

    students = relationship("StudentModel", back_populates="comments")
    posts = relationship("PostModel", back_populates="comments")
    student_comment_votes = relationship(
        "StudentCommentVoteModel", back_populates="comments")
    reports = relationship("ReportModel", back_populates="comments")
