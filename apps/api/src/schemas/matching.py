import uuid
from datetime import datetime
from typing import List, Dict, Optional

from pydantic import BaseModel


class MatchResponse(BaseModel):
    id: uuid.UUID
    candidate_id: uuid.UUID
    job_id: uuid.UUID
    final_score: float
    breakdown: Dict[str, float]
    matched_required_skills: List[str]
    missing_required_skills: List[str]
    matched_nice_to_have_skills: List[str]
    created_at: datetime