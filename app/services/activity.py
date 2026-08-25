from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.activity import Activity, ActivityStatus, ActivityPriority
from app.models.club import ClubMember, ClubRole
from app.models.user import User
from app.schemas.activity import ActivityCreate, ActivityUpdate

# Hàm helper kiểm tra user có thuộc club hay không
def check_club_membership(db: Session, club_id: int, user_id: int) -> ClubMember:
    member = (
        db.query(ClubMember)
        .filter(ClubMember.club_id == club_id, ClubMember.user_id == user_id)
        .first()
    )
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không phải thành viên của câu lạc bộ này",
        )
    return member

# 1. Tạo hoạt động câu lạc bộ
def create_activity(
    db: Session, club_id: int, activity_in: ActivityCreate, current_user: User
) -> Activity:
    check_club_membership(db, club_id, current_user.id)

    # Kiểm tra assignee nếu có
    if activity_in.assignee_id:
        assignee_member = (
            db.query(ClubMember)
            .filter(
                ClubMember.club_id == club_id,
                ClubMember.user_id == activity_in.assignee_id,
            )
            .first()
        )
        if not assignee_member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Người được gán việc không thuộc câu lạc bộ này",
            )

    new_activity = Activity(
        title=activity_in.title.strip(),
        description=activity_in.description,
        due_date=activity_in.due_date,
        priority=activity_in.priority,
        club_id=club_id,
        created_by_id=current_user.id,
        assignee_id=activity_in.assignee_id,
    )
    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)
    return new_activity

# 2. Lấy danh sách hoạt động (Filter, Search, Sort, Pagination)
def get_club_activities(
    db: Session,
    club_id: int,
    current_user: User,
    status_filter: ActivityStatus | None = None,
    priority_filter: ActivityPriority | None = None,
    assignee_id: int | None = None,
    search: str | None = None,
    sort_by: str = "created_at",
    order: str = "desc",
    page: int = 1,
    size: int = 10,
) -> list[Activity]:
    check_club_membership(db, club_id, current_user.id)

    query = db.query(Activity).filter(Activity.club_id == club_id)

    # Filter & Search
    if status_filter:
        query = query.filter(Activity.status == status_filter)
    if priority_filter:
        query = query.filter(Activity.priority == priority_filter)
    if assignee_id:
        query = query.filter(Activity.assignee_id == assignee_id)
    if search:
        query = query.filter(Activity.title.ilike(f"%{search.strip()}%"))

    # Sort
    sort_column = getattr(Activity, sort_by, Activity.created_at)
    if order.lower() == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Pagination
    offset = (page - 1) * size
    return query.offset(offset).limit(size).all()

# 3. Xem chi tiết hoạt động
def get_activity_detail(db: Session, activity_id: int, current_user: User) -> Activity:
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Hoạt động không tồn tại"
        )

    # Chặn 403 nếu user không ở trong club đó
    check_club_membership(db, activity.club_id, current_user.id)
    return activity

# 4. Cập nhật hoạt động
def update_activity(
    db: Session, activity_id: int, activity_in: ActivityUpdate, current_user: User
) -> Activity:
    activity = get_activity_detail(db, activity_id, current_user)

    # Phân quyền: OWNER, Người tạo hoặc Assignee được sửa
    is_owner = (
        db.query(ClubMember)
        .filter(
            ClubMember.club_id == activity.club_id,
            ClubMember.user_id == current_user.id,
            ClubMember.role == ClubRole.OWNER,
        )
        .first()
    )

    if not (
        is_owner
        or activity.created_by_id == current_user.id
        or activity.assignee_id == current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền cập nhật hoạt động này",
        )

    # Kiểm tra assignee mới
    if activity_in.assignee_id is not None:
        assignee_member = (
            db.query(ClubMember)
            .filter(
                ClubMember.club_id == activity.club_id,
                ClubMember.user_id == activity_in.assignee_id,
            )
            .first()
        )
        if not assignee_member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Người được gán việc không thuộc câu lạc bộ này",
            )

    # Cập nhật partial
    update_data = activity_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(activity, field, value)

    db.commit()
    db.refresh(activity)
    return activity

# 5. Xóa hoạt động
def delete_activity(db: Session, activity_id: int, current_user: User) -> None:
    activity = get_activity_detail(db, activity_id, current_user)

    is_owner = (
        db.query(ClubMember)
        .filter(
            ClubMember.club_id == activity.club_id,
            ClubMember.user_id == current_user.id,
            ClubMember.role == ClubRole.OWNER,
        )
        .first()
    )

    if not (is_owner or activity.created_by_id == current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ OWNER hoặc người tạo mới được xóa hoạt động này",
        )

    db.delete(activity)
    db.commit()