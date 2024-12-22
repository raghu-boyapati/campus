from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc
from ..database import get_db
from ..schemas.commentSchema import CommentCreate, CommentUpdate, CommentResponse
from ..models.commentModel import CommentModel
from ..models.studentCommentVoteModel import StudentCommentVoteModel
from ..schemas.studentCommentVoteSchema import StudentCommentVoteBase, StudentCommentVoteResponse
from ..models.reportModel import ReportModel
from ..schemas.reportSchema import ReportBase, ReportResponse
from ..exceptions import CommentNotFound
router = APIRouter(prefix="/api/comments", tags=["comments"])


@router.get("/", response_model=list[CommentResponse])
def get_comments(db: Session = Depends(get_db),
                 student_id: int = Query(
        None, description="ID of the student to fetch comments for"),
        post_id: int = Query(
        None, description="ID of the post to fetch comments for"),
        sort_by_votes: bool = Query(False, description="Sort comments by votes in descending order")):
    if student_id and post_id:
        query = db.query(CommentModel).filter(
            CommentModel.student_id == student_id and CommentModel.post_id == post_id
        )

    elif student_id:
        query = db.query(CommentModel).filter(
            CommentModel.student_id == student_id and CommentModel.post_id == post_id
        )
    elif post_id:
        query = db.query(CommentModel).filter(
            CommentModel.student_id == student_id and CommentModel.post_id == post_id
        )
    else:
        query = db.query(CommentModel).options(joinedload(
            CommentModel.students), joinedload(CommentModel.posts))

    if sort_by_votes:
        query = query.order_by(desc(CommentModel.vote_count))
    all_comments = query.all()
    if not all_comments:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No comments found")
    return all_comments


@router.post("/", response_model=CommentResponse)
def create_comment(comment: CommentUpdate, db: Session = Depends(get_db)):
    new_comment = CommentModel(
        student_id=comment.student_id,
        post_id=comment.post_id,
        parent_comment_id=comment.parent_comment_id,
        content=comment.content
    )

    try:
        db.add(new_comment)
        db.commit()
        db.refresh(new_comment)
        return new_comment
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error creating comment: {str(e)}")


@router.patch("/{comment_id}", response_model=CommentResponse)
def update_comment(comment_id: int, comment: CommentUpdate, db: Session = Depends(get_db)):
    existing_comment = db.query(CommentModel).filter(
        CommentModel.comment_id == comment_id
    ).first()

    if not existing_comment:
        raise CommentNotFound()

    update_comment = comment.model_dump(exclude_unset=True)

    for key, value in update_comment.items():
        setattr(existing_comment, key, value)

    try:
        db.commit()
        db.refresh(existing_comment)
        return existing_comment
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Update failed. Possibly duplicate comment."
        )


@router.delete("/{comment_id}")
def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    existing_comment = db.query(CommentModel).filter(
        CommentModel.comment_id == comment_id
    ).first()

    if not existing_comment:
        raise CommentNotFound()
    try:
        db.delete(existing_comment)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting comment: {str(e)}"
        )

# vote for a comment


@router.post("/{comment_id}/votes", response_model=StudentCommentVoteResponse)
def add_vote_to_comment(comment_id: int, comment_vote: StudentCommentVoteBase, db: Session = Depends(get_db)):
    # student_id is later from session

    comment_exists = db.query(CommentModel).filter(
        CommentModel.comment_id == comment_id
    ).first()

    if not comment_exists:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            message=" Comment not found")

    vote_exists = db.query(StudentCommentVoteModel).filter_by(
        student_id=comment_vote. student_id, comment_id=comment_id
    ).first()

    # increment vote_count in comments table
    if comment_vote.vote_value not in (1, -1):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid vote value. Must be 1 or -1."
        )
    else:
        if comment_exists.vote_count:
            comment_exists.vote_count += comment_vote.vote_value
        else:
            comment_exists.vote_count = comment_vote.vote_value

    try:
        if not vote_exists:
            # create a row in the student_comment_votes table
            new_student_comment_vote = StudentCommentVoteModel(
                student_id=comment_vote.student_id,
                comment_id=comment_vote.comment_id,
                vote_value=comment_vote.vote_value
            )
            db.add(new_student_comment_vote)
            db.commit()
            db.refresh(new_student_comment_vote)
            return new_student_comment_vote
        else:
            vote_exists.vote_value = comment_vote.vote_value
            db.commit()
            db.refresh(vote_exists)
            return vote_exists
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error creating vote for comment {comment_id}: {str(e)}")


@router.post("/{comment_id}/report", response_model=ReportResponse)
def report_comment(comment_id: int, report: ReportBase, db: Session = Depends(get_db)):
    comment_exists = db.query(CommentModel).filter(
        CommentModel.comment_id == comment_id
    ).first()

    if not comment_exists:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            message="comment not found")

    new_comment_report = ReportModel(
        student_id=report.student_id,
        comment_id=report.comment_id,
        entity_type="comment",
        reason=report.reason
    )

    try:
        db.add(new_comment_report)
        db.commit()
        db.refresh(new_comment_report)
        return new_comment_report
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error creating report for comment {comment_id}: {str(e)}")
