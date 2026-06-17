import asyncio
import functools
from typing import Callable, Any
from config.logging_config import get_logger
from config.settings import settings

logger = get_logger("scraper.retry")

def async_retry(
    retries: int = None,
    delay: float = None,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator that retries an async function with exponential backoff.
    """
    retries = retries or settings.SCRAPER_RETRY_COUNT
    delay = delay or settings.SCRAPER_RETRY_DELAY

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            current_delay = delay
            for attempt in range(1, retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == retries:
                        logger.error(
                            f"Function {func.__name__} failed after {retries} attempts. Error: {e}"
                        )
                        raise e
                    
                    logger.warning(
                        f"Attempt {attempt}/{retries} for '{func.__name__}' failed: {e}. "
                        f"Retrying in {current_delay:.1f}s..."
                    )
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff_factor
            return None
        return wrapper
    return decorator
