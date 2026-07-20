import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from src.database import Base


class PortfolioLink(Base):
    __tablename__ = "portfolio_links"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False)

    url = Column(String, nullable=False)
    link_type = Column(String, nullable=False)   # github, linkedin, behance, blog, personal_site
    summary = Column(Text, nullable=True)         # LLM summary, only for personal_site/blog types

    created_at = Column(DateTime, default=datetime.utcnow)