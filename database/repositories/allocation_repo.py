from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import AssetAllocation

class AssetAllocationRepository:
    """
    Repository class for managing operations on the AssetAllocation model.
    """
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_scheme_id(self, scheme_id: int) -> List[AssetAllocation]:
        result = await self.session.execute(
            select(AssetAllocation).where(AssetAllocation.scheme_id == scheme_id)
        )
        return list(result.scalars().all())

    async def update_allocations(self, scheme_id: int, allocations: List[dict]) -> None:
        """
        Clears existing allocations and rewrites new values for the scheme.
        """
        # Fetch existing
        existing = await self.get_by_scheme_id(scheme_id)
        for e in existing:
            await self.session.delete(e)
        
        # Add new
        for a in allocations:
            new_alloc = AssetAllocation(
                scheme_id=scheme_id,
                asset_class=a["asset_class"],
                percentage=a["percentage"],
                as_of_date=a["as_of_date"]
            )
            self.session.add(new_alloc)
        await self.session.flush()
