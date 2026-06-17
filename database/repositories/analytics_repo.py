from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import SchemeAnalytics

class SchemeAnalyticsRepository:
    """
    Repository class for managing operations on pre-computed Scheme Analytics metrics.
    """
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_scheme_id(self, scheme_id: int) -> Optional[SchemeAnalytics]:
        result = await self.session.execute(
            select(SchemeAnalytics).where(SchemeAnalytics.scheme_id == scheme_id)
        )
        return result.scalar_one_or_none()

    async def get_all_analytics(self) -> List[SchemeAnalytics]:
        result = await self.session.execute(select(SchemeAnalytics))
        return list(result.scalars().all())

    async def upsert_analytics(self, scheme_id: int, metrics: dict) -> SchemeAnalytics:
        """
        Inserts or updates the precomputed derived mathematical results.
        """
        analytics = await self.get_by_scheme_id(scheme_id)
        if not analytics:
            analytics = SchemeAnalytics(scheme_id=scheme_id)
            self.session.add(analytics)
        
        for k, v in metrics.items():
            if hasattr(analytics, k):
                setattr(analytics, k, v)
        
        await self.session.flush()
        return analytics
