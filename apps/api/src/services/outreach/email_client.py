import base64
from email.mime.text import MIMEText

from googleapiclient.discovery import build

from src.services.outreach.oauth_gmail import get_valid_credentials


def send_email_via_gmail(
    access_token: str,
    refresh_token: str,
    token_expiry,
    to_email: str,
    subject: str,
    body_text: str,
) -> dict:
    creds = get_valid_credentials(access_token, refresh_token, token_expiry)
    service = build("gmail", "v1", credentials=creds)

    message = MIMEText(body_text)
    message["to"] = to_email
    message["subject"] = subject

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    sent = service.users().messages().send(
        userId="me",
        body={"raw": raw_message},
    ).execute()

    return {"message_id": sent.get("id"), "status": "sent"}