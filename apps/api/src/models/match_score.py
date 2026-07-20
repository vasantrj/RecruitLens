import uuid
from datetime import datetime

from sqlalchemy import Column, Text, DateTime, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from src.database import Base


class MatchScore(Base):
    __tablename__ = "match_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)

    final_score = Column(Float, nullable=False)
    breakdown = Column(Text, nullable=True)
    matched_required_skills = Column(Text, nullable=True)
    missing_required_skills = Column(Text, nullable=True)
    matched_nice_to_have_skills = Column(Text, nullable=True)

    ai_feedback = Column(Text, nullable=True)   # JSON string: strengths, gaps, recommendation, interview_questions

    created_at = Column(DateTime, default=datetime.utcnow)