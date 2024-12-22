from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
import bcrypt
from ..database import Base


class StudentModel(Base):
    __tablename__ = "students"

    student_id = Column(Integer, primary_key=True,
                        index=True, autoincrement=True)
    name = Column(String(255), index=True, nullable=False)
    email = Column(String(255), index=True, unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(),
                        onupdate=func.now())

    posts = relationship("PostModel", back_populates="students")
    comments = relationship("CommentModel", back_populates="students")
    student_groups = relationship(
        "StudentGroupModel", back_populates="students")
    student_post_votes = relationship(
        "StudentPostVoteModel", back_populates="students")
    student_comment_votes = relationship(
        "StudentCommentVoteModel", back_populates="students")
    reports = relationship("ReportModel", back_populates="students")

    def set_password(self, raw_password: str) -> None:
        """Hash and set the password."""
        # Convert password to bytes
        raw_password_bytes = raw_password.encode(
            'utf-8')  # Encode the password string to bytes
        hashed = bcrypt.hashpw(raw_password_bytes, bcrypt.gensalt())
        # Store the hash as a string in the database
        self.password = hashed.decode('utf-8')

    def check_password(self, raw_password: str) -> bool:
        """Verify the provided password against the stored hash."""
        # Convert password to bytes and compare
        raw_password_bytes = raw_password.encode('utf-8')  # Encode to bytes
        return bcrypt.checkpw(raw_password_bytes, self.password.encode('utf-8'))
