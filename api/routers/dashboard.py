"""
Dashboard API Router

Provides high-level aggregated metrics for the dashboard overview.
Currently returns static snapshot data, but designed to interface with
an AnalyticsCache or direct DB aggregation in production.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/overview")
async def get_dashboard_overview(db: AsyncSession = Depends(get_db)):
    """
    Retrieves high-level summary metrics for the platform.
    
    Returns:
        dict: A dictionary containing structural metrics like total funds, 
              categories, AMCs, and the latest NAV ingestion date.
    """
    # In a real implementation, this would fetch from AnalyticsCache or execute COUNT() aggregations
    return {
        "total_funds": 15238,
        "total_categories": 42,
        "total_amcs": 45,
        "latest_nav_update": "2026-06-16"
    }
