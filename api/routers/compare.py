from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db
from api.services.compare_service import CompareService
from api.schemas.analytics_schema import CompareResponseEnvelope
from config.logging_config import get_logger

logger = get_logger("api.routers.compare")

router = APIRouter(
    prefix="/compare",
    tags=["Multi-Fund Comparison Engine"]
)

@router.get("", response_model=CompareResponseEnvelope)
async def compare_funds(
    ids: str = Query(..., description="Comma-separated list of AMFI mutual fund scheme codes, e.g. 119551,120123"),
    start_date: Optional[date] = Query(None, description="Start date of comparative window"),
    end_date: Optional[date] = Query(None, description="End date of comparative window"),
    db: AsyncSession = Depends(get_db)
):
    logger.info(f"Triggering comparison query for scheme IDs: {ids}")
    
    # Parse list of integers
    try:
        scheme_ids = [int(x.strip()) for x in ids.split(",") if x.strip()]
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid format for 'ids'. Must be a comma-separated list of integers."
        )

    if not scheme_ids:
        raise HTTPException(
            status_code=400,
            detail="The 'ids' parameter cannot be empty."
        )

    service = CompareService(db)
    result = await service.compare_funds(scheme_ids, start_date, end_date)
    return result
