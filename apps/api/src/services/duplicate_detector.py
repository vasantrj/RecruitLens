from sqlalchemy.orm import Session
from src.models.candidate import Candidate


def find_duplicate_applications(db: Session, user_id, email: str, current_job_id, exclude_candidate_id=None) -> list[dict]:
    """
    Finds other candidates (same user, same email) who applied to a DIFFERENT job
    than current_job_id. Returns a list of {candidate_id, job_id} for each duplicate found.
    """
    if not email:
        return []

    query = db.query(Candidate).filter(
        Candidate.user_id == user_id,
        Candidate.email == email,
        Candidate.job_id != current_job_id,
    )
    if exclude_candidate_id:
        query = query.filter(Candidate.id != exclude_candidate_id)

    duplicates = query.all()
    return [
        {"candidate_id": str(c.id), "job_id": str(c.job_id) if c.job_id else None, "full_name": c.full_name}
        for c in duplicates
    ]