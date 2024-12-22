from sqlalchemy import Column, Integer, String, DateTime, func, Text, ForeignKey, Index
from sqlalchemy.orm import relationship

from ..database import Base


class PostModel(Base):
    __tablename__ = "posts"
    post_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey(
        "students.student_id"), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.group_id"), nullable=False)
    description = Column(String(1000), nullable=False)
    details = Column(Text, nullable=True)  # Using Text for longer content
    image = Column(String(255), nullable=True)  # image url
    vote_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(),
                        onupdate=func.now())

    students = relationship('StudentModel', back_populates="posts")
    groups = relationship("GroupModel", back_populates="posts")
    comments = relationship("CommentModel", back_populates="posts")
    student_post_votes = relationship(
        "StudentPostVoteModel", back_populates="posts")
    reports = relationship("ReportModel", back_populates="posts")
    # Optional: Add an index for frequently queried columns
    __table_args__ = (
        Index('idx_student_id', 'student_id'),
        Index('idx_group_id', 'group_id'),
    )
