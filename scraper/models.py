from datetime import date
from typing import Optional
from pydantic import BaseModel, Field

class FundHouseRecord(BaseModel):
    name: str = Field(..., description="Name of the Fund House (AMC)")

class SchemeRecord(BaseModel):
    scheme_code: int = Field(..., description="Unique scheme code assigned by AMFI")
    scheme_name: str = Field(..., description="Full mutual fund scheme name")
    isin_div_payout: Optional[str] = Field(None, description="ISIN for IDCW payout or growth")
    isin_div_reinvest: Optional[str] = Field(None, description="ISIN for IDCW reinvestment")
    category: str = Field(..., description="Scheme category (e.g., Equity - Large Cap)")
    scheme_type: str = Field(..., description="Scheme type (e.g., Open Ended)")
    fund_house_name: str = Field(..., description="Name of the managing AMC")
    
    # Mapping distinct plan codes for real historical tracking
    regular_scheme_code: Optional[int] = Field(None, description="Mapped regular scheme code")
    direct_scheme_code: Optional[int] = Field(None, description="Mapped direct scheme code")
    
    # Extra performance metrics
    asset_class: Optional[str] = Field(None, description="Asset class (Equity, Debt, etc.)")
    benchmark_name: Optional[str] = Field(None, description="Designated benchmark index")
    scheme_riskometer: Optional[str] = Field(None, description="Scheme riskometer rating")
    benchmark_riskometer: Optional[str] = Field(None, description="Benchmark riskometer rating")
    regular_nav: Optional[float] = Field(None, description="Regular plan NAV")
    direct_nav: Optional[float] = Field(None, description="Direct plan NAV")
    regular_cagr_5y: Optional[float] = Field(None, description="Regular 5-Year CAGR return")
    direct_cagr_5y: Optional[float] = Field(None, description="Direct 5-Year CAGR return")
    benchmark_cagr_5y: Optional[float] = Field(None, description="Benchmark 5-Year CAGR return")
    regular_info_ratio: Optional[float] = Field(None, description="Regular 5-Year Information Ratio")
    direct_info_ratio: Optional[float] = Field(None, description="Direct 5-Year Information Ratio")
    daily_aum: Optional[float] = Field(None, description="Daily AUM in INR Crores")

class NavRecord(BaseModel):
    scheme_code: int = Field(..., description="AMFI scheme code")
    nav_date: date = Field(..., description="Applicable NAV date")
    nav_value: Optional[float] = Field(None, description="Direct NAV value")
    regular_nav_value: Optional[float] = Field(None, description="Regular NAV value")
