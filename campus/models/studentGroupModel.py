from sqlalchemy import Column, Integer, Boolean, func, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Session
from fastapi import Depends
from ..database import Base
from datetime import datetime


class StudentGroupModel(Base):
    __tablename__ = "student_groups"
    student_group_id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.student_id"))
    group_id = Column(Integer, ForeignKey("groups.group_id"))
    is_subscribed = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(),
                        onupdate=func.now())

    students = relationship("StudentModel", back_populates="student_groups")
    groups = relationship("GroupModel", back_populates="student_groups")
