import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.candidate import Candidate
from src.models.email_log import EmailLog
from src.models.company_integration import CompanyIntegration
from src.models.user import User
from src.schemas.outreach import EmailPreviewRequest, EmailSendRequest
from src.services.outreach.templates import render_template
from src.services.outreach.email_client import send_email_via_gmail
from src.deps import get_current_user

router = APIRouter(prefix="/outreach", tags=["outreach"])


@router.post("/preview")
def preview_email(
    payload: EmailPreviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Step 1 of the send flow: generates the email content for the recruiter to review.
    Does NOT send anything — this is the manual review safety step.
    """
    candidate = db.query(Candidate).filter(
        Candidate.id == payload.candidate_id, Candidate.user_id == current_user.id
    ).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    candidate_name = candidate.full_name or "Candidate"
    rendered = render_template(payload.template_key, candidate_name, payload.role_title)

    return {
        "candidate_id": str(candidate.id),
        "to_email": candidate.email,
        "subject": rendered["subject"],
        "body": rendered["body"],
    }


@router.post("/send")
def send_email(
    payload: EmailSendRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Step 2 of the send flow: actually sends the email.
    Requires the recruiter to have already seen the preview and explicitly
    confirmed by calling this endpoint with the (possibly edited) subject/body.
    """
    candidate = db.query(Candidate).filter(
        Candidate.id == payload.candidate_id, Candidate.user_id == current_user.id
    ).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    integration = db.query(CompanyIntegration).filter(
        CompanyIntegration.provider == "gmail", CompanyIntegration.user_id == current_user.id
    ).first()
    if not integration or not integration.access_token:
        raise HTTPException(status_code=400, detail="Gmail is not connected. Call /integrations/gmail/connect first.")

    log_entry = EmailLog(
        candidate_id=candidate.id,
        to_email=payload.to_email,
        subject=payload.subject,
        body=payload.body,
        template_used=payload.template_key,
        status="pending",
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)

    try:
        result = send_email_via_gmail(
            access_token=integration.access_token,
            refresh_token=integration.refresh_token,
            token_expiry=integration.token_expiry,
            to_email=payload.to_email,
            subject=payload.subject,
            body_text=payload.body,
        )
        log_entry.status = "sent"
        log_entry.gmail_message_id = result.get("message_id")
        log_entry.sent_at = datetime.utcnow()
    except Exception as e:
        log_entry.status = "failed"
        log_entry.error_message = str(e)

    db.commit()
    db.refresh(log_entry)

    return {
        "email_log_id": log_entry.id,
        "status": log_entry.status,
        "error": log_entry.error_message,
    }


@router.get("/history/{candidate_id}")
def get_email_history(
    candidate_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    candidate = db.query(Candidate).filter(
        Candidate.id == candidate_id, Candidate.user_id == current_user.id
    ).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    logs = db.query(EmailLog).filter(EmailLog.candidate_id == candidate_id).all()
    return [
        {
            "id": log.id,
            "to_email": log.to_email,
            "subject": log.subject,
            "status": log.status,
            "sent_at": log.sent_at,
            "created_at": log.created_at,
        }
        for log in logs
    ]