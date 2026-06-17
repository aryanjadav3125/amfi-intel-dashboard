from datetime import date, timedelta
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from api.services.fund_service import FundService
from config.logging_config import get_logger

logger = get_logger("api.services.compare")

class CompareService:
    """
    Handles operations for comparing multiple mutual fund schemes.
    """
    def __init__(self, session: AsyncSession):
        self.session = session
        self.fund_service = FundService(session)

    async def compare_funds(self, scheme_ids: List[int], start_date: date = None, end_date: date = None) -> Dict[str, Any]:
        """
        Compiles structural performance metrics and normalized baseline returns (₹10,000 invested)
        for multiple schemes over a matching time range.
        """
        if not start_date:
            start_date = date.today() - timedelta(days=365)
        if not end_date:
            end_date = date.today()

        comparison_matrix = []
        chart_series: Dict[str, List[Dict[str, Any]]] = {}

        for sid in scheme_ids:
            details = await self.fund_service.get_fund_details(sid)
            if not details:
                continue

            # Add to matrix
            comparison_matrix.append({
                "scheme_id": details["scheme_id"],
                "scheme_name": details["scheme_name"],
                "category": details["category"],
                "latest_nav": details["latest_nav"],
                "cagr_1y": details["metrics"]["cagr_1y"],
                "cagr_3y": details["metrics"]["cagr_3y"],
                "volatility": details["metrics"]["volatility"],
                "sharpe_ratio": details["metrics"]["sharpe_ratio"],
                "max_drawdown": details["metrics"]["max_drawdown"]
            })

            # Fetch NAV history for charting
            navs = await self.fund_service.get_nav_history(sid, start_date, end_date)
            if not navs:
                continue

            start_nav_val = navs[0]["nav"]
            series = []
            
            for pt in navs:
                # Normalize base value to 10000 INR
                normalized_value = 10000.0
                if start_nav_val > 0:
                    normalized_value = 10000.0 * (pt["nav"] / start_nav_val)

                series.append({
                    "date": pt["date"],
                    "nav": pt["nav"],
                    "value": round(normalized_value, 2)
                })

            chart_series[str(sid)] = series

        # Pivot chart series into a unified time series structure for Recharts compatibility
        # format: list of { date: "YYYY-MM-DD", "scheme_119551": value1, "scheme_120123": value2 }
        unified_chart = []
        dates_seen = set()
        
        # Collect all unique dates across series
        for series in chart_series.values():
            for pt in series:
                dates_seen.add(pt["date"])

        sorted_dates = sorted(list(dates_seen))

        # Build chart rows
        for d in sorted_dates:
            row = {"date": d}
            for sid, series in chart_series.items():
                # Find value on this date
                val = next((pt["value"] for pt in series if pt["date"] == d), None)
                if val is not None:
                    row[f"scheme_{sid}"] = val
            unified_chart.append(row)

        return {
            "matrix": comparison_matrix,
            "chart": unified_chart
        }
