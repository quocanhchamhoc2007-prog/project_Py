import time
import bcrypt
import jwt
from app.core.config import settings

SECRET_KEY = settings.SECRET_KEY
REFRESH_SECRET_KEY = getattr(settings, "REFRESH_SECRET_KEY", settings.SECRET_KEY)
ALGORITHM = getattr(settings, "JWT_ALGORITHM", "HS256")

def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt() 
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    return hashed_bytes.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def generate_user_token(user_id: int, email: str, role: str) -> str:
    payload = {
        "sub": email,
        "user_id": user_id,
        "role": role,
        "type": "access",
        "exp": int(time.time()) + 1800 , # 30 phút
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def generate_refresh_token(user_id: int, email: str, role: str) -> str:
    payload = {
        "sub": email,
        "user_id": user_id,
        "role": role,
        "type": "refresh",
        "exp": int(time.time()) + (7 * 24 * 3600)  # 7 ngày
    }
    return jwt.encode(payload, REFRESH_SECRET_KEY, algorithm=ALGORITHM)



# Luồng hoạt động (Workflow)

# Khi người dùng Đăng ký (/auth/register):
# Hệ thống gọi hash_password() để biến mật khẩu thô thành chuỗi băm trước khi INSERT vào Database.

# Khi người dùng Đăng nhập (/auth/login):
# Hệ thống gọi verify_password(). Nếu chính xác, hệ thống chạy đồng thời generate_user_token() và generate_refresh_token() để trả cặp Token về cho Client.

# Khi gọi các API bảo mật (ví dụ: /users/me):
# Client đính kèm Access Token vào Header. Server giải mã Token, kiểm tra thời hạn (exp) và xem type có đúng là "access" hay không.

# Khi Access Token hết hạn:
# Client gửi Refresh Token lên endpoint /auth/refresh. Server kiểm tra type == "refresh", nếu hợp lệ sẽ chạy lại generate_user_token() để cấp Access Token mới.