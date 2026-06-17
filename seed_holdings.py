import asyncio
import datetime
import random
from sqlalchemy import select
from database.engine import AsyncSessionFactory, engine, Base
from database.models import Scheme, Holding

COMPANIES = ["HDFC Bank", "Infosys", "Reliance", "TCS", "ICICI Bank", "L&T", "ITC", "SBI", "Bharti Airtel", "Hindustan Unilever"]
SECTORS = ["Financial Services", "IT", "Energy", "IT", "Financial Services", "Construction", "FMCG", "Financial Services", "Telecommunication", "FMCG"]

async def seed_holdings():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionFactory() as session:
        result = await session.execute(select(Scheme.scheme_id))
        schemes = result.scalars().all()
        
        for scheme_id in schemes:
            # check if already exists
            res = await session.execute(select(Holding).where(Holding.scheme_id == scheme_id))
            if res.scalars().first():
                continue
                
            num_holdings = random.randint(3, 8)
            chosen_indices = random.sample(range(len(COMPANIES)), num_holdings)
            
            total_alloc = 0
            for idx in chosen_indices:
                alloc = round(random.uniform(2.0, 15.0), 2)
                total_alloc += alloc
                session.add(Holding(
                    scheme_id=scheme_id,
                    company_name=COMPANIES[idx],
                    sector=SECTORS[idx],
                    allocation_percentage=alloc,
                    as_of_date=datetime.date(2026, 6, 16)
                ))
        
        await session.commit()
        print("Seeded holdings!")

if __name__ == "__main__":
    asyncio.run(seed_holdings())
