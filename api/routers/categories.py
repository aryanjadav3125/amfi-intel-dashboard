from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db
from api.services.fund_service import FundService
from database.models import Scheme
from config.logging_config import get_logger

logger = get_logger("api.routers.categories")

router = APIRouter(
    prefix="/categories",
    tags=["Categories heatmaps & Leaders"]
)

@router.get("", response_model=List[str])
async def list_categories(
    db: AsyncSession = Depends(get_db)
):
    """
    Exposes a distinct list of all mutual fund categories populated in the system.
    """
    logger.debug("Fetching distinct mutual fund categories...")
    service = FundService(db)
    result = await service.scheme_repo.get_all_categories()
    return result


@router.get("/summary", response_model=List[Dict[str, Any]])
async def get_categories_summary(
    db: AsyncSession = Depends(get_db)
):
    """
    Returns an aggregated list of categories with fund counts.
    Useful for landing pages and summaries.
    """
    service = FundService(db)
    categories = await service.scheme_repo.get_all_categories()
    
    summary = []
    for cat in categories:
        # Query total schemes inside category
        from sqlalchemy import func
        result = await db.execute(
            select(func.count(Scheme.scheme_id)).where(Scheme.category == cat)
        )
        count = result.scalar() or 0
        
        summary.append({
            "category": cat,
            "fund_count": count
        })
        
    return summary


@router.get("/{category}/leaders", response_model=List[Dict[str, Any]])
async def get_category_leaders(
    category: str,
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns mutual funds inside the specified category, sorted by their 1-year performance.
    """
    service = FundService(db)
    funds_envelope = await service.get_funds_list(category=category, limit=200)
    funds = funds_envelope["funds"]
    
    # Sort funds by 1-year CAGR descending. Keep None values at bottom.
    leaders = sorted(
        funds,
        key=lambda x: x["cagr_1y"] if x["cagr_1y"] is not None else -9999.0,
        reverse=True
    )
    
    return leaders[:limit]
