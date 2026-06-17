from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db
from api.services.fund_service import FundService
from api.schemas.fund_schema import FundListEnvelope, FundDetailResponse, AmcResponse
from api.schemas.nav_schema import NavHistoryPoint
from api.schemas.analytics_schema import SipSimulationResponse
from config.logging_config import get_logger

logger = get_logger("api.routers.funds")

router = APIRouter(
    prefix="/funds",
    tags=["Funds Explorer & Detail Pages"]
)

@router.get("", response_model=FundListEnvelope)
async def list_funds(
    category: Optional[str] = Query(None, description="Filter schemes by specific mutual fund category"),
    amc_id: Optional[int] = Query(None, description="Filter schemes by Asset Management Company ID"),
    q: Optional[str] = Query(None, description="Search query matching scheme names"),
    scheme_type: Optional[str] = Query(None, description="Filter schemes by type (e.g. Open Ended, Close Ended)"),
    asset_class: Optional[str] = Query(None, description="Filter schemes by asset class (e.g. Equity, Debt)"),
    limit: int = Query(20, ge=1, le=100, description="Pagination page limit size"),
    offset: int = Query(0, ge=0, description="Pagination page offset start"),
    db: AsyncSession = Depends(get_db)
):
    logger.debug(f"Listing funds with parameters limit={limit}, category={category}, q={q}, scheme_type={scheme_type}, asset_class={asset_class}")
    service = FundService(db)
    result = await service.get_funds_list(
        category=category, amc_id=amc_id, query=q, scheme_type=scheme_type, asset_class=asset_class, limit=limit, offset=offset
    )
    return result


@router.get("/amcs", response_model=List[AmcResponse])
async def list_amcs(
    db: AsyncSession = Depends(get_db)
):
    logger.info("Retrieving all registered Asset Management Companies (AMCs)...")
    service = FundService(db)
    amcs = await service.amc_repo.get_all()
    return [{"fund_house_id": a.fund_house_id, "name": a.name, "code": a.code} for a in amcs]


@router.get("/{scheme_id}", response_model=FundDetailResponse)
async def get_fund_details(
    scheme_id: int,
    db: AsyncSession = Depends(get_db)
):
    logger.info(f"Retrieving fund details for scheme code {scheme_id}...")
    service = FundService(db)
    result = await service.get_fund_details(scheme_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Scheme with code {scheme_id} not found.")
    return result


@router.get("/{scheme_id}/nav", response_model=List[NavHistoryPoint])
async def get_fund_nav_history(
    scheme_id: int,
    start_date: Optional[date] = Query(None, description="History start date (defaults to 1 year ago)"),
    end_date: Optional[date] = Query(None, description="History end date (defaults to today)"),
    db: AsyncSession = Depends(get_db)
):
    service = FundService(db)
    # Check if scheme exists
    details = await service.get_fund_details(scheme_id)
    if not details:
        raise HTTPException(status_code=404, detail=f"Scheme with code {scheme_id} not found.")
        
    result = await service.get_nav_history(scheme_id, start_date, end_date)
    return result


@router.get("/{scheme_id}/sim-sip", response_model=SipSimulationResponse)
async def simulate_sip(
    scheme_id: int,
    monthly_investment: float = Query(5000.0, ge=100.0, description="Monthly SIP amount in INR"),
    years: int = Query(3, ge=1, le=10, description="SIP duration in years"),
    db: AsyncSession = Depends(get_db)
):
    service = FundService(db)
    # Check if scheme exists
    details = await service.get_fund_details(scheme_id)
    if not details:
        raise HTTPException(status_code=404, detail=f"Scheme with code {scheme_id} not found.")
        
    result = await service.simulate_sip(scheme_id, monthly_investment, years)
    if not result:
        raise HTTPException(status_code=400, detail="Insufficient historical data to simulate SIP.")
    return result
