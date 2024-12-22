from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..database import get_db
from ..models.studentModel import StudentModel
from ..schemas.studentSchema import StudentCreate, StudentUpdate,  StudentResponse
from ..exceptions import StudentNotFoundException, InvalidCredentialsException

router = APIRouter(prefix="/api/students", tags=["students"])


@router.get("/", response_model=list[StudentResponse])
def get_all_students(db: Session = Depends(get_db)):
    students = db.query(StudentModel).all()
    return students


@router.post("/", response_model=StudentResponse, status_code=201)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    try:
        db_student = StudentModel(
            name=student.name,
            email=student.email
        )
        db_student.set_password(student.password)

        db.add(db_student)
        db.commit()
        db.refresh(db_student)
        return db_student
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="A student with this email already exists"
        )


@router.post("/verify", response_model=StudentResponse)
def verify_student(student: StudentCreate, db: Session = Depends(get_db)):
    existing_student = (
        db.query(StudentModel)
        .filter(
            (StudentModel.name == student.name) |
            (StudentModel.email == student.email)
        )
        .first()
    )

    if not existing_student:
        raise StudentNotFoundException()

    if not existing_student.check_password(student.password):
        raise InvalidCredentialsException()

    return existing_student


@router.patch("/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: int,
    student_update: StudentUpdate,
    db: Session = Depends(get_db)
):
    # Find the existing student
    db_student = db.query(StudentModel).filter(
        StudentModel.student_id == student_id).first()

    if not db_student:
        raise StudentNotFoundException()

    # Update fields only if they are provided
    update_data = student_update.model_dump(exclude_unset=True)

    # Handle password update separately
    if 'password' in update_data:
        db_student.set_password(update_data.pop('password'))

    # Update other fields
    for key, value in update_data.items():
        setattr(db_student, key, value)

    try:
        db.commit()
        db.refresh(db_student)
        return db_student
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Update failed. Possibly duplicate email."
        )


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(
    student_id: int,
    db: Session = Depends(get_db)
):
    # Find the existing student
    db_student = db.query(StudentModel).filter(
        StudentModel.student_id == student_id).first()

    if not db_student:
        raise StudentNotFoundException()

    try:
        db.delete(db_student)
        db.commit()
        # Returns no content (204) on successful deletion
        return None
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting student: {str(e)}"
        )
