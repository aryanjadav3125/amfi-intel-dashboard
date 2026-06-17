from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from database.engine import Base
from config.constants import (
    TABLE_FUND_HOUSES, TABLE_SCHEMES, TABLE_NAV_DAILY,
    TABLE_ASSET_ALLOCATION, TABLE_PIPELINE_RUNS,
    TABLE_FUND_HOUSE_AUM, TABLE_CATEGORY_AUM
)

class FundHouse(Base):
    __tablename__ = TABLE_FUND_HOUSES

    fund_house_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    code = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    schemes = relationship("Scheme", back_populates="fund_house", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<FundHouse(id={self.fund_house_id}, name='{self.name}')>"


class Scheme(Base):
    __tablename__ = TABLE_SCHEMES

    scheme_id = Column(Integer, primary_key=True, autoincrement=False)  # matching AMFI Scheme Code
    fund_house_id = Column(Integer, ForeignKey(f"{TABLE_FUND_HOUSES}.fund_house_id"), nullable=False)
    scheme_code = Column(Integer, unique=True, nullable=False, index=True)  # redundant matching key
    scheme_name = Column(String(500), nullable=False)
    isin_div_payout = Column(String(50), nullable=True)
    isin_div_reinvest = Column(String(50), nullable=True)
    isin_growth = Column(String(50), nullable=True)
    category = Column(String(255), nullable=False, index=True)
    sub_category = Column(String(255), nullable=True)
    scheme_type = Column(String(100), nullable=False)
    
    # Mapping distinct plan codes for real historical tracking
    regular_scheme_code = Column(Integer, nullable=True)
    direct_scheme_code = Column(Integer, nullable=True)
    
    # High-Fidelity Performance Grid Columns
    asset_class = Column(String(100), nullable=True)
    benchmark_name = Column(String(255), nullable=True)
    scheme_riskometer = Column(String(50), nullable=True)
    benchmark_riskometer = Column(String(50), nullable=True)
    regular_nav = Column(Float, nullable=True)
    direct_nav = Column(Float, nullable=True)
    regular_cagr_5y = Column(Float, nullable=True)
    direct_cagr_5y = Column(Float, nullable=True)
    benchmark_cagr_5y = Column(Float, nullable=True)
    regular_info_ratio = Column(Float, nullable=True)
    direct_info_ratio = Column(Float, nullable=True)
    daily_aum = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    fund_house = relationship("FundHouse", back_populates="schemes")
    navs = relationship("NavDaily", back_populates="scheme", cascade="all, delete-orphan")
    allocations = relationship("AssetAllocation", back_populates="scheme", cascade="all, delete-orphan")
    analytics = relationship("SchemeAnalytics", uselist=False, back_populates="scheme", cascade="all, delete-orphan")
    holdings = relationship("Holding", back_populates="scheme", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Scheme(code={self.scheme_code}, name='{self.scheme_name}')>"


class NavDaily(Base):
    __tablename__ = TABLE_NAV_DAILY

    nav_id = Column(Integer, primary_key=True, autoincrement=True)
    scheme_id = Column(Integer, ForeignKey(f"{TABLE_SCHEMES}.scheme_id"), nullable=False)
    nav_date = Column(Date, nullable=False, index=True)
    nav_value = Column(Float, nullable=False)  # Direct Plan NAV
    regular_nav_value = Column(Float, nullable=True)  # Regular Plan NAV
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    scheme = relationship("Scheme", back_populates="navs")

    # Constraints & Indexes
    __table_args__ = (
        UniqueConstraint("scheme_id", "nav_date", name="uq_scheme_date"),
        Index("idx_nav_scheme_date", "scheme_id", "nav_date"),
    )

    def __repr__(self):
        return f"<NavDaily(scheme_id={self.scheme_id}, date={self.nav_date}, value={self.nav_value})>"


class AssetAllocation(Base):
    __tablename__ = TABLE_ASSET_ALLOCATION

    allocation_id = Column(Integer, primary_key=True, autoincrement=True)
    scheme_id = Column(Integer, ForeignKey(f"{TABLE_SCHEMES}.scheme_id"), nullable=False)
    asset_class = Column(String(100), nullable=False)  # e.g., Equity, Debt, Cash, Gold
    percentage = Column(Float, nullable=False)
    as_of_date = Column(Date, nullable=False)

    # Relationships
    scheme = relationship("Scheme", back_populates="allocations")

    def __repr__(self):
        return f"<AssetAllocation(scheme_id={self.scheme_id}, asset={self.asset_class}, pct={self.percentage})>"


class SchemeAnalytics(Base):
    __tablename__ = "scheme_analytics"

    scheme_id = Column(Integer, ForeignKey(f"{TABLE_SCHEMES}.scheme_id"), primary_key=True)
    cagr_1m = Column(Float, nullable=True)
    cagr_3m = Column(Float, nullable=True)
    cagr_6m = Column(Float, nullable=True)
    cagr_1y = Column(Float, nullable=True)
    cagr_3y = Column(Float, nullable=True)
    cagr_5y = Column(Float, nullable=True)
    volatility = Column(Float, nullable=True)
    sharpe_ratio = Column(Float, nullable=True)
    sortino_ratio = Column(Float, nullable=True)
    max_drawdown = Column(Float, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    scheme = relationship("Scheme", back_populates="analytics")

    def __repr__(self):
        return f"<SchemeAnalytics(scheme_id={self.scheme_id})>"


class PipelineRun(Base):
    __tablename__ = TABLE_PIPELINE_RUNS

    run_id = Column(Integer, primary_key=True, autoincrement=True)
    run_type = Column(String(50), nullable=False)  # 'daily' or 'backfill'
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    records_inserted = Column(Integer, default=0)
    records_skipped = Column(Integer, default=0)
    errors_count = Column(Integer, default=0)
    status = Column(String(50), default="started")  # 'started', 'success', 'failed', 'partial'

    def __repr__(self):
        return f"<PipelineRun(id={self.run_id}, status='{self.status}')>"


class FundHouseAum(Base):
    __tablename__ = TABLE_FUND_HOUSE_AUM

    aum_id = Column(Integer, primary_key=True, autoincrement=True)
    fund_house_id = Column(Integer, ForeignKey(f"{TABLE_FUND_HOUSES}.fund_house_id"), nullable=False, index=True)
    period = Column(String(50), nullable=False, index=True)  # e.g., "Q4 2025-26", "April 2026"
    average_aum = Column(Float, nullable=False)  # in INR Crores
    aaum = Column(Float, nullable=False)  # in INR Crores
    direct_aum = Column(Float, nullable=True)  # in INR Crores
    regular_aum = Column(Float, nullable=True)  # in INR Crores
    t15_aum = Column(Float, nullable=True)  # in INR Crores
    b15_aum = Column(Float, nullable=True)  # in INR Crores
    folio_count = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    fund_house = relationship("FundHouse")

    __table_args__ = (
        UniqueConstraint("fund_house_id", "period", name="uq_amc_period"),
    )

    def __repr__(self):
        return f"<FundHouseAum(amc_id={self.fund_house_id}, period='{self.period}', average_aum={self.average_aum})>"


class CategoryAum(Base):
    __tablename__ = TABLE_CATEGORY_AUM

    category_aum_id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(255), nullable=False, index=True)  # e.g., "Equity Scheme - Large Cap Fund"
    period = Column(String(50), nullable=False, index=True)
    aum_value = Column(Float, nullable=False)  # in INR Crores
    folio_count = Column(Integer, nullable=True)
    percentage_of_total = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("category", "period", name="uq_category_period"),
    )

    def __repr__(self):
        return f"<CategoryAum(category='{self.category}', period='{self.period}', aum={self.aum_value})>"


class BenchmarkDaily(Base):
    __tablename__ = "benchmark_daily"

    benchmark_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)  # e.g., "Nifty 50 TRI", "BSE 500 TRI"
    price_date = Column(Date, nullable=False, index=True)
    price_value = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("name", "price_date", name="uq_benchmark_date"),
        Index("idx_benchmark_name_date", "name", "price_date"),
    )

    def __repr__(self):
        return f"<BenchmarkDaily(name='{self.name}', date={self.price_date}, value={self.price_value})>"


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(String(50), default="Investor")  # e.g., Admin, Analyst, Investor
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    saved_funds = relationship("SavedFund", back_populates="user", cascade="all, delete-orphan")
    saved_comparisons = relationship("SavedComparison", back_populates="user", cascade="all, delete-orphan")
    recent_searches = relationship("RecentSearch", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(email='{self.email}', role='{self.role}')>"


class SavedFund(Base):
    __tablename__ = "saved_funds"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    scheme_id = Column(Integer, ForeignKey("schemes.scheme_id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="saved_funds")
    scheme = relationship("Scheme")

    __table_args__ = (
        UniqueConstraint("user_id", "scheme_id", name="uq_user_scheme"),
    )

    def __repr__(self):
        return f"<SavedFund(user_id={self.user_id}, scheme_id={self.scheme_id})>"


class SavedComparison(Base):
    __tablename__ = "saved_comparisons"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    name = Column(String(255), nullable=False)
    scheme_ids = Column(String(1000), nullable=False)  # Semicolon/comma-separated IDs
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="saved_comparisons")

    def __repr__(self):
        return f"<SavedComparison(name='{self.name}', user_id={self.user_id})>"


class RecentSearch(Base):
    __tablename__ = "recent_searches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    query = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="recent_searches")

    def __repr__(self):
        return f"<RecentSearch(query='{self.query}', user_id={self.user_id})>"


class Holding(Base):
    __tablename__ = "holdings"

    holding_id = Column(Integer, primary_key=True, autoincrement=True)
    scheme_id = Column(Integer, ForeignKey("schemes.scheme_id"), nullable=False, index=True)
    company_name = Column(String(255), nullable=False, index=True)
    sector = Column(String(255), nullable=False, index=True)
    allocation_percentage = Column(Float, nullable=False)
    isin = Column(String(50), nullable=True)
    market_value = Column(Float, nullable=True)
    as_of_date = Column(Date, nullable=False, index=True)

    # Relationships
    scheme = relationship("Scheme", back_populates="holdings")

    def __repr__(self):
        return f"<Holding(scheme_id={self.scheme_id}, company='{self.company_name}', pct={self.allocation_percentage})>"


class Portfolio(Base):
    __tablename__ = "portfolios"

    portfolio_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User")
    funds = relationship("PortfolioFund", back_populates="portfolio", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Portfolio(id={self.portfolio_id}, name='{self.name}', user_id={self.user_id})>"


class PortfolioFund(Base):
    __tablename__ = "portfolio_funds"

    id = Column(Integer, primary_key=True, autoincrement=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.portfolio_id"), nullable=False, index=True)
    scheme_id = Column(Integer, ForeignKey("schemes.scheme_id"), nullable=False, index=True)
    allocation_percentage = Column(Float, nullable=False, default=0.0)
    invested_amount = Column(Float, nullable=True)
    added_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    portfolio = relationship("Portfolio", back_populates="funds")
    scheme = relationship("Scheme")

    __table_args__ = (
        UniqueConstraint("portfolio_id", "scheme_id", name="uq_portfolio_scheme"),
    )

    def __repr__(self):
        return f"<PortfolioFund(portfolio_id={self.portfolio_id}, scheme_id={self.scheme_id})>"


class PortfolioOverlap(Base):
    __tablename__ = "portfolio_overlaps"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scheme_a_id = Column(Integer, ForeignKey("schemes.scheme_id"), nullable=False, index=True)
    scheme_b_id = Column(Integer, ForeignKey("schemes.scheme_id"), nullable=False, index=True)
    overlap_percentage = Column(Float, nullable=False)
    common_holdings_count = Column(Integer, nullable=False)
    sector_similarity_score = Column(Float, nullable=True)
    diversification_score = Column(Float, nullable=True)
    calculated_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("scheme_a_id", "scheme_b_id", name="uq_scheme_a_b"),
    )

    def __repr__(self):
        return f"<PortfolioOverlap(a={self.scheme_a_id}, b={self.scheme_b_id}, overlap={self.overlap_percentage})>"


class AnalyticsCache(Base):
    __tablename__ = "analytics_cache"

    cache_key = Column(String(255), primary_key=True)
    cache_group = Column(String(100), nullable=False, index=True) # e.g. 'top_performers', 'dashboard_metrics'
    data_json = Column(String, nullable=False) # Store JSON string of the cached data
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<AnalyticsCache(key='{self.cache_key}', group='{self.cache_group}')>"


class ReportRecord(Base):
    __tablename__ = "report_records"

    report_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    report_type = Column(String(100), nullable=False) # 'Fund', 'Comparison', 'Portfolio'
    format = Column(String(20), nullable=False) # 'PDF', 'EXCEL', 'CSV'
    parameters_json = Column(String, nullable=True) # The filters/funds used
    file_path = Column(String(1000), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    download_count = Column(Integer, default=0)

    # Relationships
    user = relationship("User")

    def __repr__(self):
        return f"<ReportRecord(id={self.report_id}, type='{self.report_type}', user_id={self.user_id})>"
