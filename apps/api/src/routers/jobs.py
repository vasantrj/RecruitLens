from typing import List
import uuid
import json as json_module

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.job import Job
from src.models.user import User
from src.schemas.job import JobCreate, JobResponse, RoleOnlyJobCreate
from src.services.extraction.jd_parser import extract_structured_jd_data
from src.services.extraction.role_profile import generate_role_profile
from src.deps import get_current_user

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/", response_model=JobResponse)
def create_job(
    job: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_job = Job(
        user_id=current_user.id,
        title=job.title,
        description=job.description,
        is_role_only="true" if job.is_role_only else "false",
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job


@router.post("/role-only", response_model=JobResponse)
def create_role_only_job(
    payload: RoleOnlyJobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Accepts just a role title, uses the LLM to synthesize a canonical
    requirements profile, and stores it directly as parsed_requirements
    (skipping the raw-JD-text extraction step, since there's no JD text).
    """
    profile = generate_role_profile(payload.role_title)

    new_job = Job(
        user_id=current_user.id,
        title=payload.role_title,
        description=None,
        is_role_only="true",
        parsed_requirements=json_module.dumps(profile),
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job


@router.get("/", response_model=List[JobResponse])
def list_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Job).filter(Job.user_id == current_user.id).all()


@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/{job_id}/extract")
def extract_job_requirements(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if not job.description:
        raise HTTPException(status_code=400, detail="Job has no description text to parse")

    structured_data = extract_structured_jd_data(job.description)
    job.parsed_requirements = json_module.dumps(structured_data)

    db.commit()
    db.refresh(job)

    return {
        "job_id": job.id,
        "parsed_requirements": structured_data,
    }