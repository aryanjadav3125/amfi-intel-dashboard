from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User, SavedFund, SavedComparison, RecentSearch, Scheme

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.user_id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create_user(self, email: str, hashed_password: str, full_name: Optional[str] = None) -> User:
        user = User(email=email, hashed_password=hashed_password, full_name=full_name)
        self.session.add(user)
        await self.session.flush()
        return user

    async def add_saved_fund(self, user_id: int, scheme_id: int) -> SavedFund:
        # Check if already saved
        result = await self.session.execute(
            select(SavedFund).where(SavedFund.user_id == user_id, SavedFund.scheme_id == scheme_id)
        )
        existing = result.scalar_one_or_none()
        if existing:
            return existing

        saved_fund = SavedFund(user_id=user_id, scheme_id=scheme_id)
        self.session.add(saved_fund)
        await self.session.flush()
        return saved_fund

    async def remove_saved_fund(self, user_id: int, scheme_id: int) -> bool:
        result = await self.session.execute(
            select(SavedFund).where(SavedFund.user_id == user_id, SavedFund.scheme_id == scheme_id)
        )
        existing = result.scalar_one_or_none()
        if existing:
            await self.session.delete(existing)
            await self.session.flush()
            return True
        return False

    async def get_saved_funds(self, user_id: int) -> List[Scheme]:
        # Join with Scheme to get full details
        result = await self.session.execute(
            select(Scheme).join(SavedFund, SavedFund.scheme_id == Scheme.scheme_id).where(SavedFund.user_id == user_id)
        )
        return list(result.scalars().all())

    async def get_saved_comparisons(self, user_id: int) -> List[SavedComparison]:
        result = await self.session.execute(select(SavedComparison).where(SavedComparison.user_id == user_id))
        return list(result.scalars().all())
