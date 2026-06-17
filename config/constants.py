# Database Table Names
TABLE_FUND_HOUSES = "fund_houses"
TABLE_SCHEMES = "schemes"
TABLE_NAV_DAILY = "nav_daily"
TABLE_ASSET_ALLOCATION = "asset_allocation"
TABLE_PIPELINE_RUNS = "pipeline_runs"
TABLE_FUND_HOUSE_AUM = "fund_house_aum"
TABLE_CATEGORY_AUM = "category_aum"

# File Constants
AMFI_DELIMITER = ";"
AMFI_ENCODING = "iso-8859-1"
DATE_FORMAT = "%d-%b-%Y"  # e.g., 20-May-2026

# NAV Status Edge Cases
NAV_NOT_AVAILABLE = "N.A."

# Risk Levels & Tags
RISK_LOW = "Low"
RISK_MODERATE = "Moderate"
RISK_HIGH = "High"

# standard categories list for normalisation checks
SCHEME_CATEGORIES = [
    "Equity Scheme - Large Cap Fund",
    "Equity Scheme - Mid Cap Fund",
    "Equity Scheme - Small Cap Fund",
    "Equity Scheme - Multi Cap Fund",
    "Equity Scheme - Flexi Cap Fund",
    "Equity Scheme - Sectoral/ Thematic",
    "Debt Scheme - Liquid Fund",
    "Debt Scheme - Gilt Fund",
    "Debt Scheme - Corporate Bond",
    "Hybrid Scheme - Balanced Advantage",
    "Hybrid Scheme - Aggressive Hybrid",
    "Solution Oriented Schemes",
    "Other Schemes - Index Funds",
    "Other Schemes - Gold ETF",
]
