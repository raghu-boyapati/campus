from sqlalchemy import Column, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from ..database import Base


class StudentCommentVoteModel(Base):
    __tablename__ = "student_comment_votes"

    student_comment_vote_id = Column(
        Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey(
        "students.student_id"), nullable=False)
    comment_id = Column(Integer, ForeignKey(
        "comments.comment_id"), nullable=False)
    # 1 for upvote, -1 for downvote
    vote_value = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(),
                        onupdate=func.now())

    students = relationship(
        "StudentModel", back_populates="student_comment_votes")
    comments = relationship(
        "CommentModel", back_populates="student_comment_votes")
