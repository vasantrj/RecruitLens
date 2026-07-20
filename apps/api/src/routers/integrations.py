from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.company_integration import CompanyIntegration
from src.services.outreach.oauth_gmail import get_authorization_url, exchange_code_for_tokens

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.get("/gmail/connect")
def connect_gmail():
    auth_url = get_authorization_url()
    return RedirectResponse(auth_url)


@router.get("/gmail/callback")
def gmail_callback(code: str, db: Session = Depends(get_db)):
    tokens = exchange_code_for_tokens(code)

    existing = db.query(CompanyIntegration).filter(CompanyIntegration.provider == "gmail").first()
    if existing:
        existing.access_token = tokens["access_token"]
        if tokens["refresh_token"]:
            existing.refresh_token = tokens["refresh_token"]
        existing.token_expiry = tokens["expiry"]
        existing.updated_at = datetime.utcnow()
    else:
        existing = CompanyIntegration(
            provider="gmail",
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_expiry=tokens["expiry"],
        )
        db.add(existing)

    db.commit()

    return {"status": "connected", "message": "Gmail account connected successfully. You can close this tab."}


@router.get("/gmail/status")
def gmail_status(db: Session = Depends(get_db)):
    integration = db.query(CompanyIntegration).filter(CompanyIntegration.provider == "gmail").first()
    if not integration:
        return {"connected": False}
    return {"connected": True, "connected_at": integration.created_at}