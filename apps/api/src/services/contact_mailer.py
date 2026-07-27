import smtplib
from email.mime.text import MIMEText

from src.config import settings


def send_contact_email(name: str, email: str, subject: str, message: str):
    body = f"From: {name} <{email}>\n\n{message}"
    msg = MIMEText(body)
    msg["Subject"] = f"[RecruitLensAI Contact] {subject}"
    msg["From"] = settings.contact_email_address
    msg["To"] = settings.contact_email_address
    msg["Reply-To"] = email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(settings.contact_email_address, settings.contact_email_app_password)
        server.sendmail(settings.contact_email_address, settings.contact_email_address, msg.as_string())