import pytest
import httpx
from datetime import date
from unittest.mock import AsyncMock, MagicMock
from scraper.reports_fetcher import ReportsFetcher
from scraper.exceptions import ScraperFetchError

async def call_undecorated(instance, method_name, *args, **kwargs):
    bound_method = getattr(instance, method_name)
    func = getattr(bound_method, "__func__", bound_method)
    undecorated = getattr(func, "__wrapped__", None)
    print(f"DEBUG: call_undecorated {method_name} - bound_method: {bound_method}, func: {func}, undecorated: {undecorated}")
    if undecorated:
        return await undecorated(instance, *args, **kwargs)
    return await bound_method(*args, **kwargs)

@pytest.mark.asyncio
async def test_fetch_nav_report_invalid_type():
    fetcher = ReportsFetcher()
    with pytest.raises(ValueError) as exc:
        await call_undecorated(fetcher, "fetch_nav_report", "invalid")
    assert "Invalid report type" in str(exc.value)

@pytest.mark.asyncio
async def test_fetch_nav_report_success(mocker):
    # Mock httpx AsyncClient
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"Scheme Code;Scheme Name;Net Asset Value\n119551;HDFC Index Fund;384.51"
    
    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(return_value=mock_response)
    
    mocker.patch("httpx.AsyncClient", return_value=mock_client)
    
    fetcher = ReportsFetcher()
    content = await call_undecorated(fetcher, "fetch_nav_report", "all")
    assert "HDFC Index Fund" in content
    mock_client.get.assert_called_once_with(
        "https://www.amfiindia.com/spages/NAVAll.txt",
        headers=fetcher.headers
    )

@pytest.mark.asyncio
async def test_fetch_nav_report_http_error(mocker):
    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    
    # Create a real httpx.RequestError
    dummy_request = httpx.Request("GET", "https://portal.amfiindia.com/spages/NAVOpen.txt")
    mock_client.get = AsyncMock(side_effect=httpx.RequestError("Connection refused", request=dummy_request))
    mocker.patch("httpx.AsyncClient", return_value=mock_client)
    
    fetcher = ReportsFetcher()
    with pytest.raises(ScraperFetchError):
        await call_undecorated(fetcher, "fetch_nav_report", "open")

@pytest.mark.asyncio
async def test_fetch_nav_history_success(mocker):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"Historical NAV Data"
    
    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(return_value=mock_response)
    
    mocker.patch("httpx.AsyncClient", return_value=mock_client)
    
    fetcher = ReportsFetcher()
    from_dt = date(2026, 5, 1)
    to_dt = date(2026, 5, 20)
    
    content = await call_undecorated(
        fetcher,
        "fetch_nav_history",
        mf_id="9",
        scheme_type="Open",
        from_date=from_dt,
        to_date=to_dt
    )
    
    assert content == "Historical NAV Data"
    mock_client.get.assert_called_once_with(
        fetcher.HISTORY_ENDPOINT,
        params={
            "mf": "9",
            "tp": "Open",
            "frmdt": "01-May-2026",
            "todt": "20-May-2026"
        },
        headers=fetcher.headers
    )
