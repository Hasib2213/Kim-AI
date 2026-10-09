import smtplib
from email.message import EmailMessage
from app.core.settings import settings


def send_email_sync(to: str, subject: str, body: str):
    if not settings.smtp_host or not settings.smtp_from_email:
        raise RuntimeError('SMTP settings are not configured')
    msg = EmailMessage()
    msg['From'] = settings.smtp_from_email
    msg['To'] = to
    msg['Subject'] = subject
    msg.set_content(body)
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
        if settings.smtp_use_tls:
            smtp.starttls()
        if settings.smtp_username:
            smtp.login(settings.smtp_username, settings.smtp_password or '')
        smtp.send_message(msg)
    return True
