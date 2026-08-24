from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import jwt

from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, RefreshTokenRequest, TokenResponse, UserResponse
from app.core.security import (
    hash_password, 
    verify_password, 
    generate_user_token, 
    generate_refresh_token,
    REFRESH_SECRET_KEY, 
    ALGORITHM
)
#tất cả api trong này đều bắt đầu bằng auth 
router = APIRouter(prefix="/auth", tags=["Auth"])

# đăng kí tài khoản 
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
# lấy thông tin người dùng đăng kí tài khoản thông qua schema và lấy data sesson thông qua hàm get db
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    # kiểm tra xem tài khoản đẵ được đăng kí chưa 
    # tìm user thông qua email được gửi lên nếu tìm thâys trả về user object nêus k tìm thấy trả none 
    if db.query(User).filter(User.email == user_in.email).first():
        # nêu email đã tồn tại raise ra thông báo 400 là đã tồn tại
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email đã được đăng ký"
        )
    # try exept dùng để bao hàm bắt lỗi những chỗ có thể sảy ra trong databasse 
    try:
        # bắt đầu tạo user mơis gồm các trường đượcc gửi lên
        new_user = User(
    email=user_in.email,
    password_hash=hash_password(user_in.password),
    full_name=user_in.full_name,
    role="user"  # <-- Ép cứng role là "user" tại đây
)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    # bắt full lỗi cos thể xảy ra 
    except SQLAlchemyError:
        # dùng rollback để quay trở lại và không lưu lỗi
        db.rollback()
        # thông báo ra cho người dùng biêts đang bị lỗi 
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Lỗi lưu dữ liệu tài khoản"
        )
#  đăng nhập 
@router.post("/login", response_model=TokenResponse)
# cho người dùng nhập thông tin bao gồm email và mật khẩu lâys bằng schema
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    # kiểm tra xem đã có tài khoản này hay chưa 
    user = db.query(User).filter(User.email == credentials.email).first()
    # kiểm tra email và mật khẩu 
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Email hoặc mật khẩu không chính xác"
        )
    # kiểm tra xem tài khoản này đã bị is active = flass hay chưa
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Tài khoản đã bị khóa"
        )
    # nêus đăng nhập thành công ssever tạo 2 token và trả về phis client 

    return {
        # tạo token
        "access_token": generate_user_token(user.id, user.email, user.role),
        # refrssh token
        "refresh_token": generate_refresh_token(user.id, user.email, user.role),
        # k phaiur token nó chjir cho biêts access có dạng bearer
        "token_type": "bearer"
    }
# refresh token để lấy token mới
# Nhận Refresh Token → kiểm tra → cấp token mới.
@router.post("/refresh", response_model=TokenResponse)
# paload cchuawss refrsh token 
def refresh_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    # bởi vì jwt deccode co thể phhast sinh lỗi nên cần bătgs lỗi 
    try:
        # đây là dong quan trọng nhast
        # hiểu theo cachs sau : refesh -> jwt.decode -> kiểm tra chữ kí -> kiểm tra thời hạn -> kiểm tra cấu trucs -> payload bên trong
        decoded = jwt.decode(payload.refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        # payload.refrssh token đây là token dc client gửi lên 
        # REFRESH_SECRET_KEY là chìa khoá bi mật để kiêmr tra token \
        # Token được ký bằng Secret Key
    #          ↓
    #    Server có Secret Key
    #          ↓
    #   Server kiểm tra chữ ký
    # algorithms là thuật toanss hs256 
    # sau khi chạy thành công decoded là dict
        if decoded.get("type") != "refresh":
            # kieemr tra loai token lay gia tri type 
            # vd neu token la accesse thi typr = accesse -> loai chi lay token la refsh
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token không đúng loại refresh token")
        # lay user_id 
        # có mục đích lấy ID của người dùng từ Refresh Token để biết Refresh Token đó thuộc tài khoản nào, sau đó dùng ID đó để tìm user trong database.
        user_id = int(decoded.get("user_id"))
        #  bawts full loix 
        # Token không hợp lệ
        # Token hết hạn
        # Signature sai
    except (jwt.PyJWTError, ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Refresh token không hợp lệ hoặc đã hết hạn"
        )
    # timf user trong data
    user = db.query(User).filter(User.id == user_id).first()
    # kiem tra usser o 2 th 
    # bi khoa hoc k ton tai
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Tài khoản không tồn tại hoặc đã bị khóa"
        )

    return {
        "access_token": generate_user_token(user.id, user.email, user.role),
        "refresh_token": generate_refresh_token(user.id, user.email, user.role),
        "token_type": "bearer"
    }