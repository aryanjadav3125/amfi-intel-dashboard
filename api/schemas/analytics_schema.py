from datetime import date
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class CompareMatrixResponse(BaseModel):
    scheme_id: int
    scheme_name: str
    category: str
    latest_nav: float
    cagr_1y: Optional[float] = None
    cagr_3y: Optional[float] = None
    volatility: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None

class CompareResponseEnvelope(BaseModel):
    matrix: List[CompareMatrixResponse]
    chart: List[Dict[str, Any]]  # Dynamic keys for scheme growth values

class SipPoint(BaseModel):
    date: date
    invested: float
    value: float

class SipSimulationResponse(BaseModel):
    total_investment: float
    final_value: float
    profit: float
    absolute_returns: float
    annualized_returns: Optional[float]
    chart: List[SipPoint]
