from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.activity import (
    ActivityCreate,
    ActivityUpdate,
    ActivityResponse,
    ActivityStatus,
    ActivityPriority,
)
from app.services import activity as activity_service

router = APIRouter(tags=["Activities"])

@router.post(
    "/clubs/{club_id}/activities",
    response_model=ActivityResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_activity(
    club_id: int,
    activity_in: ActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return activity_service.create_activity(db, club_id, activity_in, current_user)

@router.get("/clubs/{club_id}/activities", response_model=list[ActivityResponse])
def get_club_activities(
    club_id: int,
    status: ActivityStatus | None = None,
    priority: ActivityPriority | None = None,
    assignee_id: int | None = None,
    search: str | None = None,
    sort_by: str = Query("created_at", enum=["created_at", "due_date"]),
    order: str = Query("desc", enum=["asc", "desc"]),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return activity_service.get_club_activities(
        db=db,
        club_id=club_id,
        current_user=current_user,
        status_filter=status,
        priority_filter=priority,
        assignee_id=assignee_id,
        search=search,
        sort_by=sort_by,
        order=order,
        page=page,
        size=size,
    )

@router.get("/activities/{activity_id}", response_model=ActivityResponse)
def get_activity_detail(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return activity_service.get_activity_detail(db, activity_id, current_user)

@router.patch("/activities/{activity_id}", response_model=ActivityResponse)
def update_activity(
    activity_id: int,
    activity_in: ActivityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return activity_service.update_activity(db, activity_id, activity_in, current_user)

@router.delete("/activities/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    activity_service.delete_activity(db, activity_id, current_user)
    return None