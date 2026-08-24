# app/core/deps.py

import jwt

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from sqlalchemy.orm import Session

from app.core.security import SECRET_KEY, ALGORITHM
from app.db.database import get_db
from app.models.user import User

# Nó chỉ lấy token từ Header.
http_bearer = HTTPBearer()


# xác thực 
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    # HTTPAuthorizationCredentials có mục đích rất đơn giản: nó nhận và chứa thông tin được gửi trong HTTP
    # Kết nối database
    db: Session = Depends(get_db),
) -> User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token không hợp lệ hoặc đã hết hạn",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        #  lấy ra jwt
        token = credentials.credentials

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("type") != "access":

            print("--> LỖI 401: " "Token không phải loại 'access'")

            raise credentials_exception

        user_id = payload.get("user_id")
        if user_id is None:

            print("--> LỖI 401: " "Payload thiếu user_id")

            raise credentials_exception

    except jwt.ExpiredSignatureError:

        print("--> LỖI 401: Token đã HẾT HẠN")

        raise credentials_exception

    except jwt.PyJWTError as e:

        print(f"--> LỖI 401 DECODE: {e}")

        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()

    if not user or not user.is_active:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản không hoạt động hoặc không tồn tại",
        )

    return user
# get_current_user()
# 1. Có gửi Authorization Header không?
#         ↓
# 2. Có JWT không?
#         ↓
# 3. JWT có đúng chữ ký không?
#         ↓
# 4. JWT có hết hạn không?
#         ↓
# 5. JWT có user_id hợp lệ và user tồn tại không?

#  phân quyền 
def require_role(allowed_roles: list[str]):

    def role_checker(
        # current_user
        current_user: User = Depends(get_current_user),
    ) -> User:

        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền truy cập tài nguyên này",
            )
        return current_user

    return role_checker


#
get_current_admin = require_role(["admin"])
# Nó tạo ra một dependency dành riêng cho Admin.
