from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from ..database import get_db

from ..schemas.studentGroupSchema import StudentGroupResponse, StudentGroupBase
from ..models.studentGroupModel import StudentGroupModel
from ..models.studentModel import StudentModel
from ..models.groupModel import GroupModel

router = APIRouter(prefix="/api/studentGroup", tags=["student groups"])


@router.get("/", response_model=list[StudentGroupResponse])
def get_student_groups(student_id: int = Query(None, description="student_id to get all the groups of a student"), db: Session = Depends(get_db)):
    if student_id:
        existing_student_groups = db.query(StudentGroupModel).filter(
            StudentGroupModel.student_id == student_id
        ).options(joinedload(GroupModel)).all()
    else:
        existing_student_groups = db.query(StudentGroupModel).all()
    if not existing_student_groups:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No student groups found")

    return existing_student_groups


@router.post("/", response_model=StudentGroupResponse)
def create_student_group(student_group: StudentGroupBase, db: Session = Depends(get_db)):
    new_student_group = StudentGroupModel(
        student_id=student_group.student_id,
        group_id=student_group.group_id,
        is_subscribed=student_group.is_subscribed
    )

    try:
        db.add(new_student_group)
        db.commit()
        db.refresh(new_student_group)
        return new_student_group
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error creating student_group: {str(e)}")


@router.patch("/{student_group_id}", response_model=StudentGroupResponse)
def update_student_group(student_group_id: int, student_group: StudentGroupBase, db: Session = Depends(get_db)):
    existing_student_group = db.query(StudentGroupModel).filter(
        StudentGroupModel.student_group_id == student_group_id
    ).first()

    if not existing_student_group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"StudentGroup with id {student_group_id} not found")

    update_student_group = student_group.model_dump(exclude_unset=True)

    for key, value in update_student_group.items():
        setattr(existing_student_group, key, value)

    try:
        db.commit()
        db.refresh(existing_student_group)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Update failed. Possibly duplicate email."
        )


@router.delete("/{student_group_id}", response_model=StudentGroupResponse)
def delete_student_group(student_group_id: int, db: Session = Depends(get_db)):
    delete_student_group = db.query(StudentGroupModel).filter(
        StudentGroupModel.student_group_id == student_group_id
    ).first()

    if not delete_student_group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"StudentGroup with id {student_group_id} not found")

    try:
        db.delete(delete_student_group)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error deleting student group: {str(e)}")


@router.post("/{group_id}/students/{student_id}", status_code=status.HTTP_201_CREATED)
def add_student_to_group(group_id: int, student_id: int, db: Session = Depends(get_db)):
    # Check if the group exists
    group = db.query(GroupModel).filter(
        GroupModel.group_id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    # Check if the student exists
    student = db.query(StudentModel).filter(
        StudentModel.student_id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    # Check if the student is already in the group
    existing_membership = db.query(StudentGroupModel).filter(
        StudentGroupModel.group_id == group_id, StudentGroupModel.student_id == student_id).first()

    if existing_membership:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Student is already in the group")

    # Create a new student-group relationship
    new_membership = StudentGroupModel(
        student_id=student_id, group_id=group_id, is_subscribed=True)
    db.add(new_membership)
    db.commit()
    db.refresh(new_membership)

    return {"message": "Student added to group successfully"}

# Remove student from a group


@router.delete("/{group_id}/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_student_from_group(group_id: int, student_id: int, db: Session = Depends(get_db)):
    # Find the student-group relationship
    membership = db.query(StudentGroupModel).filter(
        StudentGroupModel.group_id == group_id, StudentGroupModel.student_id == student_id).first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Membership not found")

    # Remove the student from the group
    db.delete(membership)
    db.commit()

    return None
