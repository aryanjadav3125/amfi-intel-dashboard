import pytest
import math
import numpy as np
import pandas as pd
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

from database.models import Scheme, NavDaily, BenchmarkDaily
from pipeline.risk_engine import RiskEngine

@pytest.mark.asyncio
async def test_risk_engine_calculations():
    # 1. Prepare sample scheme
    scheme = Scheme(
        scheme_id=101,
        scheme_code=101,
        scheme_name="Test Direct Fund",
        benchmark_name="Nifty 50 TRI",
        regular_scheme_code=201,
        direct_scheme_code=101
    )

    # 2. Prepare daily NAV records (10 records for pandas standard deviation calculations)
    # Direct NAV grows from 100 to 110, Regular NAV grows from 98 to 106.8
    # Benchmark daily prices grow from 1000 to 1080
    dates = [date(2026, 5, 1) + pd.Timedelta(days=i) for i in range(10)]
    
    nav_values = [100.0, 101.1, 102.3, 103.0, 104.2, 105.5, 106.3, 107.8, 108.9, 110.0]
    regular_nav_values = [98.0, 98.9, 100.0, 100.5, 101.5, 102.6, 103.2, 104.5, 105.6, 106.8]
    benchmark_values = [1000.0, 1008.0, 1017.0, 1023.0, 1031.0, 1042.0, 1049.0, 1059.0, 1068.0, 1080.0]
    
    nav_records = []
    benchmark_records = []
    
    for i, dt in enumerate(dates):
        nav_records.append(
            NavDaily(
                scheme_id=101,
                nav_date=dt,
                nav_value=nav_values[i],
                regular_nav_value=regular_nav_values[i]
            )
        )
        benchmark_records.append(
            BenchmarkDaily(
                name="Nifty 50 TRI",
                price_date=dt,
                price_value=benchmark_values[i]
            )
        )

    # 3. Create mock session and session execution returns
    mock_session = AsyncMock()
    
    # Mock return values for session.execute() queries:
    # First execution: select(Scheme)
    mock_scheme_result = MagicMock()
    mock_scheme_result.scalars.return_value.all.return_value = [scheme]
    
    # Second execution: select(BenchmarkDaily) (check if empty, returns benchmark_records so no fetch)
    mock_bench_result = MagicMock()
    mock_bench_result.scalars.return_value.all.return_value = benchmark_records
    
    # Third execution: select(NavDaily)
    mock_nav_result = MagicMock()
    mock_nav_result.scalars.return_value.all.return_value = nav_records
    
    # Configure execute side effects
    mock_session.execute.side_effect = [
        mock_scheme_result,  # select Schemes
        mock_bench_result,   # select BenchmarkDaily check
        mock_bench_result,   # select BenchmarkDaily load
        mock_nav_result,     # select NavDaily
        AsyncMock()          # update(Scheme)
    ]

    # 4. Patch get_db_session context manager
    with patch("pipeline.risk_engine.get_db_session") as mock_get_db_session:
        mock_get_db_session.return_value.__aenter__.return_value = mock_session
        mock_get_db_session.return_value.__exit__.return_value = None
        
        # 5. Run Risk Engine calculation
        engine = RiskEngine()
        updated_count = await engine.update_all_scheme_analytics()
        
        # Assertions
        assert updated_count == 1
        
        # Verify the database execute update was called
        assert mock_session.execute.call_count >= 5
        
        # Get the update query values
        update_call = mock_session.execute.call_args_list[-1]
        query = update_call[0][0]
        
        # Verify we updated with computed properties
        # (e.g. check the values dictionary passed to the sqlalchemy update)
        assert query.is_update
        params = query.compile().params
        
        assert "direct_nav" in params
        assert "regular_nav" in params
        assert "direct_cagr_5y" in params
        assert "regular_cagr_5y" in params
        assert "benchmark_cagr_5y" in params
        assert "direct_info_ratio" in params
        assert "regular_info_ratio" in params
        
        # Test math calculation logic sanity checks
        # NAV direct at end should be 110.0
        assert params["direct_nav"] == 110.0
        # NAV regular at end should be 106.8
        assert params["regular_nav"] == 106.8
        
        # Volatility / active tracking ratios should have populated valid floats
        assert isinstance(params["direct_cagr_5y"], float)
        assert isinstance(params["direct_info_ratio"], float)
