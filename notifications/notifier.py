import abc
from config.settings import settings
from config.logging_config import get_logger

logger = get_logger("notifications.notifier")

class BaseChannel(abc.ABC):
    """
    Abstract Base Class for a notification channel.
    """
    @abc.abstractmethod
    async def send(self, subject: str, body: str) -> None:
        pass


class ConsoleChannel(BaseChannel):
    """
    Fallback channel that prints alerts directly to the logging console.
    """
    async def send(self, subject: str, body: str) -> None:
        logger.info(f"[NOTIFIER ALERT] Subject: {subject}\nBody:\n{body}")


async def get_notifier_channel() -> BaseChannel:
    """
    Factory function returning the active notifier channel according to config settings.
    """
    channel_type = settings.NOTIFICATION_CHANNEL.lower()
    
    if channel_type == "console":
        return ConsoleChannel()
    elif channel_type == "email":
        try:
            from notifications.channels.email_channel import EmailChannel
            return EmailChannel()
        except Exception as e:
            logger.error(f"Failed to load EmailChannel, falling back to Console: {e}")
            return ConsoleChannel()
    elif channel_type == "slack":
        try:
            from notifications.channels.slack_channel import SlackChannel
            return SlackChannel()
        except Exception as e:
            logger.error(f"Failed to load SlackChannel, falling back to Console: {e}")
            return ConsoleChannel()
    elif channel_type == "telegram":
        try:
            from notifications.channels.telegram_channel import TelegramChannel
            return TelegramChannel()
        except Exception as e:
            logger.error(f"Failed to load TelegramChannel, falling back to Console: {e}")
            return ConsoleChannel()
    else:
        logger.warning(f"Unknown notification channel '{channel_type}'. Falling back to Console.")
        return ConsoleChannel()


async def send_success(run_summary: str) -> None:
    """
    Dispatches a success notification. Handles errors silently to protect pipeline.
    """
    try:
        channel = await get_notifier_channel()
        subject = "🚀 AMFI Ingestion Pipeline - RUN SUCCESS"
        await channel.send(subject, run_summary)
    except Exception as e:
        logger.error(f"Silent failure sending success notification: {e}")


async def send_failure(error_details: str) -> None:
    """
    Dispatches a failure notification. Handles errors silently to protect pipeline.
    """
    try:
        channel = await get_notifier_channel()
        subject = "⚠️ AMFI Ingestion Pipeline - RUN FAILURE"
        await channel.send(subject, error_details)
    except Exception as e:
        logger.error(f"Silent failure sending failure notification: {e}")
