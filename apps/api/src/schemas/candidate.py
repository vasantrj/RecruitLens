import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CandidateResponse(BaseModel):
    id: uuid.UUID
    job_id: Optional[uuid.UUID] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    resume_file_path: str
    raw_text: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True