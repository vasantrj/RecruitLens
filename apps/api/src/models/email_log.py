import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from src.database import Base


class EmailLog(Base):
    __tablename__ = "email_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False)

    to_email = Column(String, nullable=False)
    subject = Column(Text, nullable=False)
    body = Column(Text, nullable=False)
    template_used = Column(String, nullable=True)

    status = Column(String, default="pending")   # pending, sent, failed
    gmail_message_id = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)