from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class ClubBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: str | None = None

class ClubCreate(ClubBase):
    pass

class ClubUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)
    description: str | None = None

class ClubResponse(ClubBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    owner_id: int
    created_at: datetime

class AddMemberRequest(BaseModel):
    user_id: int

class MemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    full_name: str | None = None
    email: str
    role: str
    joined_at: datetime

class ClubMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    club_id: int
    user_id: int
    role: str
    joined_at: datetime