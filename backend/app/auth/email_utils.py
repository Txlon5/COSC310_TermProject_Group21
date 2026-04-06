import smtplib
from email.mime.text import MIMEText
from fastapi import HTTPException


# Email Host Information
SMTP_HOST = "sandbox.smtp.mailtrap.io"
SMTP_PORT = 587
SMTP_USER = "24b567e057a980"
SMTP_PASS = "f30fee31cf94ee"
FROM_EMAIL = "noreply@yourapp.com"
FRONTEND_URL = "localhost:8000"


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
    link = f"{FRONTEND_URL}/auth/forgot-password/{token_id}"
    send_email(
        to=to,
        subject="Reset your password",
        body=f"Click the link to reset your password: {link}",
    )
