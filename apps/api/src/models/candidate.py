import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from src.database import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=True)

    full_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)

    resume_file_path = Column(String, nullable=False)
    raw_text = Column(Text, nullable=True)
    embedded_links = Column(Text, nullable=True)

    parsed_data = Column(Text, nullable=True)
    github_signal_score = Column(Float, nullable=True)   # cached technical_signal_score, 0-100

    created_at = Column(DateTime, default=datetime.utcnow)