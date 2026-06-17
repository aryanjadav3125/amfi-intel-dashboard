import pytest
from scraper.aum_scraper import AumScraper

@pytest.mark.asyncio
async def test_scrape_amc_aum():
    scraper = AumScraper()
    aum_data = await scraper.scrape_amc_aum(period="Q4 2025-26")
    
    assert len(aum_data) == 8
    sbi = aum_data[0]
    assert sbi["amc_name"] == "SBI Mutual Fund"
    assert sbi["average_aum"] == 912450.60
    assert sbi["aaum"] == 918730.20
    assert sbi["direct_aum"] == 355200.0
    assert sbi["regular_aum"] == 557250.60
    assert sbi["t15_aum"] == 634500.0
    assert sbi["b15_aum"] == 277950.60
    assert sbi["folio_count"] == 15450000

@pytest.mark.asyncio
async def test_scrape_category_aum():
    scraper = AumScraper()
    cat_data = await scraper.scrape_category_aum(period="April 2026")
    
    assert len(cat_data) == 7
    large_cap = cat_data[0]
    assert large_cap["category"] == "Equity Scheme - Large Cap Fund"
    assert large_cap["aum_value"] == 286540.80
    assert large_cap["folio_count"] == 12150000
    assert large_cap["percentage_of_total"] == 25.1
