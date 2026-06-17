import httpx
from config.settings import settings
from config.logging_config import get_logger
from notifications.notifier import BaseChannel

logger = get_logger("notifications.telegram")

class TelegramChannel(BaseChannel):
    """
    Dispatches direct alerts to a Telegram chat using Telegram Bot HTTP APIs.
    """
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID

    async def send(self, subject: str, body: str) -> None:
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram Bot Token or Chat ID not configured. Skipping Telegram alert.")
            return

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        text = f"*{subject}*\n\n{body}"
        
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }

        logger.info(f"Delivering bot notification message to Telegram chat {self.chat_id}...")
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                response = await client.post(url, json=payload)
                result = response.json()
                if not result.get("ok"):
                    logger.error(
                        f"Telegram API returned failure status. Result: {result}"
                    )
                else:
                    logger.info("Telegram notification successfully sent.")
            except Exception as e:
                logger.error(f"Error calling Telegram Bot API endpoint: {e}")
                raise e
