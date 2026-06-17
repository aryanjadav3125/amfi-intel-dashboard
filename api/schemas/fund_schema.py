from datetime import date
from typing import List, Optional
from pydantic import BaseModel

class FundSummaryResponse(BaseModel):
    scheme_id: int
    scheme_name: str
    category: str
    scheme_type: str
    latest_nav: float
    latest_date: Optional[date]
    cagr_1y: Optional[float]
    
    # Enriched side-by-side performance metrics
    asset_class: Optional[str] = None
    benchmark_name: Optional[str] = None
    scheme_riskometer: Optional[str] = None
    benchmark_riskometer: Optional[str] = None
    regular_nav: Optional[float] = None
    direct_nav: Optional[float] = None
    regular_cagr_5y: Optional[float] = None
    direct_cagr_5y: Optional[float] = None
    benchmark_cagr_5y: Optional[float] = None
    regular_info_ratio: Optional[float] = None
    direct_info_ratio: Optional[float] = None
    daily_aum: Optional[float] = None

class FundListEnvelope(BaseModel):
    funds: List[FundSummaryResponse]
    total: int

class AssetAllocationResponse(BaseModel):
    asset_class: str
    percentage: float

class SchemeMetricsResponse(BaseModel):
    cagr_1y: Optional[float]
    cagr_3y: Optional[float]
    volatility: Optional[float]
    sharpe_ratio: Optional[float]
    sortino_ratio: Optional[float]
    max_drawdown: Optional[float]

class FundDetailResponse(BaseModel):
    scheme_id: int
    scheme_name: str
    category: str
    scheme_type: str
    isin_growth: Optional[str]
    isin_div_payout: Optional[str]
    latest_nav: float
    latest_date: Optional[date]
    allocations: List[AssetAllocationResponse]
    metrics: SchemeMetricsResponse
    
    # Enriched side-by-side performance metrics
    asset_class: Optional[str] = None
    benchmark_name: Optional[str] = None
    scheme_riskometer: Optional[str] = None
    benchmark_riskometer: Optional[str] = None
    regular_nav: Optional[float] = None
    direct_nav: Optional[float] = None
    regular_cagr_5y: Optional[float] = None
    direct_cagr_5y: Optional[float] = None
    benchmark_cagr_5y: Optional[float] = None
    regular_info_ratio: Optional[float] = None
    direct_info_ratio: Optional[float] = None
    daily_aum: Optional[float] = None

class AmcResponse(BaseModel):
    fund_house_id: int
    name: str
    code: Optional[str]

