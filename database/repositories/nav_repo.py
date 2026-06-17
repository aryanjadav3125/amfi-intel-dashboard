from datetime import date
from typing import List, Optional, Tuple, Set
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import NavDaily
from config.logging_config import get_logger

logger = get_logger("database.nav_repo")

class NavDailyRepository:
    """
    Repository class for managing operations on the NavDaily model.
    """
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_scheme_id(self, scheme_id: int, limit: int = 1000) -> List[NavDaily]:
        result = await self.session.execute(
            select(NavDaily)
            .where(NavDaily.scheme_id == scheme_id)
            .order_by(NavDaily.nav_date.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_nav_by_scheme_and_range(
        self, scheme_id: int, start_date: date, end_date: date
    ) -> List[NavDaily]:
        result = await self.session.execute(
            select(NavDaily)
            .where(
                and_(
                    NavDaily.scheme_id == scheme_id,
                    NavDaily.nav_date >= start_date,
                    NavDaily.nav_date <= end_date
                )
            )
            .order_by(NavDaily.nav_date.asc())
        )
        return list(result.scalars().all())

    async def get_latest_nav_date(self) -> Optional[date]:
        """
        Returns the absolute latest date recorded in the nav_daily table.
        """
        from sqlalchemy import func
        result = await self.session.execute(select(func.max(NavDaily.nav_date)))
        return result.scalar()

    async def upsert_nav_batch(self, nav_records: List[dict]) -> Tuple[int, int]:
        """
        Database-agnostic batch upsert of NAV records.
        Identifies and skips existing (scheme_id, nav_date) duplicates,
        inserting new records in bulk.
        Returns: (inserted_count, skipped_count)
        """
        if not nav_records:
            return 0, 0

        # Segment dates to query database for duplicates efficiently
        dates = {r["nav_date"] for r in nav_records}
        
        # To avoid massive in-clause, query distinct scheme-date combinations for the date range
        min_date = min(dates)
        max_date = max(dates)
        
        # Fetch existing combinations in range
        result = await self.session.execute(
            select(NavDaily.scheme_id, NavDaily.nav_date)
            .where(
                and_(
                    NavDaily.nav_date >= min_date,
                    NavDaily.nav_date <= max_date
                )
            )
        )
        existing_pairs: Set[Tuple[int, date]] = {(row[0], row[1]) for row in result.all()}

        new_navs = []
        skipped_count = 0

        for r in nav_records:
            pair = (r["scheme_code"], r["nav_date"])
            if pair not in existing_pairs:
                new_navs.append(
                    NavDaily(
                        scheme_id=r["scheme_code"],
                        nav_date=r["nav_date"],
                        nav_value=r["nav_value"],
                        regular_nav_value=r.get("regular_nav_value")
                    )
                )
            else:
                skipped_count += 1

        if new_navs:
            # Chunk session additions to avoid memory footprint spikes
            chunk_size = 1000
            for i in range(0, len(new_navs), chunk_size):
                chunk = new_navs[i:i + chunk_size]
                self.session.add_all(chunk)
            await self.session.flush()
            logger.debug(f"Inserted {len(new_navs)} daily NAV rows in this chunk.")

        return len(new_navs), skipped_count
