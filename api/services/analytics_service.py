import math
from datetime import date, timedelta
from typing import List, Dict, Any, Optional
import numpy as np
from database.models import NavDaily
from config.logging_config import get_logger

logger = get_logger("api.services.analytics")

class AnalyticsService:
    """
    Implements advanced financial calculations over mutual fund NAV histories.
    """
    
    @staticmethod
    def calculate_cagr(nav_history: List[NavDaily], days_back: int) -> Optional[float]:
        """
        Calculates Compound Annual Growth Rate (CAGR) for a given historical window in days.
        """
        if len(nav_history) < 2:
            return None
            
        today_nav = nav_history[-1]
        target_date = today_nav.nav_date - timedelta(days=days_back)
        
        # Find the NAV closest to the target date
        start_nav = None
        for nav in nav_history:
            if nav.nav_date >= target_date:
                start_nav = nav
                break
                
        if not start_nav or start_nav.nav_date == today_nav.nav_date or start_nav.nav_value <= 0:
            return None
            
        days = (today_nav.nav_date - start_nav.nav_date).days
        if days <= 0:
            return None
            
        try:
            ratio = today_nav.nav_value / start_nav.nav_value
            cagr = (ratio ** (365.0 / days)) - 1.0
            return round(cagr, 4)
        except Exception as e:
            logger.debug(f"Error calculating CAGR: {e}")
            return None

    @staticmethod
    def calculate_volatility_and_ratios(
        nav_history: List[NavDaily], risk_free_rate: float = 0.06
    ) -> Dict[str, Optional[float]]:
        """
        Calculates:
        - Annualized Volatility
        - Sharpe Ratio
        - Sortino Ratio
        - Maximum Drawdown
        """
        result = {
            "volatility": None,
            "sharpe_ratio": None,
            "sortino_ratio": None,
            "max_drawdown": None
        }
        
        if len(nav_history) < 5:
            return result

        # 1. Daily Returns
        prices = [nav.nav_value for nav in nav_history]
        dates = [nav.nav_date for nav in nav_history]
        
        returns = []
        for i in range(1, len(prices)):
            if prices[i - 1] > 0:
                returns.append((prices[i] - prices[i - 1]) / prices[i - 1])
                
        if len(returns) < 3:
            return result

        returns_arr = np.array(returns)
        
        # 2. Annualized Volatility
        daily_std = np.std(returns_arr)
        volatility = daily_std * math.sqrt(252)
        result["volatility"] = round(float(volatility), 4)

        # 3. Annualized Return (approx using total period CAGR)
        days = (dates[-1] - dates[0]).days
        if days > 0 and prices[0] > 0:
            ann_return = (prices[-1] / prices[0]) ** (365.0 / days) - 1.0
        else:
            ann_return = float(np.mean(returns_arr) * 252)

        # 4. Sharpe Ratio
        if volatility > 0:
            sharpe = (ann_return - risk_free_rate) / volatility
            result["sharpe_ratio"] = round(float(sharpe), 4)

        # 5. Sortino Ratio
        downside_returns = returns_arr[returns_arr < 0]
        if len(downside_returns) > 1:
            downside_std = np.std(downside_returns) * math.sqrt(252)
            if downside_std > 0:
                sortino = (ann_return - risk_free_rate) / downside_std
                result["sortino_ratio"] = round(float(sortino), 4)
        else:
            # Fallback if no negative returns
            if volatility > 0:
                result["sortino_ratio"] = round(float((ann_return - risk_free_rate) / volatility), 4)

        # 6. Maximum Drawdown
        peaks = []
        current_peak = -1.0
        drawdowns = []
        
        for price in prices:
            if price > current_peak:
                current_peak = price
            peaks.append(current_peak)
            
            if current_peak > 0:
                dd = (price - current_peak) / current_peak
                drawdowns.append(dd)
            else:
                drawdowns.append(0.0)
                
        if drawdowns:
            max_dd = min(drawdowns)
            result["max_drawdown"] = round(float(max_dd), 4)
            
        return result
