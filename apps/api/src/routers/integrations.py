from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from fastapi import Query

from src.database import get_db
from src.models.company_integration import CompanyIntegration
from src.services.auth.security import decode_access_token
from src.models.user import User
from src.services.outreach.oauth_gmail import get_authorization_url, exchange_code_for_tokens
from src.deps import get_current_user

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.get("/gmail/connect")
def connect_gmail(token: str = Query(...), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    auth_url = get_authorization_url(state=str(user.id))
    return RedirectResponse(auth_url)


@router.get("/gmail/callback")
def gmail_callback(code: str, state: str, db: Session = Depends(get_db)):
    user_id = state  # the user id we passed in above

    tokens = exchange_code_for_tokens(code)

    existing = db.query(CompanyIntegration).filter(
        CompanyIntegration.provider == "gmail", CompanyIntegration.user_id == user_id
    ).first()

    if existing:
        existing.access_token = tokens["access_token"]
        if tokens["refresh_token"]:
            existing.refresh_token = tokens["refresh_token"]
        existing.token_expiry = tokens["expiry"]
        existing.updated_at = datetime.utcnow()
    else:
        existing = CompanyIntegration(
            user_id=user_id,
            provider="gmail",
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_expiry=tokens["expiry"],
        )
        db.add(existing)

    db.commit()

    return {"status": "connected", "message": "Gmail account connected successfully. You can close this tab."}


@router.get("/gmail/status")
def gmail_status(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    integration = db.query(CompanyIntegration).filter(
        CompanyIntegration.provider == "gmail", CompanyIntegration.user_id == current_user.id
    ).first()
    if not integration:
        return {"connected": False}
    return {"connected": True, "connected_at": integration.created_at}