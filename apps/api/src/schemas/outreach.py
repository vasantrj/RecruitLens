from pydantic import BaseModel
from typing import Optional


class EmailPreviewRequest(BaseModel):
    candidate_id: str
    template_key: str   # "invite_interview", "reject", "next_round"
    role_title: str


class EmailPreviewResponse(BaseModel):
    candidate_id: str
    to_email: Optional[str]
    subject: str
    body: str


class EmailSendRequest(BaseModel):
    candidate_id: str
    to_email: str
    subject: str
    body: str
    template_key: Optional[str] = None