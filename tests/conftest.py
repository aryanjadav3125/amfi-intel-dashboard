import pytest
import pytest_asyncio
from datetime import date
from scraper.models import SchemeRecord, NavRecord

@pytest.fixture
def sample_scheme_record() -> SchemeRecord:
    return SchemeRecord(
        scheme_code=119551,
        scheme_name="HDFC Index Fund - NIFTY 50 Plan - Growth",
        isin_div_payout="INF179K01844",
        isin_div_reinvest=None,
        category="Equity Scheme - Large Cap Fund",
        scheme_type="Open Ended",
        fund_house_name="HDFC Mutual Fund"
    )

@pytest.fixture
def sample_nav_record() -> NavRecord:
    return NavRecord(
        scheme_code=119551,
        nav_date=date(2026, 5, 20),
        nav_value=384.51
    )

@pytest.fixture
def raw_amfi_sample_text() -> str:
    return (
        "Open Ended Schemes ( Equity Scheme - Large Cap Fund )\n"
        "HDFC Mutual Fund\n"
        "\n"
        "Scheme Code;ISIN Div Payout/ ISIN Growth;ISIN Div Reinvestment;Scheme Name;Net Asset Value;Date\n"
        "119551;INF179K01844;-;HDFC Index Fund - NIFTY 50 Plan - Growth;384.51;20-May-2026\n"
        "122639;INF200K01UT1;-;SBI Bluechip Fund - Direct Growth;N.A.;20-May-2026\n"
        "malformed_line_with_no_semicolons\n"
    )
