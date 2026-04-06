import smtplib
from email.mime.text import MIMEText
from fastapi import HTTPException
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# Email Host Information
SMTP_HOST = str(os.getenv("SMTP_HOST"))
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = str(os.getenv("SMTP_USER"))
SMTP_PASS = str(os.getenv("SMTP_PASS"))
FROM_EMAIL = str(os.getenv("FROM_EMAIL"))
FRONTEND_URL = str(os.getenv("FRONTEND_URL"))


def send_email(to: str, subject: str, body: str) -> None:
    """
    Sends an email to the specified email address
    Raises 502 if the email could not be delivered
    """
    # Build email message
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = to

    # Connect to SMTP server and send email
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()  # Email connection type is STARTTLS
            server.login(SMTP_USER, SMTP_PASS)  # User login
            server.sendmail(FROM_EMAIL, to, msg.as_string())  # Send email
    except smtplib.SMTPException as e:
        raise HTTPException(status_code=502, detail=f"Email delivery failed: {e}")


def send_verification_email(to: str, token_id: str) -> None:
    """
    Sends a verification email link with the token_id
    """
    # Build verification link and send email
    link = f"{FRONTEND_URL}/auth/verify/{token_id}"
    send_email(
        to=to,
        subject="Verify your account",
        body=f"Click the link to verify your account: {link}",
    )


def send_reset_email(to: str, token_id: str) -> None:
    """
    Sends a password reset email link with the token_id
    """
    # Build reset link and send email
    link = f"{FRONTEND_URL}/auth/reset-password/{token_id}"
    send_email(
        to=to,
        subject="Reset your password",
        body=f"Click the link to reset your password: {link}",
    )
