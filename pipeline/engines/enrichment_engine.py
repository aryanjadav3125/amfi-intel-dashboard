import pandas as pd
import numpy as np
from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import Scheme, NavDaily, SchemeAnalytics

class EnrichmentEngine:
    """
    Calculates advanced financial metrics: CAGR, Rolling Returns, Volatility, Sharpe Ratio.
    """
    def __init__(self, session: AsyncSession):
        self.session = session

    async def generate_metrics_for_scheme(self, scheme_id: int):
        # Fetch NAVs
        result = await self.session.execute(
            select(NavDaily.nav_date, NavDaily.nav_value)
            .where(NavDaily.scheme_id == scheme_id)
            .order_by(NavDaily.nav_date)
        )
        navs = result.all()
        
        if len(navs) < 30:
            return None # Not enough data
            
        df = pd.DataFrame(navs, columns=['date', 'nav'])
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        
        # Calculate daily returns
        df['returns'] = df['nav'].pct_change()
        
        # Risk-free rate assumption (e.g., 6% annually for India)
        rf_daily = 0.06 / 252
        
        # Volatility (Annualized)
        volatility = df['returns'].std() * np.sqrt(252)
        
        # Sharpe Ratio
        mean_return = df['returns'].mean()
        sharpe_ratio = ((mean_return - rf_daily) / df['returns'].std()) * np.sqrt(252) if df['returns'].std() > 0 else 0
        
        # Max Drawdown
        roll_max = df['nav'].cummax()
        drawdown = df['nav'] / roll_max - 1.0
        max_drawdown = drawdown.min()
        
        # CAGR calculations
        latest_nav = df['nav'].iloc[-1]
        
        def calculate_cagr(years):
            days = years * 365
            past_date = df.index[-1] - pd.Timedelta(days=days)
            # find closest date
            past_df = df[df.index <= past_date]
            if past_df.empty:
                return None
            past_nav = past_df['nav'].iloc[-1]
            return ((latest_nav / past_nav) ** (1 / years) - 1) * 100
            
        # Update or create analytics record
        analytics_result = await self.session.execute(
            select(SchemeAnalytics).where(SchemeAnalytics.scheme_id == scheme_id)
        )
        analytics = analytics_result.scalar_one_or_none()
        
        if not analytics:
            analytics = SchemeAnalytics(scheme_id=scheme_id)
            self.session.add(analytics)
            
        analytics.cagr_1y = calculate_cagr(1)
        analytics.cagr_3y = calculate_cagr(3)
        analytics.cagr_5y = calculate_cagr(5)
        analytics.volatility = float(volatility) * 100 # percentage
        analytics.sharpe_ratio = float(sharpe_ratio)
        analytics.max_drawdown = float(max_drawdown) * 100 # percentage
        
        await self.session.commit()
        return analytics
