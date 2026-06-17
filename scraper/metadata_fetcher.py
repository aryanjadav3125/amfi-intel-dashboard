from config.logging_config import get_logger
from scraper.nav_fetcher import NavFetcher

logger = get_logger("scraper.metadata_fetcher")

class MetadataFetcher:
    """
    Supplements scheme metadata fetching.
    For standard AMFI, metadata is embedded in the main NAV flat file,
    so this class delegates to NavFetcher.
    """
    def __init__(self):
        self.fetcher = NavFetcher()

    async def fetch_raw_metadata(self) -> str:
        logger.info("Fetching supplementary metadata (delegating to NavFetcher)...")
        return await self.fetcher.fetch_raw_nav()
