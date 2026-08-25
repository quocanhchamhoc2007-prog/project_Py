import sys
from pathlib import Path
from datetime import datetime, timedelta

# Tự động tìm thư mục gốc của project (chứa folder app/) để import module
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from app.db.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.models.club import Club
from app.models.activity import ClubActivity


def seed_data():
    db = SessionLocal()
    try:
        print("=== BẮT ĐẦU SEED DỮ LIỆU MẪU (FastAPI) ===")

        # ---------------------------------------------------------------------
        # 1. SEED BẢNG USERS
        # ---------------------------------------------------------------------
        default_password = get_password_hash("123456")

        users_data = [
            {
                "email": "admin@gmail.com",
                "full_name": "Nguyễn Văn Admin",
                "role": "ADMIN",
                "hashed_password": default_password,
                "is_active": True,
            },
            {
                "email": "leader.tinhoc@gmail.com",
                "full_name": "Trần Thị Chủ Tịch",
                "role": "CLUB_LEADER",
                "hashed_password": default_password,
                "is_active": True,
            },
            {
                "email": "leader.tienganh@gmail.com",
                "full_name": "Lê Văn Leader",
                "role": "CLUB_LEADER",
                "hashed_password": default_password,
                "is_active": True,
            },
            {
                "email": "member1@gmail.com",
                "full_name": "Phạm Minh Thành Viên",
                "role": "MEMBER",
                "hashed_password": default_password,
                "is_active": True,
            },
        ]

        users_dict = {}
        for u in users_data:
            user = db.query(User).filter(User.email == u["email"]).first()
            if not user:
                user = User(**u)
                db.add(user)
                db.flush()
                print(f"[+] Thêm User: {user.email}")
            else:
                print(f"[-] User đã tồn tại: {user.email}")
            users_dict[u["email"]] = user

        # ---------------------------------------------------------------------
        # 2. SEED BẢNG CLUBS
        # ---------------------------------------------------------------------
        clubs_data = [
            {
                "name": "CLB Tin Học & Lập Trình",
                "description": "Nơi chia sẻ kiến thức CNTT, thuật toán và phát triển phần mềm.",
                "leader_id": users_dict["leader.tinhoc@gmail.com"].id,
                "is_active": True,
            },
            {
                "name": "CLB Tiếng Anh Giao Tiếp",
                "description": "Môi trường rèn luyện phản xạ và kỹ năng giao tiếp Tiếng Anh.",
                "leader_id": users_dict["leader.tienganh@gmail.com"].id,
                "is_active": True,
            },
        ]

        clubs_dict = {}
        for c in clubs_data:
            club = db.query(Club).filter(Club.name == c["name"]).first()
            if not club:
                club = Club(**c)
                db.add(club)
                db.flush()
                print(f"[+] Thêm CLB: {club.name}")
            else:
                print(f"[-] CLB đã tồn tại: {club.name}")
            clubs_dict[c["name"]] = club

        # ---------------------------------------------------------------------
        # 3. SEED BẢNG ACTIVITIES (HOẠT ĐỘNG CLB)
        # ---------------------------------------------------------------------
        now = datetime.now()
        activities_data = [
            {
                "club_id": clubs_dict["CLB Tin Học & Lập Trình"].id,
                "title": "Workshop: Tối ưu hoá truy vấn SQL",
                "description": "Hướng dẫn viết SQL hiệu quả, thiết kế ERD và đánh Index chuẩn.",
                "location": "Phòng A2-301",
                "start_time": now + timedelta(days=5, hours=10),
                "end_time": now + timedelta(days=5, hours=13),
                "status": "UPCOMING",
            },
            {
                "club_id": clubs_dict["CLB Tin Học & Lập Trình"].id,
                "title": "Lập trình Web Responsive với HTML/CSS",
                "description": "Thực hành làm giao diện Dark Mode và hiệu ứng UI chuyên nghiệp.",
                "location": "Lab CNTT 1",
                "start_time": now + timedelta(days=10, hours=14),
                "end_time": now + timedelta(days=10, hours=17),
                "status": "UPCOMING",
            },
            {
                "club_id": clubs_dict["CLB Tiếng Anh Giao Tiếp"].id,
                "title": "English Speaking Club: Tech & AI Trend",
                "description": "Thảo luận bằng Tiếng Anh về xu hướng Trí tuệ nhân tạo.",
                "location": "Hội trường B",
                "start_time": now + timedelta(days=7, hours=9),
                "end_time": now + timedelta(days=7, hours=11),
                "status": "UPCOMING",
            },
        ]

        for act in activities_data:
            activity = db.query(ClubActivity).filter(
                ClubActivity.title == act["title"],
                ClubActivity.club_id == act["club_id"]
            ).first()

            if not activity:
                activity = ClubActivity(**act)
                db.add(activity)
                print(f"[+] Thêm Hoạt động: {activity.title}")
            else:
                print(f"[-] Hoạt động đã tồn tại: {activity.title}")

        db.commit()
        print("\n===> HOÀN THÀNH SEED DỮ LIỆU THÀNH CÔNG! <===")

    except Exception as e:
        db.rollback()
        print(f"Lỗi khi seed dữ liệu: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()