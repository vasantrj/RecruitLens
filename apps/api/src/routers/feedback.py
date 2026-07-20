import json
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.match_score import MatchScore
from src.models.candidate import Candidate
from src.models.job import Job
from src.services.llm.feedback_generator import generate_recruiter_feedback

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("/{match_id}")
def generate_feedback(match_id: uuid.UUID, db: Session = Depends(get_db)):
    match = db.query(MatchScore).filter(MatchScore.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    candidate = db.query(Candidate).filter(Candidate.id == match.candidate_id).first()
    job = db.query(Job).filter(Job.id == match.job_id).first()

    if not candidate or not job:
        raise HTTPException(status_code=404, detail="Related candidate or job not found")

    candidate_data = json.loads(candidate.parsed_data) if candidate.parsed_data else {}
    job_data = json.loads(job.parsed_requirements) if job.parsed_requirements else {}

    match_result = {
        "final_score": match.final_score,
        "breakdown": json.loads(match.breakdown) if match.breakdown else {},
        "matched_required_skills": json.loads(match.matched_required_skills) if match.matched_required_skills else [],
        "missing_required_skills": json.loads(match.missing_required_skills) if match.missing_required_skills else [],
        "matched_nice_to_have_skills": json.loads(match.matched_nice_to_have_skills) if match.matched_nice_to_have_skills else [],
    }

    feedback = generate_recruiter_feedback(candidate_data, job_data, match_result)

    match.ai_feedback = json.dumps(feedback)
    db.commit()
    db.refresh(match)

    return {
        "match_id": match.id,
        "feedback": feedback,
    }