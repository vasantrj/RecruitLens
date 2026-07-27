from fastapi import APIRouter, HTTPException
from src.schemas.contact import ContactRequest
from src.services.contact_mailer import send_contact_email

router = APIRouter(prefix="/contact", tags=["contact"])


@router.post("/")
def submit_contact_form(payload: ContactRequest):
    try:
        send_contact_email(payload.name, payload.email, payload.subject, payload.message)
        return {"status": "sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")