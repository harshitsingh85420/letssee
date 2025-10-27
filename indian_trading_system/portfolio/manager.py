"""
Portfolio management system with position sizing and risk management.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional
import logging

from ..utils.constants import (
    MAX_POSITIONS, SECTOR_CONCENTRATION_LIMIT, MAX_PORTFOLIO_HEAT,
    MAX_CORRELATION, KELLY_FRACTION, MAX_POSITION_SIZE,
    STOP_LOSS_ATR_MULTIPLIER, STOP_LOSS_PCT
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PositionSizer:
    """
    Position sizing strategies for portfolio management.
    """

    @staticmethod
    def equal_weight(capital: float, num_positions: int) -> float:
        """
        Equal weight allocation.

        Args:
            capital: Total capital
            num_positions: Number of positions

        Returns:
            Position size per stock
        """
        return capital / num_positions

    @staticmethod
    def volatility_parity(capital: float, volatilities: Dict[str, float]) -> Dict[str, float]:
        """
        Volatility parity (inverse volatility weighting).

        Args:
            capital: Total capital
            volatilities: Dictionary mapping symbols to volatilities

        Returns:
            Dictionary with position sizes
        """
        # Inverse volatility weights
        inv_vols = {symbol: 1.0 / vol for symbol, vol in volatilities.items()}
        total_inv_vol = sum(inv_vols.values())

        # Normalize to get weights
        weights = {symbol: inv_vol / total_inv_vol for symbol, inv_vol in inv_vols.items()}

        # Calculate position sizes
        position_sizes = {symbol: capital * weight for symbol, weight in weights.items()}

        return position_sizes

    @staticmethod
    def kelly_criterion(win_rate: float, avg_win: float, avg_loss: float,
                       capital: float, fraction: float = KELLY_FRACTION,
                       max_position: float = MAX_POSITION_SIZE) -> float:
        """
        Kelly Criterion position sizing.

        Formula: f = (p * b - q) / b
        where p = win rate, q = loss rate, b = avg_win / avg_loss

        Args:
            win_rate: Historical win rate (0-1)
            avg_win: Average winning return
            avg_loss: Average losing return (positive number)
            capital: Total capital
            fraction: Fraction of Kelly to use (e.g., 0.25 for 1/4 Kelly)
            max_position: Maximum position size as fraction of capital

        Returns:
            Position size
        """
        if avg_loss == 0 or win_rate >= 1.0 or win_rate <= 0:
            return capital * max_position

        loss_rate = 1 - win_rate
        win_loss_ratio = avg_win / avg_loss

        # Kelly formula
        kelly = (win_rate * win_loss_ratio - loss_rate) / win_loss_ratio

        # Apply fraction and cap at max position
        kelly_fraction_size = max(0, kelly * fraction)
        kelly_fraction_size = min(kelly_fraction_size, max_position)

        return capital * kelly_fraction_size

    @staticmethod
    def atr_based_sizing(capital: float, atr: float, price: float,
                        risk_per_trade: float = 0.02,
                        atr_multiplier: float = STOP_LOSS_ATR_MULTIPLIER) -> int:
        """
        ATR-based position sizing (fixed risk per trade).

        Args:
            capital: Total capital
            atr: Average True Range
            price: Current price
            risk_per_trade: Risk per trade as fraction of capital (e.g., 0.02 = 2%)
            atr_multiplier: ATR multiplier for stop loss

        Returns:
            Number of shares
        """
        risk_amount = capital * risk_per_trade
        stop_distance = atr * atr_multiplier

        if stop_distance == 0:
            return 0

        shares = int(risk_amount / stop_distance)
        return shares


class PortfolioManager:
    """
    Portfolio management with risk controls.
    """

    def __init__(self, capital: float,
                 max_positions: int = MAX_POSITIONS,
                 sector_limit: float = SECTOR_CONCENTRATION_LIMIT,
                 max_heat: float = MAX_PORTFOLIO_HEAT,
                 max_correlation: float = MAX_CORRELATION):
        """
        Initialize portfolio manager.

        Args:
            capital: Total capital
            max_positions: Maximum number of positions
            sector_limit: Maximum sector concentration (as fraction)
            max_heat: Maximum portfolio heat (total exposure as fraction of capital)
            max_correlation: Maximum average correlation
        """
        self.capital = capital
        self.max_positions = max_positions
        self.sector_limit = sector_limit
        self.max_heat = max_heat
        self.max_correlation = max_correlation
        self.positions = {}  # symbol -> position info
        self.position_sizer = PositionSizer()

    def can_add_position(self, symbol: str, sector: Optional[str] = None,
                        correlation: Optional[float] = None) -> bool:
        """
        Check if a new position can be added.

        Args:
            symbol: Stock symbol
            sector: Sector (optional)
            correlation: Correlation with existing positions (optional)

        Returns:
            True if position can be added, False otherwise
        """
        # Check max positions
        if len(self.positions) >= self.max_positions:
            logger.warning(f"Cannot add {symbol}: max positions ({self.max_positions}) reached")
            return False

        # Check sector concentration
        if sector:
            sector_exposure = self._get_sector_exposure()
            current_sector_exposure = sector_exposure.get(sector, 0)

            if current_sector_exposure >= self.sector_limit:
                logger.warning(f"Cannot add {symbol}: sector {sector} at limit ({current_sector_exposure:.1%})")
                return False

        # Check portfolio heat
        current_heat = self._get_portfolio_heat()
        if current_heat >= self.max_heat:
            logger.warning(f"Cannot add {symbol}: portfolio heat at limit ({current_heat:.1%})")
            return False

        # Check correlation
        if correlation is not None and correlation > self.max_correlation:
            logger.warning(f"Cannot add {symbol}: correlation too high ({correlation:.2f})")
            return False

        return True

    def add_position(self, symbol: str, shares: int, entry_price: float,
                    stop_loss: Optional[float] = None,
                    sector: Optional[str] = None):
        """
        Add a new position.

        Args:
            symbol: Stock symbol
            shares: Number of shares
            entry_price: Entry price
            stop_loss: Stop loss price (optional)
            sector: Sector (optional)
        """
        if symbol in self.positions:
            logger.warning(f"Position for {symbol} already exists")
            return

        position_value = shares * entry_price

        self.positions[symbol] = {
            'shares': shares,
            'entry_price': entry_price,
            'current_price': entry_price,
            'stop_loss': stop_loss,
            'sector': sector,
            'position_value': position_value,
            'unrealized_pnl': 0,
            'unrealized_pnl_pct': 0
        }

        logger.info(f"Added position: {symbol}, {shares} shares @ ₹{entry_price:.2f}")

    def update_position(self, symbol: str, current_price: float):
        """
        Update position with current price.

        Args:
            symbol: Stock symbol
            current_price: Current price
        """
        if symbol not in self.positions:
            return

        position = self.positions[symbol]
        position['current_price'] = current_price

        # Update P&L
        position['unrealized_pnl'] = (current_price - position['entry_price']) * position['shares']
        position['unrealized_pnl_pct'] = (current_price - position['entry_price']) / position['entry_price']
        position['position_value'] = current_price * position['shares']

    def remove_position(self, symbol: str) -> Optional[Dict]:
        """
        Remove a position.

        Args:
            symbol: Stock symbol

        Returns:
            Position info or None if not found
        """
        if symbol in self.positions:
            position = self.positions.pop(symbol)
            logger.info(f"Removed position: {symbol}, P&L: ₹{position['unrealized_pnl']:.2f}")
            return position
        return None

    def check_stop_loss(self, symbol: str) -> bool:
        """
        Check if stop loss is hit.

        Args:
            symbol: Stock symbol

        Returns:
            True if stop loss hit, False otherwise
        """
        if symbol not in self.positions:
            return False

        position = self.positions[symbol]

        if position['stop_loss'] is None:
            return False

        if position['current_price'] <= position['stop_loss']:
            logger.warning(f"Stop loss hit for {symbol}: ₹{position['current_price']:.2f} <= ₹{position['stop_loss']:.2f}")
            return True

        return False

    def _get_sector_exposure(self) -> Dict[str, float]:
        """Get sector-wise exposure as fraction of capital."""
        sector_exposure = {}
        total_value = sum(pos['position_value'] for pos in self.positions.values())

        if total_value == 0:
            return sector_exposure

        for position in self.positions.values():
            sector = position.get('sector', 'Unknown')
            exposure = position['position_value'] / self.capital

            if sector in sector_exposure:
                sector_exposure[sector] += exposure
            else:
                sector_exposure[sector] = exposure

        return sector_exposure

    def _get_portfolio_heat(self) -> float:
        """Get portfolio heat (total exposure as fraction of capital)."""
        total_value = sum(pos['position_value'] for pos in self.positions.values())
        return total_value / self.capital

    def get_portfolio_summary(self) -> pd.DataFrame:
        """
        Get portfolio summary.

        Returns:
            DataFrame with portfolio positions
        """
        if not self.positions:
            return pd.DataFrame()

        summary = []
        for symbol, position in self.positions.items():
            summary.append({
                'symbol': symbol,
                'shares': position['shares'],
                'entry_price': position['entry_price'],
                'current_price': position['current_price'],
                'position_value': position['position_value'],
                'unrealized_pnl': position['unrealized_pnl'],
                'unrealized_pnl_pct': position['unrealized_pnl_pct'],
                'stop_loss': position.get('stop_loss'),
                'sector': position.get('sector', 'Unknown')
            })

        return pd.DataFrame(summary)

    def get_portfolio_metrics(self) -> Dict:
        """
        Get portfolio metrics.

        Returns:
            Dictionary with metrics
        """
        if not self.positions:
            return {}

        total_value = sum(pos['position_value'] for pos in self.positions.values())
        total_pnl = sum(pos['unrealized_pnl'] for pos in self.positions.values())
        total_pnl_pct = total_pnl / (total_value - total_pnl) if (total_value - total_pnl) > 0 else 0

        return {
            'num_positions': len(self.positions),
            'total_value': total_value,
            'total_pnl': total_pnl,
            'total_pnl_pct': total_pnl_pct,
            'portfolio_heat': self._get_portfolio_heat(),
            'sector_exposure': self._get_sector_exposure(),
            'capital_deployed': total_value,
            'cash_available': self.capital - total_value
        }

    def print_portfolio(self):
        """Print portfolio summary."""
        summary = self.get_portfolio_summary()

        if summary.empty:
            print("\nPortfolio is empty")
            return

        print("\n" + "="*80)
        print("PORTFOLIO SUMMARY")
        print("="*80)

        print(f"\nPositions ({len(summary)}):")
        print(summary.to_string(index=False))

        metrics = self.get_portfolio_metrics()

        print(f"\nPortfolio Metrics:")
        print(f"  Total Value: ₹{metrics['total_value']:,.2f}")
        print(f"  Unrealized P&L: ₹{metrics['total_pnl']:,.2f} ({metrics['total_pnl_pct']:.2%})")
        print(f"  Portfolio Heat: {metrics['portfolio_heat']:.2%}")
        print(f"  Cash Available: ₹{metrics['cash_available']:,.2f}")

        print(f"\nSector Exposure:")
        for sector, exposure in metrics['sector_exposure'].items():
            print(f"  {sector}: {exposure:.2%}")

        print("="*80)


if __name__ == "__main__":
    # Example usage
    portfolio = PortfolioManager(capital=1000000, max_positions=10)

    # Add positions
    portfolio.add_position('RELIANCE.NS', 100, 2500, stop_loss=2400, sector='Energy')
    portfolio.add_position('TCS.NS', 50, 3500, stop_loss=3400, sector='IT')
    portfolio.add_position('HDFCBANK.NS', 75, 1600, stop_loss=1550, sector='Banking')

    # Update prices
    portfolio.update_position('RELIANCE.NS', 2550)
    portfolio.update_position('TCS.NS', 3450)
    portfolio.update_position('HDFCBANK.NS', 1620)

    # Print portfolio
    portfolio.print_portfolio()

    # Check stop losses
    for symbol in portfolio.positions.keys():
        if portfolio.check_stop_loss(symbol):
            print(f"\nStop loss triggered for {symbol}!")
