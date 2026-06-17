from typing import List, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Holding

class HoldingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_scheme_id(self, scheme_id: int) -> List[Holding]:
        result = await self.session.execute(
            select(Holding).where(Holding.scheme_id == scheme_id).order_by(Holding.allocation_percentage.desc())
        )
        return list(result.scalars().all())

    async def get_sector_breakdown(self, scheme_id: int) -> List[Dict[str, Any]]:
        result = await self.session.execute(
            select(Holding.sector, func.sum(Holding.allocation_percentage).label("total_allocation"))
            .where(Holding.scheme_id == scheme_id)
            .group_by(Holding.sector)
            .order_by(func.sum(Holding.allocation_percentage).desc())
        )
        
        breakdown = []
        for row in result.all():
            breakdown.append({
                "sector": row[0],
                "allocation": float(row[1])
            })
        return breakdown

    async def update_holdings(self, scheme_id: int, holdings_data: List[dict]) -> None:
        """
        Clears existing holdings and rewrites new values for the scheme.
        """
        # Fetch existing
        existing = await self.get_by_scheme_id(scheme_id)
        for e in existing:
            await self.session.delete(e)
        
        # Add new
        for h in holdings_data:
            new_holding = Holding(
                scheme_id=scheme_id,
                company_name=h["company_name"],
                sector=h["sector"],
                allocation_percentage=h["allocation_percentage"],
                isin=h.get("isin"),
                market_value=h.get("market_value"),
                as_of_date=h["as_of_date"]
            )
            self.session.add(new_holding)
        await self.session.flush()
