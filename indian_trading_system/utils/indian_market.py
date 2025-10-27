"""
Indian market-specific utilities.
Transaction costs, market regime identification, and regulatory features.
"""

import numpy as np
import pandas as pd
import logging
from typing import Dict

from .constants import (
    BROKERAGE_PCT, STT_SELL_PCT, EXCHANGE_CHARGES_PCT,
    GST_RATE, STAMP_DUTY_BUY_PCT, TOTAL_TRANSACTION_COST_PCT,
    SLIPPAGE_LARGE_CAP, SLIPPAGE_MID_CAP,
    REGIME_ADX_THRESHOLD, REGIME_HURST_THRESHOLD
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IndianMarketUtils:
    """
    Utilities for Indian equity market specific features.
    """

    @staticmethod
    def calculate_transaction_costs(trade_value: float,
                                   brokerage_cap: float = 20.0) -> Dict[str, float]:
        """
        Calculate detailed transaction costs for Indian equity trading.

        Args:
            trade_value: Value of trade in INR
            brokerage_cap: Maximum brokerage per trade (default ₹20)

        Returns:
            Dictionary with cost breakdown
        """
        # Brokerage (0.03% or ₹20, whichever is lower)
        brokerage = min(trade_value * BROKERAGE_PCT / 100, brokerage_cap)

        # Exchange charges
        exchange_charges = trade_value * EXCHANGE_CHARGES_PCT / 100

        # GST on brokerage and exchange charges
        gst = (brokerage + exchange_charges) * GST_RATE

        # STT (only on sell side)
        stt = trade_value * STT_SELL_PCT / 100

        # Stamp duty (only on buy side)
        stamp_duty = trade_value * STAMP_DUTY_BUY_PCT / 100

        # SEBI charges
        sebi_charges = trade_value * 0.0001 / 100  # 0.0001%

        # Total for one-way (either buy or sell)
        buy_costs = brokerage + exchange_charges + gst + stamp_duty + sebi_charges
        sell_costs = brokerage + exchange_charges + gst + stt + sebi_charges

        # Round-trip costs
        total_round_trip = buy_costs + sell_costs

        return {
            'brokerage': brokerage,
            'stt': stt,
            'exchange_charges': exchange_charges,
            'gst': gst,
            'stamp_duty': stamp_duty,
            'sebi_charges': sebi_charges,
            'buy_costs': buy_costs,
            'sell_costs': sell_costs,
            'total_round_trip': total_round_trip,
            'total_round_trip_pct': (total_round_trip / trade_value) * 100
        }

    @staticmethod
    def get_slippage(market_cap_category: str = 'large') -> float:
        """
        Get estimated slippage based on market cap category.

        Args:
            market_cap_category: 'large', 'mid', or 'small'

        Returns:
            Slippage percentage
        """
        if market_cap_category.lower() == 'large':
            return SLIPPAGE_LARGE_CAP
        elif market_cap_category.lower() == 'mid':
            return SLIPPAGE_MID_CAP
        else:  # small cap
            return 0.002  # 0.2%

    @staticmethod
    def identify_market_regime(df: pd.DataFrame, adx_threshold: float = REGIME_ADX_THRESHOLD) -> pd.Series:
        """
        Identify market regime (trending vs ranging).

        Args:
            df: DataFrame with price data and ADX
            adx_threshold: Threshold for trending market

        Returns:
            Series with regime ('trending' or 'ranging')
        """
        if 'adx' not in df.columns:
            # Calculate ADX if not present
            from ..indicators.technical import TrendIndicators
            df = TrendIndicators.adx(df)

        regime = pd.Series('ranging', index=df.index)
        regime[df['adx'] > adx_threshold] = 'trending'

        return regime

    @staticmethod
    def calculate_hurst_exponent(df: pd.DataFrame, period: int = 100) -> pd.Series:
        """
        Calculate Hurst Exponent for trend persistence.

        Hurst > 0.5: Trending market
        Hurst = 0.5: Random walk
        Hurst < 0.5: Mean-reverting market

        Args:
            df: DataFrame with close prices
            period: Rolling window period

        Returns:
            Series with Hurst exponent values
        """
        close = df['close']
        hurst = pd.Series(index=df.index, dtype=float)

        for i in range(period, len(df)):
            ts = close.iloc[i-period:i].values

            # Calculate lags
            lags = range(2, 20)
            tau = []

            for lag in lags:
                # Calculate lag difference
                pp = np.array([ts[i:i+lag] for i in range(0, len(ts)-lag)])
                tau.append(np.sqrt(np.std(np.subtract(pp[:, -1], pp[:, 0]))))

            # Linear fit
            try:
                poly = np.polyfit(np.log(lags), np.log(tau), 1)
                hurst.iloc[i] = poly[0] * 2.0
            except:
                hurst.iloc[i] = 0.5

        return hurst

    @staticmethod
    def is_market_open(timestamp: pd.Timestamp) -> bool:
        """
        Check if Indian market is open.

        Market hours: 9:15 AM to 3:30 PM IST, Monday to Friday

        Args:
            timestamp: Timestamp to check

        Returns:
            True if market is open, False otherwise
        """
        # Check if weekday (Monday=0, Friday=4)
        if timestamp.dayofweek > 4:
            return False

        # Check time (9:15 AM to 3:30 PM)
        time = timestamp.time()
        market_open = pd.Timestamp('09:15').time()
        market_close = pd.Timestamp('15:30').time()

        return market_open <= time <= market_close

    @staticmethod
    def get_trading_holidays(year: int) -> list:
        """
        Get approximate NSE trading holidays for a year.

        Note: This is a simplified list. For production, fetch from NSE API.

        Args:
            year: Year

        Returns:
            List of holiday dates
        """
        # Common holidays (approximate)
        holidays = [
            f'{year}-01-26',  # Republic Day
            f'{year}-03-08',  # Holi (approximate)
            f'{year}-03-29',  # Good Friday (approximate)
            f'{year}-04-14',  # Ambedkar Jayanti
            f'{year}-05-01',  # Maharashtra Day
            f'{year}-08-15',  # Independence Day
            f'{year}-10-02',  # Gandhi Jayanti
            f'{year}-10-24',  # Dussehra (approximate)
            f'{year}-11-12',  # Diwali (approximate)
            f'{year}-11-13',  # Diwali Balipratipada
            f'{year}-12-25',  # Christmas
        ]

        return [pd.Timestamp(d) for d in holidays]

    @staticmethod
    def check_stock_surveillance(symbol: str) -> Dict:
        """
        Check if stock is in ASM/GSM or F&O ban.

        Note: This is a placeholder. In production, fetch from NSE API.

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary with surveillance status
        """
        # Placeholder - in production, fetch from NSE
        return {
            'in_asm': False,
            'in_gsm': False,
            'in_fno_ban': False,
            'stage': None
        }

    @staticmethod
    def calculate_sector_exposure(portfolio: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate sector-wise exposure.

        Args:
            portfolio: DataFrame with columns ['symbol', 'position_size', 'sector']

        Returns:
            DataFrame with sector exposure
        """
        if 'sector' not in portfolio.columns:
            logger.warning("Sector information not available")
            return pd.DataFrame()

        sector_exposure = portfolio.groupby('sector')['position_size'].sum()
        total_exposure = portfolio['position_size'].sum()

        sector_exposure_pct = (sector_exposure / total_exposure * 100).round(2)

        return pd.DataFrame({
            'sector': sector_exposure.index,
            'exposure': sector_exposure.values,
            'exposure_pct': sector_exposure_pct.values
        }).sort_values('exposure_pct', ascending=False)

    @staticmethod
    def calculate_correlation_matrix(returns_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate correlation matrix for portfolio stocks.

        Args:
            returns_df: DataFrame with returns for each stock

        Returns:
            Correlation matrix
        """
        return returns_df.corr()

    @staticmethod
    def calculate_portfolio_heat(positions: pd.DataFrame) -> float:
        """
        Calculate portfolio heat (total exposure as fraction of capital).

        Args:
            positions: DataFrame with position sizes

        Returns:
            Portfolio heat (0 to 1+)
        """
        if 'position_size' not in positions.columns:
            return 0.0

        return positions['position_size'].sum()


class PerformanceMetrics:
    """
    Performance metrics calculation for Indian markets.
    """

    @staticmethod
    def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.065) -> float:
        """
        Calculate Sharpe ratio.

        Args:
            returns: Series of returns
            risk_free_rate: Risk-free rate (default: 6.5% for Indian 10Y bond)

        Returns:
            Sharpe ratio
        """
        if len(returns) == 0 or returns.std() == 0:
            return 0.0

        excess_returns = returns - risk_free_rate / 252  # Daily risk-free rate
        return np.sqrt(252) * excess_returns.mean() / excess_returns.std()

    @staticmethod
    def calculate_sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.065) -> float:
        """
        Calculate Sortino ratio (only penalizes downside volatility).

        Args:
            returns: Series of returns
            risk_free_rate: Risk-free rate

        Returns:
            Sortino ratio
        """
        if len(returns) == 0:
            return 0.0

        excess_returns = returns - risk_free_rate / 252
        downside_returns = excess_returns[excess_returns < 0]

        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0.0

        return np.sqrt(252) * excess_returns.mean() / downside_returns.std()

    @staticmethod
    def calculate_max_drawdown(equity_curve: pd.Series) -> float:
        """
        Calculate maximum drawdown.

        Args:
            equity_curve: Series of portfolio values

        Returns:
            Maximum drawdown (as positive percentage)
        """
        if len(equity_curve) == 0:
            return 0.0

        cummax = equity_curve.cummax()
        drawdown = (equity_curve - cummax) / cummax

        return abs(drawdown.min())

    @staticmethod
    def calculate_calmar_ratio(returns: pd.Series, equity_curve: pd.Series) -> float:
        """
        Calculate Calmar ratio (return / max drawdown).

        Args:
            returns: Series of returns
            equity_curve: Series of portfolio values

        Returns:
            Calmar ratio
        """
        if len(returns) == 0:
            return 0.0

        annual_return = (1 + returns.mean()) ** 252 - 1
        max_dd = PerformanceMetrics.calculate_max_drawdown(equity_curve)

        if max_dd == 0:
            return 0.0

        return annual_return / max_dd

    @staticmethod
    def calculate_win_rate(returns: pd.Series) -> float:
        """
        Calculate win rate.

        Args:
            returns: Series of returns

        Returns:
            Win rate (0 to 1)
        """
        if len(returns) == 0:
            return 0.0

        winning_trades = returns[returns > 0]
        return len(winning_trades) / len(returns)

    @staticmethod
    def calculate_profit_factor(returns: pd.Series) -> float:
        """
        Calculate profit factor (gross profits / gross losses).

        Args:
            returns: Series of returns

        Returns:
            Profit factor
        """
        if len(returns) == 0:
            return 0.0

        gross_profits = returns[returns > 0].sum()
        gross_losses = abs(returns[returns < 0].sum())

        if gross_losses == 0:
            return np.inf if gross_profits > 0 else 0.0

        return gross_profits / gross_losses


if __name__ == "__main__":
    # Example usage
    market_utils = IndianMarketUtils()

    # Calculate transaction costs
    trade_value = 100000  # ₹1 lakh
    costs = market_utils.calculate_transaction_costs(trade_value)

    print("Transaction Costs for ₹1,00,000 trade:")
    for key, value in costs.items():
        if 'pct' in key:
            print(f"  {key}: {value:.4f}%")
        else:
            print(f"  {key}: ₹{value:.2f}")

    # Performance metrics
    np.random.seed(42)
    returns = pd.Series(np.random.normal(0.001, 0.02, 252))  # Simulated daily returns
    equity_curve = (1 + returns).cumprod()

    metrics = PerformanceMetrics()

    print("\nPerformance Metrics:")
    print(f"  Sharpe Ratio: {metrics.calculate_sharpe_ratio(returns):.2f}")
    print(f"  Sortino Ratio: {metrics.calculate_sortino_ratio(returns):.2f}")
    print(f"  Max Drawdown: {metrics.calculate_max_drawdown(equity_curve):.2%}")
    print(f"  Calmar Ratio: {metrics.calculate_calmar_ratio(returns, equity_curve):.2f}")
    print(f"  Win Rate: {metrics.calculate_win_rate(returns):.2%}")
    print(f"  Profit Factor: {metrics.calculate_profit_factor(returns):.2f}")
