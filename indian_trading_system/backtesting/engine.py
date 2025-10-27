"""
Backtesting engine for Indian equity trading system.
Vectorized backtesting with transaction costs and slippage.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional
import logging

from ..utils.constants import (
    TOTAL_TRANSACTION_COST_PCT, SLIPPAGE_LARGE_CAP,
    STOP_LOSS_ATR_MULTIPLIER, STOP_LOSS_PCT
)
from ..utils.indian_market import IndianMarketUtils, PerformanceMetrics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BacktestEngine:
    """
    Vectorized backtesting engine with Indian market features.
    """

    def __init__(self, initial_capital: float = 1000000,
                 commission: float = TOTAL_TRANSACTION_COST_PCT / 100,
                 slippage: float = SLIPPAGE_LARGE_CAP):
        """
        Initialize backtest engine.

        Args:
            initial_capital: Initial capital in INR
            commission: Commission rate (as decimal)
            slippage: Slippage rate (as decimal)
        """
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.market_utils = IndianMarketUtils()
        self.performance = PerformanceMetrics()

    def run_backtest(self, df: pd.DataFrame, signals: pd.Series,
                    position_size: float = 1.0) -> Dict:
        """
        Run backtest on a single stock with buy/sell signals.

        Args:
            df: DataFrame with OHLCV data
            signals: Series with signals (1=buy, -1=sell, 0=hold)
            position_size: Position size as fraction of capital (0-1)

        Returns:
            Dictionary with backtest results
        """
        logger.info(f"Running backtest with {len(df)} periods")

        # Initialize
        capital = self.initial_capital
        position = 0  # Number of shares
        entry_price = 0
        trades = []
        equity_curve = []
        positions = []

        for i in range(len(df)):
            row = df.iloc[i]
            signal = signals.iloc[i] if i < len(signals) else 0

            current_equity = capital + (position * row['close'] if position > 0 else 0)
            equity_curve.append(current_equity)
            positions.append(position)

            # Buy signal
            if signal == 1 and position == 0:
                # Calculate number of shares
                available_capital = capital * position_size
                effective_price = row['close'] * (1 + self.slippage)  # Slippage on buy
                commission_cost = available_capital * self.commission

                shares = int((available_capital - commission_cost) / effective_price)

                if shares > 0:
                    position = shares
                    entry_price = effective_price
                    cost = shares * effective_price + commission_cost
                    capital -= cost

                    trades.append({
                        'date': row['date'] if 'date' in row else i,
                        'type': 'BUY',
                        'price': effective_price,
                        'shares': shares,
                        'cost': cost,
                        'capital': capital
                    })

                    logger.debug(f"BUY: {shares} shares @ ₹{effective_price:.2f}")

            # Sell signal
            elif signal == -1 and position > 0:
                # Sell all shares
                effective_price = row['close'] * (1 - self.slippage)  # Slippage on sell
                proceeds = position * effective_price
                commission_cost = proceeds * self.commission
                net_proceeds = proceeds - commission_cost

                capital += net_proceeds

                # Calculate P&L
                pnl = (effective_price - entry_price) * position - commission_cost - (entry_price * position * self.commission)
                pnl_pct = pnl / (entry_price * position)

                trades.append({
                    'date': row['date'] if 'date' in row else i,
                    'type': 'SELL',
                    'price': effective_price,
                    'shares': position,
                    'proceeds': net_proceeds,
                    'capital': capital,
                    'pnl': pnl,
                    'pnl_pct': pnl_pct
                })

                logger.debug(f"SELL: {position} shares @ ₹{effective_price:.2f}, P&L: ₹{pnl:.2f} ({pnl_pct:.2%})")

                position = 0
                entry_price = 0

        # Close any open position at the end
        if position > 0:
            final_price = df.iloc[-1]['close'] * (1 - self.slippage)
            proceeds = position * final_price
            commission_cost = proceeds * self.commission
            net_proceeds = proceeds - commission_cost
            capital += net_proceeds

            pnl = (final_price - entry_price) * position - commission_cost - (entry_price * position * self.commission)
            pnl_pct = pnl / (entry_price * position)

            trades.append({
                'date': df.iloc[-1]['date'] if 'date' in df.columns else len(df)-1,
                'type': 'SELL',
                'price': final_price,
                'shares': position,
                'proceeds': net_proceeds,
                'capital': capital,
                'pnl': pnl,
                'pnl_pct': pnl_pct
            })

        # Calculate metrics
        final_equity = equity_curve[-1] if equity_curve else self.initial_capital
        total_return = (final_equity - self.initial_capital) / self.initial_capital

        trades_df = pd.DataFrame(trades)
        equity_series = pd.Series(equity_curve)
        returns = equity_series.pct_change().dropna()

        # Extract realized P&L
        realized_pnl = trades_df[trades_df['type'] == 'SELL']['pnl'].sum() if len(trades_df) > 0 else 0

        results = {
            'initial_capital': self.initial_capital,
            'final_equity': final_equity,
            'total_return': total_return,
            'total_return_pct': total_return * 100,
            'realized_pnl': realized_pnl,
            'num_trades': len(trades_df[trades_df['type'] == 'BUY']),
            'equity_curve': equity_series,
            'trades': trades_df,
            'positions': pd.Series(positions)
        }

        # Performance metrics
        if len(returns) > 0:
            results['sharpe_ratio'] = self.performance.calculate_sharpe_ratio(returns)
            results['sortino_ratio'] = self.performance.calculate_sortino_ratio(returns)
            results['max_drawdown'] = self.performance.calculate_max_drawdown(equity_series)
            results['calmar_ratio'] = self.performance.calculate_calmar_ratio(returns, equity_series)

        # Trade metrics
        if len(trades_df) > 0 and 'pnl' in trades_df.columns:
            sell_trades = trades_df[trades_df['type'] == 'SELL']
            if len(sell_trades) > 0:
                results['win_rate'] = len(sell_trades[sell_trades['pnl'] > 0]) / len(sell_trades)
                results['avg_win'] = sell_trades[sell_trades['pnl'] > 0]['pnl'].mean() if len(sell_trades[sell_trades['pnl'] > 0]) > 0 else 0
                results['avg_loss'] = sell_trades[sell_trades['pnl'] < 0]['pnl'].mean() if len(sell_trades[sell_trades['pnl'] < 0]) > 0 else 0
                results['profit_factor'] = self.performance.calculate_profit_factor(sell_trades['pnl'])

        logger.info(f"Backtest complete: Return={total_return:.2%}, Trades={results['num_trades']}")

        return results

    def run_multi_stock_backtest(self, data_dict: Dict[str, pd.DataFrame],
                                 signals_dict: Dict[str, pd.Series],
                                 position_size_per_stock: float = 0.1) -> Dict:
        """
        Run backtest on multiple stocks with portfolio management.

        Args:
            data_dict: Dictionary mapping symbols to DataFrames
            signals_dict: Dictionary mapping symbols to signal Series
            position_size_per_stock: Position size per stock (as fraction of capital)

        Returns:
            Dictionary with portfolio backtest results
        """
        logger.info(f"Running multi-stock backtest with {len(data_dict)} stocks")

        # Run individual backtests
        stock_results = {}
        for symbol in data_dict.keys():
            if symbol in signals_dict:
                logger.info(f"Backtesting {symbol}")
                results = self.run_backtest(
                    data_dict[symbol],
                    signals_dict[symbol],
                    position_size_per_stock
                )
                stock_results[symbol] = results

        # Combine equity curves
        combined_equity = pd.DataFrame({
            symbol: results['equity_curve']
            for symbol, results in stock_results.items()
        })

        # Portfolio equity (assuming equal start)
        portfolio_equity = combined_equity.sum(axis=1) - (len(stock_results) - 1) * self.initial_capital

        # Calculate portfolio metrics
        portfolio_returns = portfolio_equity.pct_change().dropna()

        portfolio_results = {
            'initial_capital': self.initial_capital,
            'final_equity': portfolio_equity.iloc[-1],
            'total_return': (portfolio_equity.iloc[-1] - self.initial_capital) / self.initial_capital,
            'equity_curve': portfolio_equity,
            'stock_results': stock_results
        }

        # Performance metrics
        if len(portfolio_returns) > 0:
            portfolio_results['sharpe_ratio'] = self.performance.calculate_sharpe_ratio(portfolio_returns)
            portfolio_results['sortino_ratio'] = self.performance.calculate_sortino_ratio(portfolio_returns)
            portfolio_results['max_drawdown'] = self.performance.calculate_max_drawdown(portfolio_equity)
            portfolio_results['calmar_ratio'] = self.performance.calculate_calmar_ratio(portfolio_returns, portfolio_equity)

        # Aggregate trade statistics
        total_trades = sum(r.get('num_trades', 0) for r in stock_results.values())
        portfolio_results['total_trades'] = total_trades

        logger.info(f"Portfolio backtest complete: Return={portfolio_results['total_return']:.2%}")

        return portfolio_results

    def print_results(self, results: Dict):
        """
        Print backtest results in a readable format.

        Args:
            results: Results dictionary from run_backtest
        """
        print("\n" + "="*60)
        print("BACKTEST RESULTS")
        print("="*60)

        print(f"\nCapital:")
        print(f"  Initial: ₹{results['initial_capital']:,.2f}")
        print(f"  Final: ₹{results['final_equity']:,.2f}")
        print(f"  P&L: ₹{results['final_equity'] - results['initial_capital']:,.2f}")
        print(f"  Return: {results['total_return']:.2%}")

        print(f"\nPerformance Metrics:")
        if 'sharpe_ratio' in results:
            print(f"  Sharpe Ratio: {results['sharpe_ratio']:.2f}")
        if 'sortino_ratio' in results:
            print(f"  Sortino Ratio: {results['sortino_ratio']:.2f}")
        if 'max_drawdown' in results:
            print(f"  Max Drawdown: {results['max_drawdown']:.2%}")
        if 'calmar_ratio' in results:
            print(f"  Calmar Ratio: {results['calmar_ratio']:.2f}")

        print(f"\nTrading Statistics:")
        print(f"  Number of Trades: {results.get('num_trades', 0)}")
        if 'win_rate' in results:
            print(f"  Win Rate: {results['win_rate']:.2%}")
        if 'avg_win' in results:
            print(f"  Average Win: ₹{results['avg_win']:,.2f}")
        if 'avg_loss' in results:
            print(f"  Average Loss: ₹{results['avg_loss']:,.2f}")
        if 'profit_factor' in results:
            print(f"  Profit Factor: {results['profit_factor']:.2f}")

        print("\n" + "="*60)


if __name__ == "__main__":
    # Example usage
    from ..data.loader import DataLoader

    loader = DataLoader()
    df = loader.load_stock_data('RELIANCE.NS')

    if df is not None:
        # Create simple moving average crossover signals
        df['sma_5'] = df['close'].rolling(window=5).mean()
        df['sma_20'] = df['close'].rolling(window=20).mean()

        signals = pd.Series(0, index=df.index)
        signals[df['sma_5'] > df['sma_20']] = 1  # Buy signal
        signals[df['sma_5'] < df['sma_20']] = -1  # Sell signal

        # Run backtest
        engine = BacktestEngine(initial_capital=1000000)
        results = engine.run_backtest(df, signals, position_size=0.3)

        # Print results
        engine.print_results(results)

        # Show recent trades
        if len(results['trades']) > 0:
            print("\nRecent Trades:")
            print(results['trades'].tail(10))
