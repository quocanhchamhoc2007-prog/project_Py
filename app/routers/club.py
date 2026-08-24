from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.models.user import User
from app.schemas.club import ClubCreate, ClubUpdate, ClubResponse, AddMemberRequest, MemberResponse
from app.dependencies.auth import get_current_user

# Import các hàm trực tiếp từ file service
from app.services import club as club_service

router = APIRouter(prefix="/clubs", tags=["Clubs"])

@router.post("", response_model=ClubResponse, status_code=status.HTTP_201_CREATED)
def create_club(
    club_in: ClubCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return club_service.create_club(db, club_in, current_user)

@router.get("", response_model=List[ClubResponse])
def get_my_clubs(
    search: Optional[str] = Query(None, description="Tìm kiếm theo tên câu lạc bộ"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return club_service.get_my_clubs(db, current_user, search)

@router.get("/{id}", response_model=ClubResponse)
def get_club_detail(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return club_service.get_club_detail(db, id, current_user)

@router.put("/{id}", response_model=ClubResponse)
def update_club(
    id: int,
    club_in: ClubUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return club_service.update_club(db, id, club_in, current_user)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_club(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    club_service.delete_club(db, id, current_user)
    return None

@router.post("/{id}/members", status_code=status.HTTP_201_CREATED)
def add_member(
    id: int,
    payload: AddMemberRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    club_service.add_member(db, id, payload, current_user)
    return {"message": "Thêm thành viên thành công"}

@router.delete("/{id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(
    id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    club_service.remove_member(db, id, user_id, current_user)
    return None

@router.get("/{id}/members", response_model=List[MemberResponse])
def get_club_members(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return club_service.get_club_members(db, id, current_user)