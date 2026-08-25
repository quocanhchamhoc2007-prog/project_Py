import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.database import Base


class ClubRole(str, enum.Enum):
    OWNER = "OWNER"
    MEMBER = "MEMBER"


class Club(Base):
    __tablename__ = "clubs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    owner = relationship("User", back_populates="clubs_owned")
    members = relationship(
        "ClubMember", back_populates="club", cascade="all, delete-orphan"
    )
    # ĐÃ SỬA: Thay "ClubActivity" bằng "Activity"
    activities = relationship(
        "Activity", back_populates="club", cascade="all, delete-orphan"
    )


class ClubMember(Base):
    __tablename__ = "club_members"

    club_id = Column(Integer, ForeignKey("clubs.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    role = Column(String(20), nullable=False, default=ClubRole.MEMBER.value)
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    club = relationship("Club", back_populates="members")
    user = relationship("User", back_populates="club_memberships")