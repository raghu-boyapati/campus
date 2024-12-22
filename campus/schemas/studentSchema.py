from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
import re


class StudentBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr

    @validator('name')
    def validate_name(cls, v):
        if not re.match(r'^[A-Za-z\s]+$', v):
            raise ValueError('Name must contain only letters and spaces')
        return v


class StudentCreate(StudentBase):
    password: str = Field(..., min_length=8)

    @validator('password')
    def validate_password(cls, v):
        # Check for:
        # - At least 8 characters long
        # - Contains at least one letter
        # - Contains at least one number
        # - Contains at least one special character
        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~])[\w!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]{8,}$', v):
            raise ValueError(
                'Password must be at least 8 characters long and contain '
                'letters, numbers, and at least one special character'
            )
        return v


class StudentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)

    @validator('name', always=True)
    def validate_name(cls, v):
        if v is not None:
            if not re.match(r'^[A-Za-z\s]+$', v):
                raise ValueError('Name must contain only letters and spaces')
        return v

    @validator('password', always=True)
    def validate_password(cls, v):
        if v is not None:
            if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~])[\w!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]{8,}$', v):
                raise ValueError(
                    'Password must be at least 8 characters long and contain '
                    'letters, numbers, and at least one special character'
                )
        return v


class StudentResponse(StudentBase):
    student_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Updated from orm_mode
