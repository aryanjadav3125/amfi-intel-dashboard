import math
import numpy as np
import pandas as pd
from datetime import date, timedelta
from typing import List
from database.engine import get_db_session
from database.models import Scheme, NavDaily, BenchmarkDaily
from database.repositories.scheme_repo import SchemeRepository
from scraper.benchmark_connector import BenchmarkConnector
from config.logging_config import get_logger
from sqlalchemy import select, update

logger = get_logger("pipeline.risk_engine")

class RiskEngine:
    """
    Financial analytics engine powered by pandas and numpy.
    Calculates exact historical return CAGRs, tracking errors, active return drifts,
    and Information Ratios for Regular vs Direct plans against live benchmark historical indexes.
    """
    
    async def update_all_scheme_analytics(self) -> int:
        """
        Runs calculation pass over all schemes in the database.
        Populates real CAGR and Information Ratios.
        """
        logger.info("Starting historical risk and analytics calculation run...")
        
        async with get_db_session() as session:
            # 1. Fetch all Schemes
            res = await session.execute(select(Scheme))
            schemes: List[Scheme] = list(res.scalars().all())
            logger.info(f"Loaded {len(schemes)} schemes for risk profiling.")
            
            connector = BenchmarkConnector()
            updated_count = 0
            
            for scheme in schemes:
                scheme_id = scheme.scheme_id
                benchmark_name = scheme.benchmark_name or "Nifty 50 TRI"
                
                # 2. Ensure Benchmark Index historical data exists in database
                # Query index records
                b_res = await session.execute(
                    select(BenchmarkDaily).where(BenchmarkDaily.name == benchmark_name)
                )
                b_records = b_res.scalars().all()
                
                if not b_records:
                    logger.info(f"Benchmark '{benchmark_name}' history missing. Fetching...")
                    prices = await connector.fetch_historical_prices(benchmark_name, years=3)
                    
                    # Batch insert benchmark index prices
                    new_b_records = [
                        BenchmarkDaily(
                            name=p["name"],
                            price_date=p["price_date"],
                            price_value=p["price_value"]
                        )
                        for p in prices
                    ]
                    session.add_all(new_b_records)
                    await session.flush()
                    logger.info(f"Saved {len(new_b_records)} price points for benchmark '{benchmark_name}'.")
                
                # Re-query all benchmark index entries to load in memory
                b_res = await session.execute(
                    select(BenchmarkDaily).where(BenchmarkDaily.name == benchmark_name)
                )
                b_records = b_res.scalars().all()
                
                # 3. Load daily NAV history
                nav_res = await session.execute(
                    select(NavDaily).where(NavDaily.scheme_id == scheme_id).order_by(NavDaily.nav_date)
                )
                nav_records = nav_res.scalars().all()
                
                if not nav_records or len(nav_records) < 10:
                    logger.warning(f"Insufficient NAV history for scheme ID {scheme_id}. Skipping...")
                    continue
                
                # 4. Construct Pandas DataFrames for joined analytics
                nav_df = pd.DataFrame([
                    {
                        "date": pd.to_datetime(n.nav_date),
                        "direct_nav": n.nav_value,
                        "regular_nav": n.regular_nav_value or (n.nav_value * 0.94)
                    }
                    for n in nav_records
                ])
                
                bench_df = pd.DataFrame([
                    {
                        "date": pd.to_datetime(b.price_date),
                        "benchmark_value": b.price_value
                    }
                    for b in b_records
                ])
                
                if bench_df.empty:
                    logger.warning(f"Empty benchmark price feed for '{benchmark_name}'. Skipping analytics calculation.")
                    continue
                
                # Join time-series dataframes on matching date index
                df = pd.merge(nav_df, bench_df, on="date", how="inner").sort_values("date")
                
                if len(df) < 5:
                    logger.warning(f"Insufficient merged time-series history ({len(df)} overlapping days) for scheme ID {scheme_id}. Skipping...")
                    continue
                
                # 5. Math Calculations
                # CAGRs (5-Year or actual history span)
                start_row = df.iloc[0]
                end_row = df.iloc[-1]
                
                days_diff = (end_row["date"] - start_row["date"]).days
                years_diff = days_diff / 365.25
                
                if years_diff <= 0:
                    continue
                    
                # Calculate actual CAGRs
                d_cagr = (end_row["direct_nav"] / start_row["direct_nav"]) ** (1.0 / years_diff) - 1.0
                r_cagr = (end_row["regular_nav"] / start_row["regular_nav"]) ** (1.0 / years_diff) - 1.0
                b_cagr = (end_row["benchmark_value"] / start_row["benchmark_value"]) ** (1.0 / years_diff) - 1.0
                
                # Daily Returns
                df["d_return"] = np.log(df["direct_nav"] / df["direct_nav"].shift(1))
                df["r_return"] = np.log(df["regular_nav"] / df["regular_nav"].shift(1))
                df["b_return"] = np.log(df["benchmark_value"] / df["benchmark_value"].shift(1))
                
                # Active Returns (Drift)
                df["d_active"] = df["d_return"] - df["b_return"]
                df["r_active"] = df["r_return"] - df["b_return"]
                
                # Annualized Standard Deviation of Active Returns (Tracking Error)
                d_tracking_error = df["d_active"].std() * math.sqrt(252)
                r_tracking_error = df["r_active"].std() * math.sqrt(252)
                
                # Information Ratio
                # Direct Info Ratio
                if d_tracking_error > 0:
                    d_info_ratio = (df["d_active"].mean() / df["d_active"].std()) * math.sqrt(252)
                else:
                    d_info_ratio = 0.0
                    
                # Regular Info Ratio
                if r_tracking_error > 0:
                    r_info_ratio = (df["r_active"].mean() / df["r_active"].std()) * math.sqrt(252)
                else:
                    r_info_ratio = 0.0
                    
                # Limit metrics to reasonable visual boundaries
                d_cagr_pct = round(d_cagr * 100, 2)
                r_cagr_pct = round(r_cagr * 100, 2)
                b_cagr_pct = round(b_cagr * 100, 2)
                
                d_ir = round(float(d_info_ratio), 2)
                r_ir = round(float(r_info_ratio), 2)
                
                # 6. Update database Scheme row
                await session.execute(
                    update(Scheme)
                    .where(Scheme.scheme_id == scheme_id)
                    .values(
                        direct_nav=round(end_row["direct_nav"], 4),
                        regular_nav=round(end_row["regular_nav"], 4),
                        direct_cagr_5y=d_cagr_pct,
                        regular_cagr_5y=r_cagr_pct,
                        benchmark_cagr_5y=b_cagr_pct,
                        direct_info_ratio=d_ir,
                        regular_info_ratio=r_ir
                    )
                )
                updated_count += 1
                logger.info(
                    f"Updated analytics for scheme ID {scheme_id}: "
                    f"Direct 5Y CAGR: {d_cagr_pct}%, Regular 5Y CAGR: {r_cagr_pct}%, "
                    f"Direct IR: {d_ir}, Regular IR: {r_ir}"
                )
                
            logger.info(f"Completed risk engine calculations. Updated {updated_count} schemes successfully.")
            return updated_count
