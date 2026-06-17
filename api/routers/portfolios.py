from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from api.dependencies import get_db
from database.models import Portfolio, PortfolioFund, Scheme, PortfolioOverlap, Holding
from api.routers.auth import get_current_user
from collections import defaultdict

router = APIRouter(prefix="/portfolios", tags=["portfolios"])

class PortfolioCreate(BaseModel):
    name: str
    description: Optional[str] = None

class PortfolioFundCreate(BaseModel):
    scheme_id: int
    allocation_percentage: float
    invested_amount: Optional[float] = None

class PortfolioResponse(BaseModel):
    portfolio_id: int
    name: str
    description: Optional[str]
    
    class Config:
        from_attributes = True

@router.post("", response_model=PortfolioResponse)
async def create_portfolio(portfolio_in: PortfolioCreate, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    portfolio = Portfolio(
        user_id=current_user.user_id,
        name=portfolio_in.name,
        description=portfolio_in.description
    )
    db.add(portfolio)
    await db.commit()
    await db.refresh(portfolio)
    return portfolio

@router.get("", response_model=List[PortfolioResponse])
async def get_portfolios(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    result = await db.execute(select(Portfolio).where(Portfolio.user_id == current_user.user_id))
    return list(result.scalars().all())

@router.post("/{portfolio_id}/funds")
async def add_fund_to_portfolio(portfolio_id: int, fund_in: PortfolioFundCreate, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    # Verify portfolio ownership
    result = await db.execute(select(Portfolio).where(Portfolio.portfolio_id == portfolio_id, Portfolio.user_id == current_user.user_id))
    portfolio = result.scalar_one_or_none()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
        
    pf = PortfolioFund(
        portfolio_id=portfolio_id,
        scheme_id=fund_in.scheme_id,
        allocation_percentage=fund_in.allocation_percentage,
        invested_amount=fund_in.invested_amount
    )
    db.add(pf)
    try:
        await db.commit()
        await db.refresh(pf)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Fund might already be in this portfolio")
    return {"status": "success", "portfolio_fund_id": pf.id}

@router.post("/overlap")
async def calculate_overlap(funds: List[int], db: AsyncSession = Depends(get_db)):
    """
    Given a list of scheme_ids, return their overlap matrices.
    """
    if len(funds) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 funds to calculate overlap")
        
    result = await db.execute(select(Holding).where(Holding.scheme_id.in_(funds)))
    all_holdings = result.scalars().all()
    
    holdings_by_fund = defaultdict(dict)
    sectors_by_fund = defaultdict(dict)
    for h in all_holdings:
        holdings_by_fund[h.scheme_id][h.company_name] = h.allocation_percentage
        sectors_by_fund[h.scheme_id][h.sector] = sectors_by_fund[h.scheme_id].get(h.sector, 0) + h.allocation_percentage
        
    if not holdings_by_fund or len(holdings_by_fund) < 2:
        return {
            "common_holdings": [],
            "overlap_percentage": 0.0,
            "sector_similarity": {},
            "diversification_score": 100.0,
            "concentration_risk": "Low"
        }
        
    common_companies = set(list(holdings_by_fund.values())[0].keys())
    for f_id in holdings_by_fund:
        common_companies = common_companies.intersection(set(holdings_by_fund[f_id].keys()))
        
    total_overlap = 0.0
    pairs = 0
    fund_ids = list(holdings_by_fund.keys())
    for i in range(len(fund_ids)):
        for j in range(i + 1, len(fund_ids)):
            f1, f2 = fund_ids[i], fund_ids[j]
            overlap = 0.0
            for company, alloc in holdings_by_fund[f1].items():
                if company in holdings_by_fund[f2]:
                    overlap += min(alloc, holdings_by_fund[f2][company])
            total_overlap += overlap
            pairs += 1
            
    avg_overlap = (total_overlap / pairs) if pairs > 0 else 0.0
    
    portfolio_sectors = defaultdict(float)
    for f_id, sectors in sectors_by_fund.items():
        for sector, alloc in sectors.items():
            portfolio_sectors[sector] += (alloc / len(fund_ids))
            
    sorted_sectors = dict(sorted(portfolio_sectors.items(), key=lambda x: x[1], reverse=True)[:5])
    diversification_score = max(0, 100.0 - avg_overlap)
    concentration_risk = "High" if avg_overlap > 50 else ("Medium" if avg_overlap > 25 else "Low")
    
    return {
        "common_holdings": list(common_companies)[:10],
        "overlap_percentage": round(avg_overlap, 1),
        "sector_similarity": {k: round(v, 1) for k, v in sorted_sectors.items()},
        "diversification_score": round(diversification_score, 1),
        "concentration_risk": concentration_risk
    }

@router.get("/{portfolio_id}/analytics")
async def get_portfolio_analytics(portfolio_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    # Dummy response for demonstration
    return {
        "portfolio_cagr": 15.2,
        "risk_score": 72.5,
        "sector_exposure": {
            "Financials": 30.5,
            "IT": 20.0,
            "Energy": 15.0
        },
        "diversification": "High"
    }
