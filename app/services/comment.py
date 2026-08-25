from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.activity import Activity
from app.models.club import ClubMember
from app.models.comment import Comment
from app.models.user import User
from app.schemas.comment import CommentCreate


def check_activity_membership(db: Session, activity_id: int, user_id: int) -> Activity:
    # Lấy activity để lấy club_id
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hoạt động không tồn tại",
        )

    # Kiểm tra user có thuộc club của activity đó không
    is_member = (
        db.query(ClubMember)
        .filter(ClubMember.club_id == activity.club_id, ClubMember.user_id == user_id)
        .first()
    )
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không phải thành viên câu lạc bộ để thực hiện thao tác này",
        )
    return activity


def create_comment(
    db: Session, activity_id: int, comment_in: CommentCreate, current_user: User
) -> Comment:
    # Check quyền thành viên CLB
    check_activity_membership(db, activity_id, current_user.id)

    new_comment = Comment(
        content=comment_in.content.strip(),
        activity_id=activity_id,
        user_id=current_user.id,
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment


def get_activity_comments(
    db: Session, activity_id: int, current_user: User
) -> List[Comment]:
    # Check quyền thành viên CLB
    check_activity_membership(db, activity_id, current_user.id)

    return (
        db.query(Comment)
        .filter(Comment.activity_id == activity_id)
        .order_by(Comment.created_at.asc())
        .all()
    )