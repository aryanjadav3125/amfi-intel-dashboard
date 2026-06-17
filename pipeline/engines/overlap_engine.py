from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import Holding, PortfolioOverlap

class OverlapEngine:
    """
    Computes common holdings, overlap %, and sector similarity between two funds.
    """
    def __init__(self, session: AsyncSession):
        self.session = session

    async def generate_overlap(self, scheme_a_id: int, scheme_b_id: int):
        # Fetch holdings for A
        result_a = await self.session.execute(
            select(Holding).where(Holding.scheme_id == scheme_a_id)
        )
        holdings_a = result_a.scalars().all()
        
        # Fetch holdings for B
        result_b = await self.session.execute(
            select(Holding).where(Holding.scheme_id == scheme_b_id)
        )
        holdings_b = result_b.scalars().all()
        
        if not holdings_a or not holdings_b:
            return None
            
        dict_a = {h.company_name: h.allocation_percentage for h in holdings_a}
        dict_b = {h.company_name: h.allocation_percentage for h in holdings_b}
        
        # Calculate Overlap %
        overlap_pct = 0.0
        common_count = 0
        
        for company, alloc_a in dict_a.items():
            if company in dict_b:
                alloc_b = dict_b[company]
                # The overlap is the minimum of the two allocations
                overlap_pct += min(alloc_a, alloc_b)
                common_count += 1
                
        # Sector Similarity
        sectors_a = {}
        for h in holdings_a:
            sectors_a[h.sector] = sectors_a.get(h.sector, 0) + h.allocation_percentage
            
        sectors_b = {}
        for h in holdings_b:
            sectors_b[h.sector] = sectors_b.get(h.sector, 0) + h.allocation_percentage
            
        sector_similarity = 0.0
        for sector, alloc_a in sectors_a.items():
            if sector in sectors_b:
                sector_similarity += min(alloc_a, sectors_b[sector])
                
        # Diversification score: 100 - Overlap%
        diversification_score = 100.0 - overlap_pct
        
        # Update or create
        result = await self.session.execute(
            select(PortfolioOverlap).where(
                PortfolioOverlap.scheme_a_id == scheme_a_id,
                PortfolioOverlap.scheme_b_id == scheme_b_id
            )
        )
        overlap_record = result.scalar_one_or_none()
        
        if not overlap_record:
            # Also check reverse to maintain uniqueness if undirected, 
            # but we defined constraint on (a,b), so we keep directional A->B or just sort them
            a, b = sorted([scheme_a_id, scheme_b_id])
            overlap_record = PortfolioOverlap(scheme_a_id=a, scheme_b_id=b)
            self.session.add(overlap_record)
            
        overlap_record.overlap_percentage = overlap_pct
        overlap_record.common_holdings_count = common_count
        overlap_record.sector_similarity_score = sector_similarity
        overlap_record.diversification_score = diversification_score
        
        await self.session.commit()
        return overlap_record
