from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from ..database import get_db
from ..models.groupModel import GroupModel
from ..schemas.groupSchema import GroupCreate, GroupUpdate, GroupResponse

router = APIRouter(prefix="/api/groups", tags=["groups"])


@router.get("/", response_model=List[GroupResponse], status_code=status.HTTP_200_OK)
def get_groups(db: Session = Depends(get_db)):
    """
    Retrieve all groups from the database
    """
    groups = db.query(GroupModel).all()
    if not groups:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No groups found")
    return groups


@router.post("/", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
def create_group(group: GroupCreate, db: Session = Depends(get_db)):
    """
    Create a new group in the database
    """
    # Check if a group with the same name already exists
    existing_group = db.query(GroupModel).filter(
        GroupModel.name == group.name).first()
    if existing_group:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="A group with this name already exists")

    # Create new group model instance
    new_group = GroupModel(
        name=group.name,
        description=group.description,
        is_default=group.is_default
    )

    try:
        db.add(new_group)
        db.commit()
        db.refresh(new_group)
        return new_group
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error creating group: {str(e)}")


@router.patch("/{group_id}", response_model=GroupResponse)
def update_group(
    group_id: int,
    group: GroupUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing group in the database
    """
    # Find the existing group
    existing_group = db.query(GroupModel).filter(
        GroupModel.group_id == group_id).first()
    if not existing_group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Group with id {group_id} not found")

    # Check if name is being updated and is unique
    if group.name is not None:
        name_conflict = db.query(GroupModel).filter(
            GroupModel.name == group.name,
            GroupModel.group_id != group_id
        ).first()
        if name_conflict:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="A group with this name already exists")
        existing_group.name = group.name

    # Update other fields if provided
    if group.description is not None:
        existing_group.description = group.description

    if group.is_default is not None:
        existing_group.is_default = group.is_default

    try:
        db.commit()
        db.refresh(existing_group)
        return existing_group
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error updating group: {str(e)}")


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_group(group_id: int, db: Session = Depends(get_db)):
    """
    Delete a group from the database
    """
    # Find the existing group
    group = db.query(GroupModel).filter(
        GroupModel.group_id == group_id).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Group with id {group_id} not found")

    try:
        db.delete(group)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error deleting group: {str(e)}")


@router.get("/search")
def search_groups(
    query: str = None,
    db: Session = Depends(get_db),
    limit: int = 20
):
    if not query:
        raise HTTPException(status_code=400, detail="Search query is required")

    search_groups = (
        db.query(GroupModel)
        .filter(
            func.lower(GroupModel.name).contains(func.lower(query)) |
            func.lower(GroupModel.description).contains(func.lower(query))
        )
        .limit(limit)
        .all()
    )

    return search_groups
