from pipeline.transformer import PipelineTransformer

def test_transform_scheme(sample_scheme_record):
    fund_house_id = 42
    transformed = PipelineTransformer.transform_scheme(sample_scheme_record, fund_house_id)
    
    assert transformed["scheme_id"] == 119551
    assert transformed["fund_house_id"] == 42
    assert transformed["scheme_name"] == "HDFC Index Fund - NIFTY 50 Plan - Growth"
    assert transformed["isin_div_payout"] == "INF179K01844"
    assert transformed["isin_growth"] == "INF179K01844"
    assert transformed["category"] == "Equity Scheme - Large Cap Fund"
    assert transformed["scheme_type"] == "Open Ended"


def test_transform_nav(sample_nav_record):
    transformed = PipelineTransformer.transform_nav(sample_nav_record)
    
    assert transformed["scheme_code"] == 119551
    assert transformed["nav_date"] == sample_nav_record.nav_date
    assert transformed["nav_value"] == 384.51
