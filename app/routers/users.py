from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.dependencies.auth import get_current_user, get_current_admin  # Import thêm get_current_admin

router = APIRouter(prefix="/users", tags=["Users"])

# 1. API xem thông tin cá nhân (User / Admin đều dùng được)
@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

# 2. API cập nhật thông tin cá nhân (User / Admin đều dùng được)
@router.put("/me", response_model=UserResponse)
def update_me(
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if user_in.full_name is not None:
        current_user.full_name = user_in.full_name
    if user_in.is_active is not None:
        current_user.is_active = user_in.is_active

    db.commit()
    db.refresh(current_user)
    return current_user

# === BỔ SUNG CÁC API DÀNH RIÊNG CHO ADMIN ===

# 3. API lấy danh sách tất cả người dùng (Chỉ Admin)
@router.get("/", response_model=list[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)  # <-- Bắt buộc role 'admin'
):
    return db.query(User).all()

# 4. API khóa hoặc mở khóa tài khoản người dùng khác (Chỉ Admin)
@router.patch("/{user_id}/status", response_model=UserResponse)
def change_user_status(
    user_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)  # <-- Bắt buộc role 'admin'
):
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Không tìm thấy người dùng"
        )
    
    target_user.is_active = is_active
    db.commit()
    db.refresh(target_user)
    return target_user