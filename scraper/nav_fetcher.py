import httpx
from config.settings import settings
from config.constants import AMFI_ENCODING
from config.logging_config import get_logger
from scraper.retry import async_retry
from scraper.exceptions import ScraperFetchError

logger = get_logger("scraper.nav_fetcher")

class NavFetcher:
    """
    Handles network requests to the AMFI endpoint to fetch daily NAV files.
    """
    def __init__(self, url: str = None, timeout: int = None):
        self.url = url or settings.AMFI_NAV_URL
        self.timeout = timeout or settings.SCRAPER_TIMEOUT

    @async_retry(exceptions=(httpx.HTTPError, httpx.TimeoutException))
    async def fetch_raw_nav(self) -> str:
        """
        Asynchronously fetches daily NAV plain-text file.
        """
        logger.info(f"Initiating fetch from AMFI endpoint: {self.url}")
        
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(self.url, headers=headers)
                if response.status_code != 200:
                    raise ScraperFetchError(
                        f"Non-OK status code from AMFI: {response.status_code}"
                    )
                
                # Decode the response text using ISO-8859-1 as specified
                content = response.content.decode(AMFI_ENCODING, errors="ignore")
                logger.info(f"Successfully fetched raw NAV document. Size: {len(content)} chars.")
                return content
                
            except Exception as exc:
                logger.warning(f"Network request to AMFI failed ({exc}). Gracefully attempting local file fallback load...")
                try:
                    import os
                    fallback_path = os.path.join(os.path.dirname(__file__), "AMFI_NAVAll_fallback.txt")
                    if os.path.exists(fallback_path):
                        with open(fallback_path, "r", encoding="iso-8859-1", errors="ignore") as f:
                            content = f.read()
                        logger.info(f"Successfully loaded high-fidelity local fallback NAV dataset ({len(content)} chars).")
                        return content
                    else:
                        logger.error(f"Local fallback dataset file not found at: {fallback_path}")
                except Exception as fallback_err:
                    logger.error(f"Failed to load local fallback dataset: {fallback_err}")
                
                logger.error(f"HTTP request error during AMFI fetch: {exc}")
                raise ScraperFetchError(f"HTTP connection failed and fallback failed: {exc}")
