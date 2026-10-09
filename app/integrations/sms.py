from twilio.rest import Client
from app.core.settings import settings


def send_sms_sync(to: str, body: str):
    if not settings.twilio_account_sid or not settings.twilio_auth_token or not settings.twilio_from_number:
        raise RuntimeError('Twilio SMS settings are not configured')
    client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
    message = client.messages.create(to=to, from_=settings.twilio_from_number, body=body)
    return {'sid': message.sid}
