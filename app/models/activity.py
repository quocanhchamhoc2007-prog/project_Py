import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from app.db.database import Base


class ActivityStatus(str, enum.Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


class ActivityPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime, nullable=True)
    priority = Column(Enum(ActivityPriority), default=ActivityPriority.MEDIUM)
    status = Column(Enum(ActivityStatus), default=ActivityStatus.TODO)

    club_id = Column(Integer, ForeignKey("clubs.id"), nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    club = relationship("Club", back_populates="activities")
    created_by = relationship("User", foreign_keys=[created_by_id])
    assignee = relationship("User", foreign_keys=[assignee_id])