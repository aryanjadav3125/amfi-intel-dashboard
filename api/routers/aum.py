from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db
from database.models import FundHouseAum, CategoryAum, FundHouse
from config.logging_config import get_logger

logger = get_logger("api.routers.aum")

router = APIRouter(
    prefix="/aum",
    tags=["AUM Disclosures & League Tables"]
)

@router.get("/summary")
async def get_aum_summary(
    period: str = "Q4 2025-26",
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Returns aggregated AMC average AUM, AAUM disclosures, folio counts, and splits.
    """
    logger.info(f"Retrieving AUM summary disclosures for period: {period}")
    
    stmt = (
        select(FundHouseAum, FundHouse.name)
        .join(FundHouse, FundHouse.fund_house_id == FundHouseAum.fund_house_id)
        .where(FundHouseAum.period == period)
        .order_by(FundHouseAum.average_aum.desc())
    )
    
    result = await db.execute(stmt)
    rows = result.all()
    
    if not rows:
        # Fallback if no records found for period, get the latest period
        latest_period_stmt = select(FundHouseAum.period).order_by(FundHouseAum.aum_id.desc()).limit(1)
        latest_res = await db.execute(latest_period_stmt)
        latest_period = latest_res.scalar_one_or_none()
        
        if latest_period:
            logger.info(f"No records for {period}. Falling back to latest period: {latest_period}")
            stmt = (
                select(FundHouseAum, FundHouse.name)
                .join(FundHouse, FundHouse.fund_house_id == FundHouseAum.fund_house_id)
                .where(FundHouseAum.period == latest_period)
                .order_by(FundHouseAum.average_aum.desc())
            )
            result = await db.execute(stmt)
            rows = result.all()
            period = latest_period
            
    amc_metrics = []
    total_avg_aum = 0.0
    total_aaum = 0.0
    total_folios = 0
    
    total_direct_aum = 0.0
    total_regular_aum = 0.0
    
    for row in rows:
        aum_model, amc_name = row
        total_avg_aum += aum_model.average_aum
        total_aaum += aum_model.aaum
        total_folios += aum_model.folio_count or 0
        total_direct_aum += aum_model.direct_aum or 0.0
        total_regular_aum += aum_model.regular_aum or 0.0
        
        amc_metrics.append({
            "fund_house_id": aum_model.fund_house_id,
            "amc_name": amc_name,
            "average_aum": aum_model.average_aum,
            "aaum": aum_model.aaum,
            "direct_aum": aum_model.direct_aum,
            "regular_aum": aum_model.regular_aum,
            "t15_aum": aum_model.t15_aum,
            "b15_aum": aum_model.b15_aum,
            "folio_count": aum_model.folio_count
        })
        
    direct_percentage = (total_direct_aum / (total_direct_aum + total_regular_aum) * 100) if (total_direct_aum + total_regular_aum) > 0 else 0.0
    
    return {
        "period": period,
        "total_avg_aum": round(total_avg_aum, 2),
        "total_aaum": round(total_aaum, 2),
        "total_folios": total_folios,
        "direct_percentage": round(direct_percentage, 2),
        "regular_percentage": round(100.0 - direct_percentage, 2),
        "amcs": amc_metrics
    }


@router.get("/categories")
async def get_category_aum(
    period: str = "April 2026",
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Returns category-wise AUM statistics and percentage allocations.
    """
    logger.info(f"Retrieving category AUM disclosures for period: {period}")
    
    stmt = (
        select(CategoryAum)
        .where(CategoryAum.period == period)
        .order_by(CategoryAum.aum_value.desc())
    )
    
    result = await db.execute(stmt)
    categories = list(result.scalars().all())
    
    if not categories:
        # Fallback to latest
        latest_period_stmt = select(CategoryAum.period).order_by(CategoryAum.category_aum_id.desc()).limit(1)
        latest_res = await db.execute(latest_period_stmt)
        latest_period = latest_res.scalar_one_or_none()
        
        if latest_period:
            logger.info(f"No records for {period}. Falling back to latest period: {latest_period}")
            stmt = (
                select(CategoryAum)
                .where(CategoryAum.period == latest_period)
                .order_by(CategoryAum.aum_value.desc())
            )
            result = await db.execute(stmt)
            categories = list(result.scalars().all())
            
    return [
        {
            "category": c.category,
            "period": c.period,
            "aum_value": c.aum_value,
            "folio_count": c.folio_count,
            "percentage_of_total": c.percentage_of_total
        }
        for c in categories
    ]
