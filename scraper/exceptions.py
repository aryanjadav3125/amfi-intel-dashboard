class ScraperError(Exception):
    """Base exception for all scraper operations."""
    pass

class ScraperFetchError(ScraperError):
    """Raised when fetching raw data from AMFI fails."""
    pass

class ScraperParseError(ScraperError):
    """Raised when parsing raw AMFI files fails."""
    pass
