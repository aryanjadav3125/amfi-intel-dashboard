import pytest
from unittest.mock import AsyncMock, patch
import notifications

@pytest.mark.asyncio
async def test_send_success_logs():
    """
    Verifies that calling send_success triggers console logs/channels properly.
    """
    with patch("notifications.notifier.get_notifier_channel") as mock_get_channel:
        mock_channel = AsyncMock()
        mock_get_channel.return_value = mock_channel
        
        await notifications.send_success("Run completed with 10 records.")
        
        mock_channel.send.assert_called_once_with(
            "🚀 AMFI Ingestion Pipeline - RUN SUCCESS",
            "Run completed with 10 records."
        )


@pytest.mark.asyncio
async def test_send_failure_logs():
    """
    Verifies that calling send_failure triggers channels properly.
    """
    with patch("notifications.notifier.get_notifier_channel") as mock_get_channel:
        mock_channel = AsyncMock()
        mock_get_channel.return_value = mock_channel
        
        await notifications.send_failure("Scrape failed due to timeout.")
        
        mock_channel.send.assert_called_once_with(
            "⚠️ AMFI Ingestion Pipeline - RUN FAILURE",
            "Scrape failed due to timeout."
        )
