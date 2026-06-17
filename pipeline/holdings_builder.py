"""
Holdings Builder Pipeline Module

This module is responsible for the synthetic generation and enrichment of 
mutual fund portfolio holdings based on asset allocation categories.
It contains predefined stock and debt pools to realistically simulate
a mutual fund's underlying asset allocation for the purpose of the dashboard.
"""

import random
from datetime import date
from typing import List, Dict, Any
from config.logging_config import get_logger

logger = get_logger("pipeline.holdings_builder")

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

class HoldingsBuilder:
    """
    Constructs and enriches portfolio holdings for mutual fund schemes.
    """
    
    @staticmethod
    def normalize_sector(sector: str) -> str:
        """
        Normalizes variations in sector names to standard taxonomy.
        """
        sector = sector.lower().strip()
        mapping = {
            "financial": "Financial Services",
            "banks": "Financial Services",
            "it": "Technology",
            "software": "Technology",
            "fmcg": "FMCG",
            "consumer goods": "FMCG",
            "auto": "Automobile",
            "pharma": "Healthcare",
            "health": "Healthcare"
        }
        for k, v in mapping.items():
            if k in sector:
                return v
        return sector.title()

    @staticmethod
    def generate_holdings_for_scheme(scheme_code: int, category: str, aum: float, as_of: date) -> List[Dict[str, Any]]:
        """
        Generates realistic portfolio holdings for schemes based on their category.
        """
        cat = category.lower()
        holdings = []
        
        if "liquid" in cat or "debt" in cat:
            selections = random.sample(DEBT_POOL, 3)
            weights = [50.0, 30.0, 17.5]
            for i, sec in enumerate(selections):
                h = sec.copy()
                h["allocation_percentage"] = weights[i]
                h["as_of_date"] = as_of
                h["market_value"] = aum * 10000000 * (weights[i] / 100.0) if aum else None
                h["sector"] = HoldingsBuilder.normalize_sector(h["sector"])
                holdings.append(h)
        elif "hybrid" in cat or "balanced" in cat:
            eq_sel = random.sample(STOCK_POOL, 4)
            db_sel = random.sample(DEBT_POOL, 2)
            eq_w = [25.0, 20.0, 10.0, 10.0]
            db_w = [15.0, 10.0]
            for i, sec in enumerate(eq_sel):
                h = sec.copy()
                h["allocation_percentage"] = eq_w[i]
                h["as_of_date"] = as_of
                h["market_value"] = aum * 10000000 * (eq_w[i] / 100.0) if aum else None
                h["sector"] = HoldingsBuilder.normalize_sector(h["sector"])
                holdings.append(h)
            for i, sec in enumerate(db_sel):
                h = sec.copy()
                h["allocation_percentage"] = db_w[i]
                h["as_of_date"] = as_of
                h["market_value"] = aum * 10000000 * (db_w[i] / 100.0) if aum else None
                h["sector"] = HoldingsBuilder.normalize_sector(h["sector"])
                holdings.append(h)
        else:
            eq_sel = random.sample(STOCK_POOL, 6)
            eq_w = [25.0, 20.0, 15.0, 15.0, 11.2, 10.0]
            for i, sec in enumerate(eq_sel):
                h = sec.copy()
                h["allocation_percentage"] = eq_w[i]
                h["as_of_date"] = as_of
                h["market_value"] = aum * 10000000 * (eq_w[i] / 100.0) if aum else None
                h["sector"] = HoldingsBuilder.normalize_sector(h["sector"])
                holdings.append(h)
                
        return holdings
