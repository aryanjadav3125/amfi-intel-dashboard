from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Scheme
from config.logging_config import get_logger

logger = get_logger("database.scheme_repo")

class SchemeRepository:
    """
    Repository class for managing operations on the Scheme model.
    """
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, scheme_id: int) -> Optional[Scheme]:
        result = await self.session.execute(
            select(Scheme).where(Scheme.scheme_id == scheme_id)
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, scheme_code: int) -> Optional[Scheme]:
        result = await self.session.execute(
            select(Scheme).where(Scheme.scheme_code == scheme_code)
        )
        return result.scalar_one_or_none()

    async def get_all(self, limit: int = 100, offset: int = 0) -> List[Scheme]:
        result = await self.session.execute(
            select(Scheme).order_by(Scheme.scheme_name).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def get_count(self) -> int:
        from sqlalchemy import func
        result = await self.session.execute(select(func.count(Scheme.scheme_id)))
        return result.scalar() or 0

    async def get_all_categories(self) -> List[str]:
        result = await self.session.execute(
            select(Scheme.category).distinct().order_by(Scheme.category)
        )
        return list(result.scalars().all())

    async def search_schemes(self, query: str, limit: int = 20) -> List[Scheme]:
        """
        Performs full-text search-like match on scheme names.
        """
        result = await self.session.execute(
            select(Scheme)
            .where(Scheme.scheme_name.ilike(f"%{query}%"))
            .order_by(Scheme.scheme_name)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def upsert_batch(self, schemes_data: List[Dict[str, Any]]) -> int:
        """
        Idempotent bulk upsert of Schemes.
        Fetches existing Scheme IDs, segments into inserts and updates,
        and executes bulk operations efficiently.
        """
        if not schemes_data:
            return 0

        # Extract all scheme_ids to be processed
        incoming_ids = [s["scheme_id"] for s in schemes_data]

        # Query existing IDs
        result = await self.session.execute(
            select(Scheme.scheme_id).where(Scheme.scheme_id.in_(incoming_ids))
        )
        existing_ids = set(result.scalars().all())

        new_records = []
        update_records = []

        now = datetime.utcnow()

        for s in schemes_data:
            if s["scheme_id"] not in existing_ids:
                new_records.append(
                    Scheme(
                        scheme_id=s["scheme_id"],
                        fund_house_id=s["fund_house_id"],
                        scheme_code=s["scheme_id"], # scheme_code matches scheme_id
                        scheme_name=s["scheme_name"],
                        isin_div_payout=s.get("isin_div_payout"),
                        isin_div_reinvest=s.get("isin_div_reinvest"),
                        isin_growth=s.get("isin_growth"),
                        category=s["category"],
                        sub_category=s.get("sub_category"),
                        scheme_type=s["scheme_type"],
                        regular_scheme_code=s.get("regular_scheme_code"),
                        direct_scheme_code=s.get("direct_scheme_code"),
                        asset_class=s.get("asset_class"),
                        benchmark_name=s.get("benchmark_name"),
                        scheme_riskometer=s.get("scheme_riskometer"),
                        benchmark_riskometer=s.get("benchmark_riskometer"),
                        regular_nav=s.get("regular_nav"),
                        direct_nav=s.get("direct_nav"),
                        regular_cagr_5y=s.get("regular_cagr_5y"),
                        direct_cagr_5y=s.get("direct_cagr_5y"),
                        benchmark_cagr_5y=s.get("benchmark_cagr_5y"),
                        regular_info_ratio=s.get("regular_info_ratio"),
                        direct_info_ratio=s.get("direct_info_ratio"),
                        daily_aum=s.get("daily_aum"),
                        created_at=now,
                        updated_at=now
                    )
                )
            else:
                update_records.append(s)

        # Execute inserts
        if new_records:
            self.session.add_all(new_records)
            await self.session.flush()
            logger.debug(f"Inserted {len(new_records)} new Scheme entries.")

        # Execute updates in bulk (or loop if small)
        for u in update_records:
            await self.session.execute(
                update(Scheme)
                .where(Scheme.scheme_id == u["scheme_id"])
                .values(
                    scheme_name=u["scheme_name"],
                    isin_div_payout=u.get("isin_div_payout"),
                    isin_div_reinvest=u.get("isin_div_reinvest"),
                    category=u["category"],
                    scheme_type=u["scheme_type"],
                    regular_scheme_code=u.get("regular_scheme_code"),
                    direct_scheme_code=u.get("direct_scheme_code"),
                    asset_class=u.get("asset_class"),
                    benchmark_name=u.get("benchmark_name"),
                    scheme_riskometer=u.get("scheme_riskometer"),
                    benchmark_riskometer=u.get("benchmark_riskometer"),
                    regular_nav=u.get("regular_nav"),
                    direct_nav=u.get("direct_nav"),
                    regular_cagr_5y=u.get("regular_cagr_5y"),
                    direct_cagr_5y=u.get("direct_cagr_5y"),
                    benchmark_cagr_5y=u.get("benchmark_cagr_5y"),
                    regular_info_ratio=u.get("regular_info_ratio"),
                    direct_info_ratio=u.get("direct_info_ratio"),
                    daily_aum=u.get("daily_aum"),
                    updated_at=now
                )
            )

        if update_records:
            logger.debug(f"Updated {len(update_records)} existing Scheme entries.")

        return len(new_records) + len(update_records)
