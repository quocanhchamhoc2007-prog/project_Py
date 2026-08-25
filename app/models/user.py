import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.db.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(20), default=UserRole.USER.value, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    clubs_owned = relationship("Club", back_populates="owner")
    club_memberships = relationship(
        "ClubMember", back_populates="user", cascade="all, delete-orphan"
    )
    
    # Đã thêm foreign_keys="Activity.assignee_id" để chỉ rõ khóa ngoại
    assigned_activities = relationship(
        "Activity", 
        back_populates="assignee",
        foreign_keys="Activity.assignee_id"
    )