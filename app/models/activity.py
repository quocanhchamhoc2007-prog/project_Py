from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.database import Base


class ClubActivity(Base):
    __tablename__ = "club_activities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    club_id = Column(Integer, ForeignKey("clubs.id"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Khớp tên với file Club và User
    club = relationship("Club", back_populates="activities")
    assignee = relationship("User", back_populates="assigned_activities")