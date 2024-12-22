from sqlalchemy import Column, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from ..database import Base


class StudentPostVoteModel(Base):
    __tablename__ = "student_post_votes"

    student_post_vote_id = Column(
        Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey(
        "students.student_id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.post_id"), nullable=False)
    # 1 for upvote, -1 for downvote
    vote_value = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(),
                        onupdate=func.now())

    students = relationship(
        "StudentModel", back_populates="student_post_votes")
    posts = relationship("PostModel", back_populates="student_post_votes")
