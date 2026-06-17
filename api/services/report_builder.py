from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database.models import Scheme, SchemeAnalytics, FundHouse, Holding
from api.services.generators.pdf_generator import PDFGenerator
from api.services.generators.excel_generator import ExcelGenerator

class ReportBuilder:
    """
    Aggregates data and dispatches to the correct format generator.
    """
    def __init__(self, session: AsyncSession):
        self.session = session
        self.pdf_generator = PDFGenerator()
        self.excel_generator = ExcelGenerator()

    async def get_fund_data(self, scheme_id: int) -> Dict[str, Any]:
        result = await self.session.execute(
            select(Scheme)
            .options(
                selectinload(Scheme.fund_house),
                selectinload(Scheme.analytics),
                selectinload(Scheme.holdings)
            )
            .where(Scheme.scheme_id == scheme_id)
        )
        scheme = result.scalar_one_or_none()
        
        if not scheme:
            return {}
            
        data = {
            "name": scheme.scheme_name,
            "category": scheme.category,
            "amc": scheme.fund_house.name if scheme.fund_house else "Unknown",
            "nav": scheme.direct_nav or scheme.regular_nav or "N/A",
            "risk": scheme.scheme_riskometer or "N/A"
        }
        
        if scheme.analytics:
            data["cagr_1y"] = round(scheme.analytics.cagr_1y, 2) if scheme.analytics.cagr_1y else "N/A"
            data["cagr_3y"] = round(scheme.analytics.cagr_3y, 2) if scheme.analytics.cagr_3y else "N/A"
            data["cagr_5y"] = round(scheme.analytics.cagr_5y, 2) if scheme.analytics.cagr_5y else "N/A"
            
        if scheme.holdings:
            sorted_holdings = sorted(scheme.holdings, key=lambda h: h.allocation_percentage, reverse=True)
            data["holdings"] = [
                {"company": h.company_name, "sector": h.sector, "allocation": round(h.allocation_percentage, 2)}
                for h in sorted_holdings
            ]
        else:
            data["holdings"] = []
            
        return data

    async def generate_fund_report(self, scheme_id: int, format_type: str) -> str:
        data = await self.get_fund_data(scheme_id)
        if not data:
            raise ValueError(f"Fund with ID {scheme_id} not found.")
            
        filename = f"report_{scheme_id}_{format_type.lower()}.{format_type.lower()}"
        
        if format_type.upper() == 'PDF':
            return self.pdf_generator.generate_fund_report(data, filename)
        elif format_type.upper() == 'EXCEL':
            return self.excel_generator.generate_fund_report(data, filename)
        else:
            raise ValueError(f"Unsupported format {format_type}")
