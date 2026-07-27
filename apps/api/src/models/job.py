import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID

from src.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    is_role_only = Column(String, default="false")
    parsed_requirements = Column(Text, nullable=True)   # JSON string: required_skills, min_years_experience, etc.
    is_archived = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)