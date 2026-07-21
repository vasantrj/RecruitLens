import json
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.candidate import Candidate
from src.models.job import Job
from src.models.match_score import MatchScore
from src.models.user import User
from src.schemas.matching import MatchResponse
from src.services.matching.scorer import compute_match_score
from src.services.bias_audit import redact_identity_signals, redact_candidate_data
from src.deps import get_current_user

router = APIRouter(prefix="/matching", tags=["matching"])


def build_jd_text_for_reranker(job: Job, job_data: dict) -> str:
    if job.description:
        return job.description
    parts = [f"Role: {job_data.get('role_title', job.title)}"]
    if job_data.get("required_skills"):
        parts.append("Required skills: " + ", ".join(job_data["required_skills"]))
    if job_data.get("nice_to_have_skills"):
        parts.append("Nice to have: " + ", ".join(job_data["nice_to_have_skills"]))
    if job_data.get("min_years_experience") is not None:
        parts.append(f"Minimum experience: {job_data['min_years_experience']} years")
    if job_data.get("education_requirement"):
        parts.append(f"Education: {job_data['education_requirement']}")
    return "\n".join(parts)


# NOTE: this route MUST be defined before /{candidate_id}/{job_id} below,
# otherwise "bias-audit" gets incorrectly matched as a job_id.
@router.post("/{match_id}/bias-audit")
def run_bias_audit(
    match_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    match = db.query(MatchScore).filter(MatchScore.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    candidate = db.query(Candidate).filter(
        Candidate.id == match.candidate_id, Candidate.user_id == current_user.id
    ).first()
    job = db.query(Job).filter(
        Job.id == match.job_id, Job.user_id == current_user.id
    ).first()

    if not candidate or not job:
        raise HTTPException(status_code=404, detail="Related candidate or job not found")

    candidate_data = json.loads(candidate.parsed_data) if candidate.parsed_data else {}
    job_data = json.loads(job.parsed_requirements) if job.parsed_requirements else {}

    jd_text_for_reranker = build_jd_text_for_reranker(job, job_data)

    fresh_original_result = compute_match_score(
        candidate_data=candidate_data,
        job_data=job_data,
        candidate_raw_text=candidate.raw_text or "",
        jd_raw_text=jd_text_for_reranker,
        github_signal_score=candidate.github_signal_score,
    )

    redacted_candidate_data = redact_candidate_data(candidate_data)
    redacted_raw_text = redact_identity_signals(candidate.raw_text or "", candidate.full_name)

    redacted_result = compute_match_score(
        candidate_data=redacted_candidate_data,
        job_data=job_data,
        candidate_raw_text=redacted_raw_text,
        jd_raw_text=jd_text_for_reranker,
        github_signal_score=candidate.github_signal_score,
    )

    fresh_original_score = fresh_original_result["final_score"]
    redacted_score = redacted_result["final_score"]
    delta = round(redacted_score - fresh_original_score, 2)

    return {
        "match_id": match.id,
        "stored_score": match.final_score,
        "fresh_original_score": fresh_original_score,
        "redacted_score": redacted_score,
        "score_delta": delta,
        "interpretation": (
            "No meaningful difference - score appears stable to identity redaction."
            if abs(delta) < 2
            else f"Score changed by {delta} points after redacting identity signals - worth reviewing why."
        ),
        "fresh_original_breakdown": fresh_original_result["breakdown"],
        "redacted_breakdown": redacted_result["breakdown"],
    }


@router.get("/job/{job_id}/rankings")
def get_job_rankings(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    matches = (
        db.query(MatchScore)
        .filter(MatchScore.job_id == job_id)
        .order_by(MatchScore.final_score.desc())
        .all()
    )

    results = []
    for match in matches:
        candidate = db.query(Candidate).filter(Candidate.id == match.candidate_id).first()
        results.append({
            "match_id": match.id,
            "candidate_id": match.candidate_id,
            "candidate_name": candidate.full_name if candidate else None,
            "candidate_email": candidate.email if candidate else None,
            "final_score": match.final_score,
            "created_at": match.created_at,
        })

    return results


@router.post("/{candidate_id}/{job_id}", response_model=MatchResponse)
def match_candidate_to_job(
    candidate_id: uuid.UUID,
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    candidate = db.query(Candidate).filter(
        Candidate.id == candidate_id, Candidate.user_id == current_user.id
    ).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    job = db.query(Job).filter(Job.id == job_id, Job.user_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if not candidate.parsed_data:
        raise HTTPException(status_code=400, detail="Candidate has not been extracted yet. Call /candidates/{id}/extract first.")
    if not job.parsed_requirements:
        raise HTTPException(status_code=400, detail="Job has no parsed requirements yet.")

    candidate_data = json.loads(candidate.parsed_data)
    job_data = json.loads(job.parsed_requirements)

    jd_text_for_reranker = build_jd_text_for_reranker(job, job_data)

    result = compute_match_score(
        candidate_data=candidate_data,
        job_data=job_data,
        candidate_raw_text=candidate.raw_text or "",
        jd_raw_text=jd_text_for_reranker,
        github_signal_score=candidate.github_signal_score,
    )

    match = MatchScore(
        candidate_id=candidate.id,
        job_id=job.id,
        final_score=result["final_score"],
        breakdown=json.dumps(result["breakdown"]),
        matched_required_skills=json.dumps(result["matched_required_skills"]),
        missing_required_skills=json.dumps(result["missing_required_skills"]),
        matched_nice_to_have_skills=json.dumps(result["matched_nice_to_have_skills"]),
    )
    db.add(match)
    db.commit()
    db.refresh(match)

    return MatchResponse(
        id=match.id,
        candidate_id=match.candidate_id,
        job_id=match.job_id,
        final_score=match.final_score,
        breakdown=result["breakdown"],
        matched_required_skills=result["matched_required_skills"],
        missing_required_skills=result["missing_required_skills"],
        matched_nice_to_have_skills=result["matched_nice_to_have_skills"],
        created_at=match.created_at,
    )