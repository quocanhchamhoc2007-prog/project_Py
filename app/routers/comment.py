from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.security import get_current_user # dependency lấy user đăng nhập
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentResponse
from app.services import comment as comment_service

router = APIRouter(prefix="/activities/{activity_id}/comments", tags=["Comments"])


@router.post("", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    activity_id: int,
    comment_in: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Tạo comment mới cho hoạt động (Chỉ thành viên CLB)"""
    return comment_service.create_comment(
        db=db, activity_id=activity_id, comment_in=comment_in, current_user=current_user
    )


@router.get("", response_model=List[CommentResponse])
def get_comments(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lấy danh sách comment của hoạt động (Chỉ thành viên CLB)"""
    return comment_service.get_activity_comments(
        db=db, activity_id=activity_id, current_user=current_user
    )