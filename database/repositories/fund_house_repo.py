from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import FundHouse
from config.logging_config import get_logger

logger = get_logger("database.fund_house_repo")

class FundHouseRepository:
    """
    Repository class for managing operations on the FundHouse model.
    """
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, fund_house_id: int) -> Optional[FundHouse]:
        result = await self.session.execute(
            select(FundHouse).where(FundHouse.fund_house_id == fund_house_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[FundHouse]:
        result = await self.session.execute(
            select(FundHouse).where(FundHouse.name == name)
        )
        return result.scalar_one_or_none()

    async def get_or_create(self, name: str, code: str = None) -> FundHouse:
        """
        Retrieves an AMC by name or inserts a new one if it does not exist.
        """
        amc = await self.get_by_name(name)
        if amc:
            return amc
        
        amc = FundHouse(name=name, code=code)
        self.session.add(amc)
        await self.session.flush()  # Populates AMC ID
        logger.debug(f"Created new Fund House entry: {name}")
        return amc

    async def get_all(self) -> List[FundHouse]:
        result = await self.session.execute(select(FundHouse).order_by(FundHouse.name))
        return list(result.scalars().all())
