from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
class ActivityBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    due_date: datetime | None = None
    priority: str = "MEDIUM"
class ActivityCreate(ActivityBase):
    assignee_id: int | None = None
class ActivityUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    assignee_id: int | None = None
    status: str | None = None
    priority: str | None = None
    due_date: datetime | None = None
class ActivityResponse(ActivityBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    club_id: int
    assignee_id: int | None
    status: str
    created_at: datetime
