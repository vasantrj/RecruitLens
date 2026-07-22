import json
import uuid
import csv
import io

from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
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



class BulkMatchRequest(BaseModel):
    job_id: str
    candidate_ids: list[str]


@router.post("/bulk-match")
def bulk_match(
    payload: BulkMatchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = db.query(Job).filter(Job.id == payload.job_id, Job.user_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if not job.parsed_requirements:
        raise HTTPException(status_code=400, detail="Job has no parsed requirements yet.")

    job_data = json.loads(job.parsed_requirements)
    jd_text_for_reranker = build_jd_text_for_reranker(job, job_data)

    results = []
    for candidate_id in payload.candidate_ids:
        candidate = db.query(Candidate).filter(
            Candidate.id == candidate_id, Candidate.user_id == current_user.id
        ).first()
        if not candidate or not candidate.parsed_data:
            results.append({"candidate_id": candidate_id, "status": "skipped"})
            continue

        candidate_data = json.loads(candidate.parsed_data)

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

        results.append({
            "candidate_id": str(candidate.id),
            "candidate_name": candidate.full_name,
            "match_id": str(match.id),
            "final_score": match.final_score,
            "status": "matched",
        })

    results.sort(key=lambda r: r.get("final_score", 0), reverse=True)
    return {"job_id": str(job.id), "results": results}



@router.get("/job/{job_id}/export")
def export_rankings(
    job_id: uuid.UUID,
    format: str = "csv",
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

    rows = []
    for m in matches:
        candidate = db.query(Candidate).filter(Candidate.id == m.candidate_id).first()
        breakdown = json.loads(m.breakdown) if m.breakdown else {}
        rows.append({
            "Name": candidate.full_name if candidate else "",
            "Email": candidate.email if candidate else "",
            "Final Score": m.final_score,
            "Skill Match %": breakdown.get("skill_match_pct", ""),
            "Experience Match %": breakdown.get("experience_match_pct", ""),
            "Title Similarity %": breakdown.get("title_similarity_pct", ""),
            "Reranker Score %": breakdown.get("reranker_score_pct", ""),
            "GitHub Bonus": breakdown.get("github_bonus_points", ""),
        })

    if format == "csv":
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=rows[0].keys() if rows else [])
        writer.writeheader()
        writer.writerows(rows)
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={job.title}_rankings.csv"},
        )

    raise HTTPException(status_code=400, detail="Only 'csv' format is currently supported.")

class ExportRequest(BaseModel):
    job_id: str
    candidate_ids: list[str]


@router.post("/export-selected")
def export_selected(
    payload: ExportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = db.query(Job).filter(Job.id == payload.job_id, Job.user_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    rows = []
    for candidate_id in payload.candidate_ids:
        candidate = db.query(Candidate).filter(
            Candidate.id == candidate_id, Candidate.user_id == current_user.id
        ).first()
        if not candidate:
            continue

        match = (
            db.query(MatchScore)
            .filter(MatchScore.candidate_id == candidate_id, MatchScore.job_id == payload.job_id)
            .order_by(MatchScore.created_at.desc())
            .first()
        )
        breakdown = json.loads(match.breakdown) if match and match.breakdown else {}

        rows.append({
            "Name": candidate.full_name or "",
            "Email": candidate.email or "",
            "Phone": candidate.phone or "",
            "Final Score": match.final_score if match else "",
            "Skill Match %": breakdown.get("skill_match_pct", ""),
            "Experience Match %": breakdown.get("experience_match_pct", ""),
            "GitHub Bonus": breakdown.get("github_bonus_points", ""),
        })

    output = io.StringIO()
    fieldnames = list(rows[0].keys()) if rows else [
        "Name", "Email", "Phone", "Final Score", "Skill Match %", "Experience Match %", "GitHub Bonus"
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

    return {"csv": output.getvalue(), "filename": f"{job.title}_shortlisted.csv"}