from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional

from app.models.club import Club, ClubMember, ClubRole
from app.models.user import User
from app.schemas.club import ClubCreate, ClubUpdate, AddMemberRequest

# tạo mới câu lạc bộ 
def create_club(db: Session, club_in: ClubCreate, current_user: User) -> Club:
    new_club = Club(name=club_in.name.strip(), description=club_in.description,owner_id=current_user.id)
    db.add(new_club)
    db.commit()
    db.refresh(new_club)
    # tự động gán người tạo nhóm thành nhóm trưởng 
    owner_member = ClubMember(
        club_id=new_club.id, user_id=current_user.id, role=ClubRole.OWNER
    )
    db.add(owner_member)
    db.commit()
    return new_club
# xem danh sách nhóm 
def get_my_clubs(
    db: Session, current_user: User, search: Optional[str] = None) -> List[Club]:
    query = (db.query(Club).join(ClubMember).filter(ClubMember.user_id == current_user.id))

    if search:
        query = query.filter(Club.name.ilike(f"%{search.strip()}%"))
    return query.all()

# xem thông tin chi tiết một nhóm 
def get_club_detail(db: Session, club_id: int, current_user: User) -> Club:
    club = db.query(Club).filter(Club.id == club_id).first()
    if not club:
        raise HTTPException(status_code=404, detail="Câu lạc bộ không tồn tại")
    # kiểm tra xem có phải thành viên nhóm hay không
    membership = (
        db.query(ClubMember)
        .filter(ClubMember.club_id == club_id, ClubMember.user_id == current_user.id)
        .first()
    )
    if not membership:
        raise HTTPException(
            status_code=403, detail="Bạn không phải là thành viên của câu lạc bộ này"
        )

    return club

# cập nhật câu lạc bộ
def update_club(
    db: Session, club_id: int, club_in: ClubUpdate, current_user: User
) -> Club:
    club = db.query(Club).filter(Club.id == club_id).first()
    if not club:
        raise HTTPException(status_code=404, detail="Câu lạc bộ không tồn tại")
    # kiểm tra xem bạn có phải trường nhóm hay không 
    owner_check = (
        db.query(ClubMember)
        .filter(
            ClubMember.club_id == club_id,
            ClubMember.user_id == current_user.id,
            ClubMember.role == ClubRole.OWNER,
        )
        .first()
    )

    if not owner_check:
        raise HTTPException(
            status_code=403, detail="Chỉ OWNER mới có quyền cập nhật câu lạc bộ"
        )

    if club_in.name is not None:
        club.name = club_in.name.strip()
    if club_in.description is not None:
        club.description = club_in.description

    db.commit()
    db.refresh(club)
    return club

# xoá cậu lạc bộ 
def delete_club(db: Session, club_id: int, current_user: User) -> None:
    club = db.query(Club).filter(Club.id == club_id).first()
    if not club:
        raise HTTPException(status_code=404, detail="Câu lạc bộ không tồn tại")
# kiểm tra xem có phải trưởng nhóm hay không
    owner_check = (
        db.query(ClubMember)
        .filter(
            ClubMember.club_id == club_id,
            ClubMember.user_id == current_user.id,
            ClubMember.role == ClubRole.OWNER,
        )
        .first()
    )
    if not owner_check:
        raise HTTPException(
            status_code=403, detail="Chỉ OWNER mới có quyền xóa câu lạc bộ"
        )

    db.delete(club)
    db.commit()

# thêm thành viên vào nhóm 
def add_member(db: Session, club_id: int, payload: AddMemberRequest, current_user: User) -> None:
    club = db.query(Club).filter(Club.id == club_id).first()
    if not club:
        raise HTTPException(status_code=404, detail="Câu lạc bộ không tồn tại")
# kiểm tra người thêm có phải trưởng nhóm hay không
    owner_check = (
        db.query(ClubMember)
        .filter(
            ClubMember.club_id == club_id,
            ClubMember.user_id == current_user.id,
            ClubMember.role == ClubRole.OWNER,
        )
        .first()
    )
    if not owner_check:
        raise HTTPException(
            status_code=403, detail="Chỉ OWNER mới có quyền thêm thành viên"
        )
    # kiểm tra người dc thêm có tồn tại hay không 
    target_user = db.query(User).filter(User.id == payload.user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User được thêm không tồn tại")
    # kiểm tra người dc thêm đã ở trong nhóm nào chưa
    existing_member = (
        db.query(ClubMember)
        .filter(ClubMember.club_id == club_id, ClubMember.user_id == payload.user_id)
        .first()
    )
    if existing_member:
        raise HTTPException(
            status_code=400, detail="User đã là thành viên của câu lạc bộ"
        )

    new_member = ClubMember(
        club_id=club_id, user_id=payload.user_id, role=ClubRole.MEMBER
    )
    db.add(new_member)
    db.commit()

# xoá thành viên khỏi nhóm 
def remove_member(db: Session, club_id: int, user_id: int, current_user: User) -> None:
    # kiểm tra quyền
    owner_check = (
        db.query(ClubMember)
        .filter(
            ClubMember.club_id == club_id,
            ClubMember.user_id == current_user.id,
            ClubMember.role == ClubRole.OWNER,
        )
        .first()
    )
    if not owner_check:
        raise HTTPException(
            status_code=403, detail="Chỉ OWNER mới có quyền xóa thành viên"
        )
# kiểm tra người có tồn tại trong nhóm k 
    target_member = (
        db.query(ClubMember)
        .filter(ClubMember.club_id == club_id, ClubMember.user_id == user_id)
        .first()
    )
    if not target_member:
        raise HTTPException(
            status_code=404, detail="Thành viên không tồn tại trong câu lạc bộ"
        )

    if target_member.role == ClubRole.OWNER:
        owner_count = (
            db.query(ClubMember)
            .filter(ClubMember.club_id == club_id, ClubMember.role == ClubRole.OWNER)
            .count()
        )
        if owner_count <= 1:
            raise HTTPException(
                status_code=400, detail="Không thể xóa OWNER cuối cùng của câu lạc bộ"
            )

    db.delete(target_member)
    db.commit()

# xem danh sách thanh viên trong nhóm 
def get_club_members(db: Session, club_id: int, current_user: User) -> List[dict]:
    # kiểm tra người đang xem có phải thành viên trong nhóm hay không
    membership = (
        db.query(ClubMember)
        .filter(ClubMember.club_id == club_id, ClubMember.user_id == current_user.id)
        .first()
    )
    if not membership:
        raise HTTPException(
            status_code=403, detail="Bạn không phải thành viên của câu lạc bộ này"
        )
    members = db.query(ClubMember).filter(ClubMember.club_id == club_id).all()

    result = []
    for m in members:
        result.append(
            {
                "user_id": m.user_id,
                "full_name": m.user.full_name,
                "email": m.user.email,
                "role": m.role,
                "joined_at": m.joined_at,
            }
        )
    return result
