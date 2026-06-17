import httpx
from config.settings import settings
from config.logging_config import get_logger
from notifications.notifier import BaseChannel

logger = get_logger("notifications.slack")

class SlackChannel(BaseChannel):
    """
    Sends message payloads directly to a configured Slack Webhook URL.
    """
    def __init__(self):
        self.webhook_url = settings.SLACK_WEBHOOK_URL

    async def send(self, subject: str, body: str) -> None:
        if not self.webhook_url:
            logger.warning("Slack Webhook URL is not configured. Skipping Slack alert.")
            return

        payload = {
            "text": f"*{subject}*\n\n{body}"
        }

        logger.info("Sending payload to Slack Webhook...")
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                response = await client.post(self.webhook_url, json=payload)
                if response.status_code not in (200, 204):
                    logger.error(
                        f"Slack returned unexpected status code: {response.status_code}. "
                        f"Response: {response.text}"
                    )
                else:
                    logger.info("Slack alert successfully delivered.")
            except Exception as e:
                logger.error(f"Error executing HTTP POST to Slack: {e}")
                raise e
