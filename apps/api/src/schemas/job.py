import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class JobCreate(BaseModel):
    title: str
    description: Optional[str] = None
    is_role_only: bool = False


class JobResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: Optional[str] = None
    is_role_only: str
    parsed_requirements: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
        
class RoleOnlyJobCreate(BaseModel):
    role_title: str