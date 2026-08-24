# tạo cấu hình 
from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    #  cấu hình setting hoạt động

    model_config = SettingsConfigDict(
        # Hãy đọc cấu hình từ file .env.
        env_file=".env",
        # File .env được đọc bằng encoding UTF-8.
        env_file_encoding="utf-8",
        # Nếu .env có những biến mà class Settings không khai báo thì bỏ qua.
        extra="ignore")
settings = Settings()

# BaseSettings là class của pydantic-settings. - "Tôi định nghĩa toàn bộ cấu hình mà ứng dụng cần ở đây."