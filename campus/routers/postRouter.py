from fastapi import APIRouter, Depends, HTTPException, status, Query
from ..schemas.postSchema import PostCreate, PostUpdate, PostResponse
from ..schemas.studentPostVoteSchema import StudentPostVoteBase, StudentPostVoteResponse
from ..models.postModel import PostModel
from ..models.studentPostVoteModel import StudentPostVoteModel
from ..models.reportModel import ReportModel
from ..schemas.reportSchema import ReportBase, ReportResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc
from sqlalchemy.exc import IntegrityError
from ..database import get_db

router = APIRouter(prefix="/api/posts", tags=["posts"])


@router.get("/", response_model=list[PostResponse])
def get_posts(db: Session = Depends(get_db),
              student_id: int = Query(
                  None, description="ID of the student to fetch posts for"),
              group_id: int = Query(
                  None, description="ID of the group to fetch posts for"),
              sort_by_votes: bool = Query(False, description="Sort posts by votes in descending order")):
    # all posts by a student in a particular group
    if group_id and student_id:
        query = db.query(PostModel).filter(
            PostModel.group_id == group_id and
            PostModel.student_id == student_id
        )
    # all posts in a group
    elif group_id:
        query = db.query(PostModel).filter(
            PostModel.group_id == group_id
        )
    # posts by a student
    elif student_id:
        query = db.query(PostModel).filter(
            PostModel.student_id == student_id
        )
    # al posts
    else:
        query = db.query(PostModel).options(
            joinedload(PostModel.students),
            joinedload(PostModel.groups)
        )

    if sort_by_votes:
        query = query.order_by(desc(PostModel.vote_count))

    all_posts = query.all()

    if not all_posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No groups found")
    return all_posts


@router.post("/", response_model=PostResponse)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    new_post = PostModel(
        student_id=post.student_id,
        group_id=post.group_id,
        description=post.description,
        details=post.details,
        image=post.image
    )

    try:
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return new_post
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error creating group: {str(e)}")


@router.patch("/{post_id}", response_model=PostResponse)
def update_post(post_id: int, update_post: PostUpdate, db: Session = Depends(get_db)):
    existing_post = db.query(PostModel).filter(
        PostModel.post_id == post_id
    ).first()

    if not existing_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {post_id} not found")

    update_items = update_post.model_dump(exclude_unset=True)
    for key, value in update_items.items():
        setattr(existing_post, key, value)

    try:
        db.commit()
        db.refresh(existing_post)
        return existing_post
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Update failed. Possibly duplicate email."
        )


@router.delete("/{post_id}", response_model=PostResponse)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    delete_post = db.query(PostModel).filter(
        PostModel.post_id == post_id
    ).first()

    if not delete_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {post_id} not found")

    try:
        db.delete(delete_post)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error deleting post: {str(e)}")


@router.get("/search")
def search_posts(
    query: str = None,
    db: Session = Depends(get_db),
    limit: int = 20
):
    if not query:
        raise HTTPException(status_code=400, detail="Search query is required")

    search_posts = (
        db.query(PostModel)
        .filter(
            func.lower(PostModel.details).contains(func.lower(query)) |
            func.lower(PostModel.description).contains(func.lower(query))
        )
        .limit(limit)
        .all()
    )

    return search_posts


@router.get("/{post_id}", response_model=PostResponse)
def get_post_by_id(post_id: int, db: Session = Depends(get_db)):
    post_by_id = db.quer(PostModel).filter(
        PostModel.post_id == post_id
    ).all()

    if not post_by_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            message=f"Post by post_id {post_id} not found")

    return post_by_id


@router.post("/{post_id}/votes", response_model=StudentPostVoteResponse)
def add_vote_to_post(post_id: int, post_vote: StudentPostVoteBase, db: Session = Depends(get_db)):
    # student_id is later from session

    post_exists = db.query(PostModel).filter(
        PostModel.post_id == post_id
    ).first()

    if not post_exists:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            message=" Post not found")

    vote_exists = db.query(StudentPostVoteModel).filter_by(
        student_id=post_vote.student_id, post_id=post_id
    ).first()

    # increment vote_count in comments table
    if post_vote.vote_value not in (1, -1):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid vote value. Must be 1 or -1."
        )
    else:

        if post_exists.vote_count:
            post_exists.vote_count += post_vote.vote_value
        else:
            post_exists.vote_count = post_vote.vote_value

    try:
        if not vote_exists:
            # create a row in the student_comment_votes table
            new_student_post_vote = StudentPostVoteModel(
                student_id=post_vote.student_id,
                post_id=post_vote.post_id,
                vote_value=post_vote.vote_value
            )
            db.add(new_student_post_vote)
            db.commit()
            db.refresh(new_student_post_vote)
            db.refresh(post_exists)
            return new_student_post_vote
        else:
            vote_exists.vote_value = post_vote.vote_value
            db.commit()
            db.refresh(vote_exists)
            return vote_exists
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error creating vote for post {post_id}: {str(e)}")


# report post
@router.post("/{post_id}/report", response_model=ReportResponse)
def report_post(post_id: int, report: ReportBase, db: Session = Depends(get_db)):
    post_exists = db.query(PostModel).filter(
        PostModel.post_id == post_id
    ).first()

    if not post_exists:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            message="Post not found")

    new_report_post = ReportModel(
        student_id=report.student_id,
        post_id=report.post_id,
        entity_type="post",
        reason=report.reason
    )

    try:
        db.add(new_report_post)
        db.commit()
        db.refresh(new_report_post)
        return new_report_post
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error creating report for post {post_id}: {str(e)}")
