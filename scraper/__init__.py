from scraper.nav_fetcher import NavFetcher
from scraper.nav_parser import NavParser
from scraper.models import NavRecord, SchemeRecord, FundHouseRecord
from scraper.exceptions import ScraperError, ScraperFetchError, ScraperParseError

async def get_daily_nav() -> list[NavRecord]:
    """
    Exposes a clean public interface to fetch and parse daily NAV records from AMFI.
    """
    fetcher = NavFetcher()
    parser = NavParser()
    raw_text = await fetcher.fetch_raw_nav()
    _, navs = parser.parse_raw_text(raw_text)
    return navs

async def get_scheme_metadata() -> list[SchemeRecord]:
    """
    Exposes a clean public interface to fetch and parse scheme metadata records from AMFI.
    """
    fetcher = NavFetcher()
    parser = NavParser()
    raw_text = await fetcher.fetch_raw_nav()
    schemes, _ = parser.parse_raw_text(raw_text)
    return schemes
