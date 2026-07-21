import uuid
import json as json_module
from typing import Optional

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.candidate import Candidate
from src.models.user import User
from src.schemas.candidate import CandidateResponse
from src.utils.file_storage import upload_resume
from src.services.extraction.resume_parser import extract_resume_text, extract_pdf_hyperlinks
from src.services.extraction.candidate_extractor import extract_structured_resume_data
from src.deps import get_current_user

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.post("/upload", response_model=CandidateResponse)
async def upload_candidate(
    file: UploadFile = File(...),
    job_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not file.filename.lower().endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported.")

    parsed_job_id = None
    if job_id and job_id.strip():
        try:
            parsed_job_id = uuid.UUID(job_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="job_id must be a valid UUID.")

    file_bytes = await file.read()

    try:
        file_key = upload_resume(file_bytes, file.filename)
        raw_text = extract_resume_text(file_bytes, file.filename)

        embedded_links = []
        if file.filename.lower().endswith(".pdf"):
            embedded_links = extract_pdf_hyperlinks(file_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process resume: {str(e)}")

    candidate = Candidate(
        user_id=current_user.id,
        job_id=parsed_job_id,
        resume_file_path=file_key,
        raw_text=raw_text,
        embedded_links=json_module.dumps(embedded_links),
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate


@router.get("/{candidate_id}", response_model=CandidateResponse)
def get_candidate(
    candidate_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    candidate = db.query(Candidate).filter(
        Candidate.id == candidate_id, Candidate.user_id == current_user.id
    ).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate


@router.post("/{candidate_id}/extract")
def extract_candidate_data(
    candidate_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    candidate = db.query(Candidate).filter(
        Candidate.id == candidate_id, Candidate.user_id == current_user.id
    ).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    if not candidate.raw_text:
        raise HTTPException(status_code=400, detail="Candidate has no extracted resume text")

    structured_data = extract_structured_resume_data(candidate.raw_text)

    candidate.parsed_data = json_module.dumps(structured_data)

    if not candidate.full_name and structured_data.get("full_name"):
        candidate.full_name = structured_data.get("full_name")
    if not candidate.email and structured_data.get("email"):
        candidate.email = structured_data.get("email")
    if not candidate.phone and structured_data.get("phone"):
        candidate.phone = structured_data.get("phone")

    db.commit()
    db.refresh(candidate)

    return {
        "candidate_id": candidate.id,
        "parsed_data": structured_data,
    }