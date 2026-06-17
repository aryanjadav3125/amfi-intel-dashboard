from datetime import date, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from database.repositories import SchemeRepository, NavDailyRepository, FundHouseRepository
from api.services.analytics_service import AnalyticsService
from config.logging_config import get_logger

logger = get_logger("api.services.fund")

class FundService:
    """
    Orchestrates queries from repositories and processes objects for API layers.
    """
    def __init__(self, session: AsyncSession):
        self.session = session
        self.scheme_repo = SchemeRepository(session)
        self.nav_repo = NavDailyRepository(session)
        self.amc_repo = FundHouseRepository(session)

    async def get_funds_list(self, category: str = None, amc_id: int = None, query: str = None, scheme_type: str = None, asset_class: str = None, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """
        Retrieves a paginated list of mutual fund schemes, filterable by category, AMC, scheme type, and asset class.
        """
        from sqlalchemy import select
        from database.models import Scheme
        
        stmt = select(Scheme)
        
        # Apply filters
        if category:
            stmt = stmt.where(Scheme.category == category)
        if amc_id:
            stmt = stmt.where(Scheme.fund_house_id == amc_id)
        if scheme_type:
            stmt = stmt.where(Scheme.scheme_type == scheme_type)
        if asset_class:
            stmt = stmt.where(Scheme.asset_class == asset_class)
        if query:
            stmt = stmt.where(Scheme.scheme_name.ilike(f"%{query}%"))
            
        stmt = stmt.order_by(Scheme.scheme_name)
        
        # Query total count
        from sqlalchemy import func
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_count_res = await self.session.execute(count_stmt)
        total_count = total_count_res.scalar() or 0
        
        # Apply pagination
        stmt = stmt.limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        schemes = list(result.scalars().all())
        
        # Enrich schemes with latest NAV value and 1-year CAGR
        enriched_funds = []
        for s in schemes:
            navs = await self.nav_repo.get_by_scheme_id(s.scheme_id, limit=5)
            latest_nav = navs[0].nav_value if navs else 0.0
            latest_date = navs[0].nav_date if navs else None
            
            # Fetch 1 year CAGR dynamically or return placeholder
            all_navs = await self.nav_repo.get_by_scheme_id(s.scheme_id, limit=1000)
            all_navs.reverse()  # chronological order
            cagr_1y = AnalyticsService.calculate_cagr(all_navs, 365)
            
            enriched_funds.append({
                "scheme_id": s.scheme_id,
                "scheme_name": s.scheme_name,
                "category": s.category,
                "scheme_type": s.scheme_type,
                "latest_nav": s.direct_nav or latest_nav,
                "latest_date": latest_date,
                "cagr_1y": cagr_1y,
                
                # High-fidelity performance metrics
                "asset_class": s.asset_class,
                "benchmark_name": s.benchmark_name,
                "scheme_riskometer": s.scheme_riskometer,
                "benchmark_riskometer": s.benchmark_riskometer,
                "regular_nav": s.regular_nav,
                "direct_nav": s.direct_nav,
                "regular_cagr_5y": s.regular_cagr_5y,
                "direct_cagr_5y": s.direct_cagr_5y,
                "benchmark_cagr_5y": s.benchmark_cagr_5y,
                "regular_info_ratio": s.regular_info_ratio,
                "direct_info_ratio": s.direct_info_ratio,
                "daily_aum": s.daily_aum
            })
            
        return {
            "funds": enriched_funds,
            "total": total_count
        }

    async def get_fund_details(self, scheme_id: int) -> Optional[Dict[str, Any]]:
        """
        Returns full detailed scheme metadata, asset allocation, and precomputed risk metrics.
        """
        scheme = await self.scheme_repo.get_by_id(scheme_id)
        if not scheme:
            return None
            
        # Get allocations
        from database.repositories import AssetAllocationRepository
        alloc_repo = AssetAllocationRepository(self.session)
        allocations = await alloc_repo.get_by_scheme_id(scheme_id)
        
        # Get NAV history
        navs = await self.nav_repo.get_by_scheme_id(scheme_id, limit=1000)
        navs.reverse()  # chronological order
        
        # Compute performance metrics dynamically
        cagr_1y = AnalyticsService.calculate_cagr(navs, 365)
        cagr_3y = AnalyticsService.calculate_cagr(navs, 365 * 3)
        
        ratios = AnalyticsService.calculate_volatility_and_ratios(navs)
        
        latest_nav = navs[-1].nav_value if navs else (scheme.direct_nav or 0.0)
        latest_date = navs[-1].nav_date if navs else None
        
        return {
            "scheme_id": scheme.scheme_id,
            "scheme_name": scheme.scheme_name,
            "category": scheme.category,
            "scheme_type": scheme.scheme_type,
            "isin_growth": scheme.isin_growth,
            "isin_div_payout": scheme.isin_div_payout,
            "latest_nav": latest_nav,
            "latest_date": latest_date,
            "allocations": [
                {"asset_class": a.asset_class, "percentage": a.percentage} for a in allocations
            ],
            "metrics": {
                "cagr_1y": cagr_1y,
                "cagr_3y": cagr_3y,
                "volatility": ratios["volatility"],
                "sharpe_ratio": ratios["sharpe_ratio"],
                "sortino_ratio": ratios["sortino_ratio"],
                "max_drawdown": ratios["max_drawdown"]
            },
            
            # Enriched side-by-side performance metrics
            "asset_class": scheme.asset_class,
            "benchmark_name": scheme.benchmark_name,
            "scheme_riskometer": scheme.scheme_riskometer,
            "benchmark_riskometer": scheme.benchmark_riskometer,
            "regular_nav": scheme.regular_nav,
            "direct_nav": scheme.direct_nav,
            "regular_cagr_5y": scheme.regular_cagr_5y,
            "direct_cagr_5y": scheme.direct_cagr_5y,
            "benchmark_cagr_5y": scheme.benchmark_cagr_5y,
            "regular_info_ratio": scheme.regular_info_ratio,
            "direct_info_ratio": scheme.direct_info_ratio,
            "daily_aum": scheme.daily_aum
        }
        
    async def get_nav_history(self, scheme_id: int, start_date: date = None, end_date: date = None) -> List[Dict[str, Any]]:
        """
        Retrieves a sorted list of daily NAV history points.
        """
        if not start_date:
            start_date = date.today() - timedelta(days=365)
        if not end_date:
            end_date = date.today()
            
        navs = await self.nav_repo.get_nav_by_scheme_and_range(scheme_id, start_date, end_date)
        return [
            {"date": n.nav_date, "nav": n.nav_value, "regular_nav": n.regular_nav_value} for n in navs
        ]

    async def simulate_sip(self, scheme_id: int, monthly_investment: float = 5000.0, years: int = 3) -> Optional[Dict[str, Any]]:
        """
        Simulates an Indian mutual fund SIP investment using actual historical NAV time-series.
        Monthly investments are triggered on the first trading day of every month in the history.
        """
        # Fetch NAV points chronologically
        navs = await self.nav_repo.get_by_scheme_id(scheme_id, limit=365 * years)
        navs.reverse()
        
        if not navs:
            return None
            
        total_units = 0.0
        total_invested = 0.0
        current_month = None
        
        chart_points = []
        
        for n in navs:
            # Check month crossing to buy units
            n_date = n.nav_date
            n_val = n.nav_value
            
            if n_val <= 0:
                continue
                
            if current_month is None:
                # First investment
                current_month = n_date.month
                total_invested += monthly_investment
                total_units += monthly_investment / n_val
            elif n_date.month != current_month:
                # Crossed month boundaries - invest monthly contribution
                current_month = n_date.month
                total_invested += monthly_investment
                total_units += monthly_investment / n_val
                
            current_value = total_units * n_val
            chart_points.append({
                "date": n_date,
                "invested": round(total_invested, 2),
                "value": round(current_value, 2)
            })
            
        if not chart_points:
            return None
            
        final_val = chart_points[-1]["value"]
        profit = final_val - total_invested
        abs_ret = (profit / total_invested) * 100.0 if total_invested > 0 else 0.0
        
        # Calculate dynamic CAGR of the SIP portfolio
        ann_ret = None
        days = (navs[-1].nav_date - navs[0].nav_date).days
        if days > 0 and total_invested > 0:
            ann_ret = ((final_val / total_invested) ** (365.0 / days)) - 1.0
            ann_ret = round(ann_ret * 100.0, 2)  # Percentage representation
            
        return {
            "total_investment": total_invested,
            "final_value": final_val,
            "profit": round(profit, 2),
            "absolute_returns": round(abs_ret, 2),
            "annualized_returns": ann_ret,
            "chart": chart_points
        }

