import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID

from src.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    account_type = Column(String, nullable=False, default="personal")  # "personal" or "company"
    company_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    full_name = Column(String, nullable=True)