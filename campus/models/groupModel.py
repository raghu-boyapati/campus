from sqlalchemy import Column, Integer, String, DateTime, Boolean, func
from sqlalchemy.orm import relationship
from ..database import Base


class GroupModel(Base):
    __tablename__ = "groups"

    group_id = Column(Integer, primary_key=True,
                      unique=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(String(1000), nullable=True)
    is_default = Column(Boolean, nullable=True, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(),
                        onupdate=func.now())
    posts = relationship("PostModel", back_populates="groups")
    student_groups = relationship(
        "StudentGroupModel", back_populates="groups")
