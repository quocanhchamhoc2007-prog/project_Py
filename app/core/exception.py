from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

#  tự định nghĩa một loại exception riêng cho ứng dụng.
class AppException(Exception):
    def __init__(self, status_code: int, message: str, detail: str | None = None):
        self.status_code = status_code
        self.message = message
        self.detail = detail


class NotFoundException(AppException):
    def __init__(
        self, message: str = "Không tìm thấy tài nguyên", detail: str | None = None
    ):
        super().__init__(status.HTTP_404_NOT_FOUND, message, detail)


class BadRequestException(AppException):
    def __init__(
        self, message: str = "Yêu cầu không hợp lệ", detail: str | None = None
    ):
        super().__init__(status.HTTP_400_BAD_REQUEST, message, detail)


class ForbiddenException(AppException):
    def __init__(
        self,
        message: str = "Bạn không có quyền thực hiện thao tác này",
        detail: str | None = None,
    ):
        super().__init__(status.HTTP_403_FORBIDDEN, message, detail)


def error_response(status_code: int, message: str, detail: str | None = None):
    # Format lỗi thống nhất cho toàn bộ app
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": {"code": status_code, "message": message, "detail": detail},
        },
    )

# Bắt các lỗi tùy chỉnh (custom exceptions) do bạn tự định nghĩa trong dự án
# Lấy trực tiếp thông tin lỗi từ đối tượng exc (gồm status_code, message, detail) để trả về cho người dùng. Thường dùng khi bạn chủ động raise AppException(...) trong logic xử lý.
def exception_handlers(app: FastAPI):
    @app.exception_handler(AppException)
    def app_exception_handler(request: Request, exc: AppException):
        return error_response(exc.status_code, exc.message, exc.detail)
# Bắt lỗi dữ liệu đầu vào không hợp lệ (do Pydantic / FastAPI tự động kích hoạt khi client gửi sai kiểu dữ liệu, thiếu trường bắt buộc, v.v.).
# Ghi đè (override) thông báo lỗi mặc định của FastAPI, trả về HTTP status 422 Unprocessable Entity kèm thông báo cố định "Validation error".
    @app.exception_handler(RequestValidationError)
    def validation_exception_handler(request: Request, exc: RequestValidationError):
        return error_response(status.HTTP_422_UNPROCESSABLE_ENTITY, "Validation error")
# Bắt tất cả các lỗi không lường trước được (lỗi hệ thống, crash code, lỗi kết nối DB,...).
# Trả về HTTP status 500 Internal Server Error với câu báo chung "Internal server error". Điều này rất quan trọng về mặt bảo mật, giúp ẩn đi các chi tiết kỹ thuật nhạy cảm (stack trace) không cho client nhìn thấy.
    @app.exception_handler(Exception)
    def generic_exception_handler(request: Request, exc: Exception):
        return error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Internal server error",
        )
