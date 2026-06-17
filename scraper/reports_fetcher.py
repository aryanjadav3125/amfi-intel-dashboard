import httpx
from datetime import date
from typing import Optional
from config.settings import settings
from config.logging_config import get_logger
from scraper.retry import async_retry
from scraper.exceptions import ScraperFetchError

logger = get_logger("scraper.reports_fetcher")

class ReportsFetcher:
    """
    Handles raw text downloads and historical NAV query requests from AMFI.
    """
    
    REPORT_URLS = {
        "all": "https://www.amfiindia.com/spages/NAVAll.txt",
        "open": "https://portal.amfiindia.com/spages/NAVOpen.txt",
        "close": "https://portal.amfiindia.com/spages/NAVClose.txt",
        "interval": "https://portal.amfiindia.com/spages/NAVInterval.txt"
    }

    HISTORY_ENDPOINT = "http://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx"

    def __init__(self, timeout: int = None):
        self.timeout = timeout or settings.SCRAPER_TIMEOUT
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        }

    @async_retry(exceptions=(httpx.HTTPError, httpx.TimeoutException))
    async def fetch_nav_report(self, report_type: str) -> str:
        """
        Fetches one of the 4 daily plain text NAV reports (all, open, close, interval).
        """
        url = self.REPORT_URLS.get(report_type.lower())
        if not url:
            raise ValueError(f"Invalid report type: {report_type}. Options are: {list(self.REPORT_URLS.keys())}")

        logger.info(f"Downloading daily NAV text report ({report_type}) from: {url}")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url, headers=self.headers)
                if response.status_code != 200:
                    raise ScraperFetchError(f"AMFI returned status code: {response.status_code}")
                
                # Decode the response text using ISO-8859-1
                content = response.content.decode("iso-8859-1", errors="ignore")
                logger.info(f"Report downloaded. Character count: {len(content)}")
                return content
            except httpx.RequestError as exc:
                logger.error(f"HTTP error downloading NAV report: {exc}")
                raise ScraperFetchError(f"HTTP request failed: {exc}")

    @async_retry(exceptions=(httpx.HTTPError, httpx.TimeoutException))
    async def fetch_nav_history(self, mf_id: Optional[str] = "", scheme_type: Optional[str] = "", from_date: Optional[date] = None, to_date: Optional[date] = None) -> str:
        """
        Queries historical NAV text file via portal.amfiindia.com with parameters.
        Parameters:
            mf: Mutual Fund code (AMC)
            tp: Scheme Type (Open-ended/Close-ended/Interval)
            frmdt: from date (dd-MMM-yyyy)
            todt: to date (dd-MMM-yyyy)
        """
        # Format dates as dd-MMM-yyyy (e.g. 20-May-2026)
        from_str = from_date.strftime("%d-%b-%Y") if from_date else ""
        to_str = to_date.strftime("%d-%b-%Y") if to_date else ""

        params = {}
        if mf_id:
            params["mf"] = str(mf_id)
        if scheme_type:
            params["tp"] = str(scheme_type)
        if from_str:
            params["frmdt"] = from_str
        if to_str:
            params["todt"] = to_str

        logger.info(f"Querying AMFI historical NAV from {self.HISTORY_ENDPOINT} with params: {params}")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(self.HISTORY_ENDPOINT, params=params, headers=self.headers)
                if response.status_code != 200:
                    raise ScraperFetchError(f"AMFI historical query returned status: {response.status_code}")
                
                content = response.content.decode("iso-8859-1", errors="ignore")
                logger.info(f"Historical report downloaded. Size: {len(content)} chars.")
                return content
            except httpx.RequestError as exc:
                logger.error(f"HTTP error querying historical NAV: {exc}")
                raise ScraperFetchError(f"Historical query failed: {exc}")
