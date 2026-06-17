import smtplib
import asyncio
from email.mime.text import MIMEText
from config.settings import settings
from config.logging_config import get_logger
from notifications.notifier import BaseChannel

logger = get_logger("notifications.email")

class EmailChannel(BaseChannel):
    """
    SMTP mail dispatch client utilizing standard smtplib.
    """
    def __init__(self):
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.user = settings.SMTP_USER
        self.password = settings.SMTP_PASSWORD
        self.to_email = settings.SMTP_TO

    def _send_sync(self, subject: str, body: str) -> None:
        """
        Synchronous email sending logic.
        """
        if not self.user or not self.to_email:
            logger.warning("SMTP credentials or recipient address missing. Skipping email.")
            return

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = self.user
        msg["To"] = self.to_email

        logger.info(f"Opening SMTP connection to {self.host}:{self.port}...")
        with smtplib.SMTP(self.host, self.port) as server:
            server.ehlo()
            server.starttls()  # Secure connection
            server.login(self.user, self.password)
            server.sendmail(self.user, [self.to_email], msg.as_string())
        logger.info(f"SMTP mail successfully sent to {self.to_email}.")

    async def send(self, subject: str, body: str) -> None:
        """
        Asynchronously sends the email notification by delegating to a separate thread.
        """
        try:
            await asyncio.to_thread(self._send_sync, subject, body)
        except Exception as e:
            logger.error(f"Failed to send email alert through SMTP: {e}")
            raise e
