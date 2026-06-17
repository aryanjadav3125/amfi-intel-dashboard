"""
Database Seeding Script

This script initializes the local SQLite or PostgreSQL database with baseline 
Fund Houses (AMCs) and parses fallback NAV data to dynamically generate a robust 
set of mutual fund schemes, categories, and historical mock allocations.
It is primarily used during fresh deployments to populate the dashboard.
"""

import asyncio
from datetime import date, datetime
from database.engine import get_db_session, init_models
import random
from database.repositories import FundHouseRepository, SchemeRepository, AssetAllocationRepository, HoldingRepository
from config.logging_config import get_logger

logger = get_logger("database.seed")

async def seed_data():
    logger.info("Starting database seeding process...")
    
    # Initialize all models first
    await init_models()
    
    async with get_db_session() as session:
        amc_repo = FundHouseRepository(session)
        scheme_repo = SchemeRepository(session)
        alloc_repo = AssetAllocationRepository(session)
        holding_repo = HoldingRepository(session)
        
        # 1. Seed standard Asset Management Companies (Fund Houses)
        amcs = [
            "HDFC Mutual Fund",
            "SBI Mutual Fund",
            "ICICI Prudential Mutual Fund",
            "Axis Mutual Fund",
            "Parag Parikh Mutual Fund",
            "Nippon India Mutual Fund",
            "Kotak Mahindra Mutual Fund",
            "UTI Mutual Fund"
        ]
        
        amc_objects = {}
        for name in amcs:
            amc = await amc_repo.get_or_create(name=name)
            amc_objects[name] = amc.fund_house_id
            
        logger.info(f"Seeded baseline Fund Houses.")
        
        # 2. Parse and seed high-fidelity mutual fund schemes dynamically from fallback dataset
        import os
        from scraper.nav_parser import NavParser
        
        fallback_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scraper", "AMFI_NAVAll_fallback.txt")
        with open(fallback_path, "r", encoding="iso-8859-1") as f:
            raw_text = f.read()
            
        parser = NavParser()
        parsed_schemes, parsed_navs = parser.parse_raw_text(raw_text)
        
        schemes_to_seed = []
        for s in parsed_schemes:
            # Ensure AMC is created/matched
            amc_name = s.fund_house_name
            if amc_name not in amc_objects:
                amc = await amc_repo.get_or_create(name=amc_name)
                amc_objects[amc_name] = amc.fund_house_id
            
            schemes_to_seed.append({
                "scheme_id": s.scheme_code,
                "fund_house_id": amc_objects[amc_name],
                "scheme_name": s.scheme_name,
                "isin_div_payout": s.isin_div_payout,
                "isin_div_reinvest": s.isin_div_reinvest,
                "isin_growth": s.isin_div_payout or s.isin_div_reinvest,
                "category": s.category,
                "scheme_type": s.scheme_type,
                "asset_class": s.asset_class,
                "benchmark_name": s.benchmark_name,
                "scheme_riskometer": s.scheme_riskometer,
                "benchmark_riskometer": s.benchmark_riskometer,
                "regular_nav": s.regular_nav,
                "direct_nav": s.direct_nav,
                "regular_cagr_5y": s.regular_cagr_5y,
                "direct_cagr_5y": s.direct_cagr_5y,
                "benchmark_cagr_5y": s.benchmark_cagr_5y,
                "regular_info_ratio": s.regular_info_ratio,
                "direct_info_ratio": s.direct_info_ratio,
                "daily_aum": s.daily_aum
            })
            
        seeded_count = await scheme_repo.upsert_batch(schemes_to_seed)
        logger.info(f"Dynamically seeded {seeded_count} high-fidelity mutual fund Schemes successfully.")
        
        # 3. Dynamic Asset Allocations Seeding based on categories
        as_of = date(2026, 5, 20)
        for s in parsed_schemes:
            cat = s.category.lower()
            if "liquid" in cat or "debt" in cat:
                allocs = [
                    {"asset_class": "Equity", "percentage": 0.0, "as_of_date": as_of},
                    {"asset_class": "Debt", "percentage": 97.5, "as_of_date": as_of},
                    {"asset_class": "Cash", "percentage": 2.5, "as_of_date": as_of}
                ]
            elif "hybrid" in cat or "balanced" in cat:
                allocs = [
                    {"asset_class": "Equity", "percentage": 65.0, "as_of_date": as_of},
                    {"asset_class": "Debt", "percentage": 25.0, "as_of_date": as_of},
                    {"asset_class": "Cash", "percentage": 10.0, "as_of_date": as_of}
                ]
            else:
                allocs = [
                    {"asset_class": "Equity", "percentage": 96.2, "as_of_date": as_of},
                    {"asset_class": "Debt", "percentage": 0.0, "as_of_date": as_of},
                    {"asset_class": "Cash", "percentage": 3.8, "as_of_date": as_of}
                ]
            await alloc_repo.update_allocations(s.scheme_code, allocs)
            
        logger.info("Enriched allocations seeded successfully.")
        
        # 3.5 Dynamic Holdings Seeding
        STOCK_POOL = [
            {"company_name": "HDFC Bank Ltd.", "sector": "Financial Services", "isin": "INE040A01034"},
            {"company_name": "Reliance Industries Ltd.", "sector": "Energy", "isin": "INE002A01018"},
            {"company_name": "ICICI Bank Ltd.", "sector": "Financial Services", "isin": "INE090A01021"},
            {"company_name": "Infosys Ltd.", "sector": "Technology", "isin": "INE009A01021"},
            {"company_name": "ITC Ltd.", "sector": "FMCG", "isin": "INE154A01025"},
            {"company_name": "TCS Ltd.", "sector": "Technology", "isin": "INE467B01029"},
            {"company_name": "Larsen & Toubro Ltd.", "sector": "Construction", "isin": "INE018A01030"},
            {"company_name": "Axis Bank Ltd.", "sector": "Financial Services", "isin": "INE238A01034"},
            {"company_name": "State Bank of India", "sector": "Financial Services", "isin": "INE062A01020"},
            {"company_name": "Bharti Airtel Ltd.", "sector": "Telecommunication", "isin": "INE397D01024"}
        ]
        DEBT_POOL = [
            {"company_name": "GOI Sec 7.26% 2033", "sector": "Sovereign", "isin": "IN0020220152"},
            {"company_name": "GOI Sec 7.38% 2027", "sector": "Sovereign", "isin": "IN0020220061"},
            {"company_name": "HDFC Bank Ltd. CP", "sector": "Financial Services", "isin": "INE040A14123"},
            {"company_name": "NABARD Bonds", "sector": "Financial Services", "isin": "INE261F08000"}
        ]
        
        for s in parsed_schemes:
            cat = s.category.lower()
            holdings = []
            if "liquid" in cat or "debt" in cat:
                # Mostly debt
                selections = random.sample(DEBT_POOL, 3)
                weights = [50.0, 30.0, 17.5]
                for i, sec in enumerate(selections):
                    h = sec.copy()
                    h["allocation_percentage"] = weights[i]
                    h["as_of_date"] = as_of
                    h["market_value"] = s.daily_aum * 10000000 * (weights[i] / 100.0) if s.daily_aum else None
                    holdings.append(h)
            elif "hybrid" in cat or "balanced" in cat:
                # Mix
                eq_sel = random.sample(STOCK_POOL, 4)
                db_sel = random.sample(DEBT_POOL, 2)
                eq_w = [25.0, 20.0, 10.0, 10.0]
                db_w = [15.0, 10.0]
                for i, sec in enumerate(eq_sel):
                    h = sec.copy()
                    h["allocation_percentage"] = eq_w[i]
                    h["as_of_date"] = as_of
                    h["market_value"] = s.daily_aum * 10000000 * (eq_w[i] / 100.0) if s.daily_aum else None
                    holdings.append(h)
                for i, sec in enumerate(db_sel):
                    h = sec.copy()
                    h["allocation_percentage"] = db_w[i]
                    h["as_of_date"] = as_of
                    h["market_value"] = s.daily_aum * 10000000 * (db_w[i] / 100.0) if s.daily_aum else None
                    holdings.append(h)
            else:
                # Equity
                eq_sel = random.sample(STOCK_POOL, 6)
                eq_w = [25.0, 20.0, 15.0, 15.0, 11.2, 10.0]
                for i, sec in enumerate(eq_sel):
                    h = sec.copy()
                    h["allocation_percentage"] = eq_w[i]
                    h["as_of_date"] = as_of
                    h["market_value"] = s.daily_aum * 10000000 * (eq_w[i] / 100.0) if s.daily_aum else None
                    holdings.append(h)
                    
            await holding_repo.update_holdings(s.scheme_code, holdings)
            
        logger.info("Stock holdings and sector allocations seeded successfully.")
        
        # 4. Seed Fund House AUM / AAUM disclosures
        from database.models import FundHouseAum, CategoryAum
        from sqlalchemy import select
        
        period = "Q4 2025-26"
        aum_seeds = [
            {
                "fund_house_id": amc_objects["HDFC Mutual Fund"],
                "average_aum": 650000.0,
                "aaum": 655000.0,
                "direct_aum": 240000.0,
                "regular_aum": 410000.0,
                "t15_aum": 480000.0,
                "b15_aum": 170000.0,
                "folio_count": 9500000
            },
            {
                "fund_house_id": amc_objects["SBI Mutual Fund"],
                "average_aum": 910000.0,
                "aaum": 915000.0,
                "direct_aum": 350000.0,
                "regular_aum": 560000.0,
                "t15_aum": 630000.0,
                "b15_aum": 280000.0,
                "folio_count": 15000000
            },
            {
                "fund_house_id": amc_objects["ICICI Prudential Mutual Fund"],
                "average_aum": 680000.0,
                "aaum": 683000.0,
                "direct_aum": 270000.0,
                "regular_aum": 410000.0,
                "t15_aum": 490000.0,
                "b15_aum": 190000.0,
                "folio_count": 10000000
            },
            {
                "fund_house_id": amc_objects["Axis Mutual Fund"],
                "average_aum": 260000.0,
                "aaum": 262000.0,
                "direct_aum": 110000.0,
                "regular_aum": 150000.0,
                "t15_aum": 200000.0,
                "b15_aum": 60000.0,
                "folio_count": 6000000
            },
            {
                "fund_house_id": amc_objects["Parag Parikh Mutual Fund"],
                "average_aum": 62000.0,
                "aaum": 63000.0,
                "direct_aum": 48000.0,
                "regular_aum": 14000.0,
                "t15_aum": 52000.0,
                "b15_aum": 10000.0,
                "folio_count": 3500000
            },
            {
                "fund_house_id": amc_objects["Nippon India Mutual Fund"],
                "average_aum": 430000.0,
                "aaum": 432000.0,
                "direct_aum": 180000.0,
                "regular_aum": 250000.0,
                "t15_aum": 320000.0,
                "b15_aum": 110000.0,
                "folio_count": 8000000
            }
        ]
        
        for s in aum_seeds:
            # Check if exists
            res = await session.execute(
                select(FundHouseAum).where(
                    (FundHouseAum.fund_house_id == s["fund_house_id"]) & 
                    (FundHouseAum.period == period)
                )
            )
            exists = res.scalar_one_or_none()
            if not exists:
                aum_entry = FundHouseAum(
                    fund_house_id=s["fund_house_id"],
                    period=period,
                    average_aum=s["average_aum"],
                    aaum=s["aaum"],
                    direct_aum=s["direct_aum"],
                    regular_aum=s["regular_aum"],
                    t15_aum=s["t15_aum"],
                    b15_aum=s["b15_aum"],
                    folio_count=s["folio_count"]
                )
                session.add(aum_entry)
        
        # 5. Seed Category AUMs
        cat_period = "April 2026"
        cat_aum_seeds = [
            {"category": "Equity Scheme - Large Cap Fund", "aum_value": 285000.0, "folio_count": 12000000, "percentage_of_total": 25.0},
            {"category": "Equity Scheme - Flexi Cap Fund", "aum_value": 180000.0, "folio_count": 8000000, "percentage_of_total": 15.8},
            {"category": "Equity Scheme - Small Cap Fund", "aum_value": 245000.0, "folio_count": 14000000, "percentage_of_total": 21.5},
            {"category": "Equity Scheme - Sectoral/ Thematic", "aum_value": 150000.0, "folio_count": 6500000, "percentage_of_total": 13.2},
            {"category": "Debt Scheme - Liquid Fund", "aum_value": 140000.0, "folio_count": 1500000, "percentage_of_total": 12.3},
            {"category": "Hybrid Scheme - Balanced Advantage", "aum_value": 70000.0, "folio_count": 3000000, "percentage_of_total": 6.1},
            {"category": "Other Schemes - Index Funds", "aum_value": 69000.0, "folio_count": 3200000, "percentage_of_total": 6.1}
        ]
        
        for c in cat_aum_seeds:
            res = await session.execute(
                select(CategoryAum).where(
                    (CategoryAum.category == c["category"]) & 
                    (CategoryAum.period == cat_period)
                )
            )
            exists = res.scalar_one_or_none()
            if not exists:
                cat_entry = CategoryAum(
                    category=c["category"],
                    period=cat_period,
                    aum_value=c["aum_value"],
                    folio_count=c["folio_count"],
                    percentage_of_total=c["percentage_of_total"]
                )
                session.add(cat_entry)
                
        logger.info("AUM and Category AUM data seeded successfully.")
        
    logger.info("Database seeding successfully completed!")

if __name__ == "__main__":
    asyncio.run(seed_data())
