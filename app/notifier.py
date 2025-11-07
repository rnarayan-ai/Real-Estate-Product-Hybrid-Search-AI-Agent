import smtplib
from email.message import EmailMessage
from twilio.rest import Client as TwilioClient
from .config import settings


class Notifier:
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_pass = settings.SMTP_PASS
        if settings.TWILIO_SID and settings.TWILIO_TOKEN:
            self.twilio = TwilioClient(settings.TWILIO_SID, settings.TWILIO_TOKEN)
        else:
            self.twilio = None

    def send_email(self, to_email: str, subject: str, body: str, attachments: list = None):
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = self.smtp_user
        msg['To'] = to_email
        msg.set_content(body)

        if attachments:
            for path in attachments:
                with open(path, 'rb') as f:
                    data = f.read()
                    msg.add_attachment(
                        data,
                        maintype='application',
                        subtype='octet-stream',
                        filename=path.split('/')[-1]
                    )

        with smtplib.SMTP(self.smtp_host, self.smtp_port) as s:
            s.starttls()
            s.login(self.smtp_user, self.smtp_pass)
            s.send_message(msg)

    def send_whatsapp(self, to_number: str, body: str):
        if not self.twilio:
            raise RuntimeError('Twilio not configured')
        from_w = f'whatsapp:{settings.TWILIO_FROM}'
        to_w = f'whatsapp:{to_number}'
        self.twilio.messages.create(body=body, from_=from_w, to=to_w)


# convenience instance
notifier = Notifier()
