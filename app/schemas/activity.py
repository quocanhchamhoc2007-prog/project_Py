from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class ActivityStatus(str, Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


class ActivityPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ActivityBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    due_date: datetime | None = None
    priority: ActivityPriority = ActivityPriority.MEDIUM


class ActivityCreate(ActivityBase):
    # gt=0 bắt buộc assignee_id nếu có phải lớn hơn 0
    assignee_id: int | None = Field(default=None, gt=0)


class ActivityUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    assignee_id: int | None = Field(default=None, gt=0)
    status: ActivityStatus | None = None
    priority: ActivityPriority | None = None
    due_date: datetime | None = None


class ActivityResponse(ActivityBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    club_id: int
    created_by_id: int
    assignee_id: int | None
    status: ActivityStatus
    created_at: datetime