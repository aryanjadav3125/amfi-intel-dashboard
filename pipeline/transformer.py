from typing import Dict, Any
from scraper.models import SchemeRecord, NavRecord

class PipelineTransformer:
    """
    Transforms parsed Pydantic objects into database-repository-friendly dictionaries.
    """
    @staticmethod
    def transform_scheme(record: SchemeRecord, fund_house_id: int) -> Dict[str, Any]:
        """
        Translates a parsed SchemeRecord into a database scheme dictionary.
        """
        return {
            "scheme_id": record.scheme_code,
            "fund_house_id": fund_house_id,
            "scheme_name": record.scheme_name,
            "isin_div_payout": record.isin_div_payout,
            "isin_div_reinvest": record.isin_div_reinvest,
            "isin_growth": record.isin_div_payout,  # Default growth ISIN to payout ISIN
            "category": record.category,
            "sub_category": None,
            "scheme_type": record.scheme_type,
            
            # Mapping distinct plan codes for real historical tracking
            "regular_scheme_code": record.regular_scheme_code,
            "direct_scheme_code": record.direct_scheme_code,
            
            # High-Fidelity Performance metrics mapping
            "asset_class": record.asset_class,
            "benchmark_name": record.benchmark_name,
            "scheme_riskometer": record.scheme_riskometer,
            "benchmark_riskometer": record.benchmark_riskometer,
            "regular_nav": record.regular_nav,
            "direct_nav": record.direct_nav,
            "regular_cagr_5y": record.regular_cagr_5y,
            "direct_cagr_5y": record.direct_cagr_5y,
            "benchmark_cagr_5y": record.benchmark_cagr_5y,
            "regular_info_ratio": record.regular_info_ratio,
            "direct_info_ratio": record.direct_info_ratio,
            "daily_aum": record.daily_aum
        }

    @staticmethod
    def transform_nav(record: NavRecord) -> Dict[str, Any]:
        """
        Translates a parsed NavRecord into a database NAV dictionary.
        """
        return {
            "scheme_code": record.scheme_code,
            "nav_date": record.nav_date,
            "nav_value": record.nav_value,
            "regular_nav_value": record.regular_nav_value
        }
