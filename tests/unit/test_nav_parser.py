from datetime import date
from scraper.nav_parser import NavParser

def test_parse_raw_text_success(raw_amfi_sample_text):
    parser = NavParser()
    schemes, navs = parser.parse_raw_text(raw_amfi_sample_text)
    
    # 2 schemes (both HDFC and SBI are parsed)
    assert len(schemes) == 2
    
    # 1 valid NAV (HDFC has 384.51, SBI has "N.A." so its NAV is skipped, and malformed is skipped)
    assert len(navs) == 1
    
    # Assert HDFC Scheme values
    hdfc_scheme = schemes[0]
    assert hdfc_scheme.scheme_code == 119551
    assert hdfc_scheme.scheme_name == "HDFC Index Fund - NIFTY 50 Plan - Growth"
    assert hdfc_scheme.category == "Equity Scheme - Large Cap Fund"
    assert hdfc_scheme.scheme_type == "Open Ended"
    assert hdfc_scheme.fund_house_name == "HDFC Mutual Fund"
    
    # Assert HDFC NAV values
    hdfc_nav = navs[0]
    assert hdfc_nav.scheme_code == 119551
    assert hdfc_nav.nav_date == date(2026, 5, 20)
    assert hdfc_nav.nav_value == 384.51
    
    # Assert SBI Scheme values
    sbi_scheme = schemes[1]
    assert sbi_scheme.scheme_code == 122639
    assert sbi_scheme.scheme_name == "SBI Bluechip Fund - Direct Growth"
    assert sbi_scheme.category == "Equity Scheme - Large Cap Fund"
    assert sbi_scheme.fund_house_name == "HDFC Mutual Fund"  # SBI inherited current fund house in mock sample
