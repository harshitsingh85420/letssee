"""
Signal generation system combining technical indicators, patterns, and ML predictions.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional
import logging

from ..indicators.technical import TechnicalIndicators
from ..indicators.volatility import VolatilityEstimators
from ..indicators.patterns import CandlestickPatterns
from ..utils.constants import ADX_TREND_THRESHOLD

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SignalGenerator:
    """
    Generate trading signals by combining multiple indicators and ML predictions.
    """

    def __init__(self):
        """Initialize signal generator."""
        self.technical = TechnicalIndicators()
        self.volatility = VolatilityEstimators()
        self.patterns = CandlestickPatterns()

    def generate_trend_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trend-based signals.

        Args:
            df: DataFrame with technical indicators

        Returns:
            DataFrame with trend signals
        """
        result_df = df.copy()

        # Supertrend signal
        result_df['signal_supertrend'] = 0
        result_df.loc[result_df['supertrend_direction'] == 1, 'signal_supertrend'] = 1
        result_df.loc[result_df['supertrend_direction'] == -1, 'signal_supertrend'] = -1

        # Ichimoku signal
        result_df['signal_ichimoku'] = 0
        bullish_ichimoku = (
            (result_df['close'] > result_df['senkou_span_a']) &
            (result_df['close'] > result_df['senkou_span_b']) &
            (result_df['tenkan_sen'] > result_df['kijun_sen'])
        )
        bearish_ichimoku = (
            (result_df['close'] < result_df['senkou_span_a']) &
            (result_df['close'] < result_df['senkou_span_b']) &
            (result_df['tenkan_sen'] < result_df['kijun_sen'])
        )
        result_df.loc[bullish_ichimoku, 'signal_ichimoku'] = 1
        result_df.loc[bearish_ichimoku, 'signal_ichimoku'] = -1

        # ADX trend strength (filter)
        result_df['strong_trend'] = result_df['adx'] > ADX_TREND_THRESHOLD

        return result_df

    def generate_momentum_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate momentum-based signals.

        Args:
            df: DataFrame with momentum indicators

        Returns:
            DataFrame with momentum signals
        """
        result_df = df.copy()

        # KST signal
        result_df['signal_kst'] = 0
        bullish_kst = (result_df['kst'] > result_df['kst_signal']) & (result_df['kst'] > 0)
        bearish_kst = (result_df['kst'] < result_df['kst_signal']) & (result_df['kst'] < 0)
        result_df.loc[bullish_kst, 'signal_kst'] = 1
        result_df.loc[bearish_kst, 'signal_kst'] = -1

        # Ultimate Oscillator signal
        result_df['signal_uo'] = 0
        result_df.loc[result_df['ultimate_oscillator'] > 70, 'signal_uo'] = -1  # Overbought
        result_df.loc[result_df['ultimate_oscillator'] < 30, 'signal_uo'] = 1   # Oversold

        # Schaff Trend Cycle signal
        result_df['signal_stc'] = 0
        bullish_stc = (result_df['stc'] > 25) & (result_df['stc'] < 75)
        bearish_stc = result_df['stc'] > 75
        result_df.loc[bullish_stc, 'signal_stc'] = 1
        result_df.loc[bearish_stc, 'signal_stc'] = -1

        return result_df

    def generate_volume_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate volume-based signals.

        Args:
            df: DataFrame with volume indicators

        Returns:
            DataFrame with volume signals
        """
        result_df = df.copy()

        # CMF signal (divergence and accumulation)
        result_df['signal_cmf'] = 0
        result_df.loc[result_df['cmf'] > 0.1, 'signal_cmf'] = 1   # Accumulation
        result_df.loc[result_df['cmf'] < -0.1, 'signal_cmf'] = -1  # Distribution

        # Klinger signal
        result_df['signal_klinger'] = 0
        bullish_klinger = result_df['klinger'] > result_df['klinger_signal']
        bearish_klinger = result_df['klinger'] < result_df['klinger_signal']
        result_df.loc[bullish_klinger, 'signal_klinger'] = 1
        result_df.loc[bearish_klinger, 'signal_klinger'] = -1

        # OBV signal (using price comparison)
        result_df['obv_sma'] = result_df['obv'].rolling(window=20).mean()
        result_df['signal_obv'] = 0
        result_df.loc[result_df['obv'] > result_df['obv_sma'], 'signal_obv'] = 1
        result_df.loc[result_df['obv'] < result_df['obv_sma'], 'signal_obv'] = -1

        return result_df

    def combine_signals(self, df: pd.DataFrame,
                       weights: Optional[Dict[str, float]] = None) -> pd.DataFrame:
        """
        Combine all signals into a single composite signal.

        Args:
            df: DataFrame with all individual signals
            weights: Weights for each signal type (optional)

        Returns:
            DataFrame with combined signal
        """
        if weights is None:
            # Default weights
            weights = {
                'trend': 0.35,
                'momentum': 0.25,
                'volume': 0.20,
                'pattern': 0.20
            }

        result_df = df.copy()

        # Get signal columns
        trend_signals = ['signal_supertrend', 'signal_ichimoku']
        momentum_signals = ['signal_kst', 'signal_uo', 'signal_stc']
        volume_signals = ['signal_cmf', 'signal_klinger', 'signal_obv']

        # Average signals by category
        result_df['avg_trend_signal'] = result_df[trend_signals].mean(axis=1)
        result_df['avg_momentum_signal'] = result_df[momentum_signals].mean(axis=1)
        result_df['avg_volume_signal'] = result_df[volume_signals].mean(axis=1)

        # Pattern strength (already normalized -1 to 1)
        if 'pattern_strength' in result_df.columns:
            result_df['pattern_signal'] = result_df['pattern_strength']
        else:
            result_df['pattern_signal'] = 0

        # Weighted composite signal
        result_df['composite_signal'] = (
            result_df['avg_trend_signal'] * weights['trend'] +
            result_df['avg_momentum_signal'] * weights['momentum'] +
            result_df['avg_volume_signal'] * weights['volume'] +
            result_df['pattern_signal'] * weights['pattern']
        )

        # Apply trend filter: only take signals in strong trends
        if 'strong_trend' in result_df.columns:
            result_df.loc[~result_df['strong_trend'], 'composite_signal'] *= 0.5

        return result_df

    def generate_entry_exit_signals(self, df: pd.DataFrame,
                                   entry_threshold: float = 0.3,
                                   exit_threshold: float = -0.2) -> pd.DataFrame:
        """
        Generate entry and exit signals from composite signal.

        Args:
            df: DataFrame with composite signal
            entry_threshold: Threshold for entry signal (positive for buy)
            exit_threshold: Threshold for exit signal (negative for sell)

        Returns:
            DataFrame with entry/exit signals
        """
        result_df = df.copy()

        # Entry signals (1 = buy, -1 = sell short, 0 = no action)
        result_df['entry_signal'] = 0
        result_df.loc[result_df['composite_signal'] > entry_threshold, 'entry_signal'] = 1
        result_df.loc[result_df['composite_signal'] < -entry_threshold, 'entry_signal'] = -1

        # Exit signals
        result_df['exit_signal'] = 0
        result_df.loc[result_df['composite_signal'] < exit_threshold, 'exit_signal'] = 1

        # Trading signal: combines entry and exit
        # 1 = buy/hold, -1 = sell/exit, 0 = no position
        result_df['trading_signal'] = result_df['entry_signal']

        return result_df

    def add_ml_signals(self, df: pd.DataFrame, ml_predictions: pd.Series,
                      ml_weight: float = 0.3) -> pd.DataFrame:
        """
        Add ML predictions to the signal generation.

        Args:
            df: DataFrame with composite signals
            ml_predictions: Series with ML predictions (probabilities 0-1)
            ml_weight: Weight for ML predictions

        Returns:
            DataFrame with ML-enhanced signals
        """
        result_df = df.copy()

        # Convert ML probabilities to signals (-1 to 1)
        ml_signal = (ml_predictions - 0.5) * 2  # Maps 0-1 to -1 to 1

        # Combine with existing composite signal
        result_df['composite_signal_with_ml'] = (
            result_df['composite_signal'] * (1 - ml_weight) +
            ml_signal * ml_weight
        )

        return result_df

    def generate_all_signals(self, df: pd.DataFrame,
                           ml_predictions: Optional[pd.Series] = None) -> pd.DataFrame:
        """
        Generate all signals from indicators.

        Args:
            df: DataFrame with OHLCV data
            ml_predictions: ML predictions (optional)

        Returns:
            DataFrame with all signals
        """
        logger.info("Generating signals...")

        # Calculate indicators if not present
        if 'supertrend' not in df.columns:
            logger.info("Calculating technical indicators...")
            df = self.technical.calculate_all(df)

        if 'yang_zhang_vol' not in df.columns:
            logger.info("Calculating volatility indicators...")
            df = self.volatility.calculate_all(df)

        if 'pattern_inverted_hammer' not in df.columns:
            logger.info("Detecting candlestick patterns...")
            df = self.patterns.detect_all_patterns(df)
            df = self.patterns.calculate_pattern_strength(df)

        # Generate signals by category
        df = self.generate_trend_signals(df)
        df = self.generate_momentum_signals(df)
        df = self.generate_volume_signals(df)

        # Combine signals
        df = self.combine_signals(df)

        # Add ML signals if available
        if ml_predictions is not None:
            df = self.add_ml_signals(df, ml_predictions)
            signal_col = 'composite_signal_with_ml'
        else:
            signal_col = 'composite_signal'

        # Generate entry/exit signals
        df['composite_signal'] = df[signal_col]
        df = self.generate_entry_exit_signals(df)

        logger.info("Signal generation complete")

        return df

    def get_signal_summary(self, df: pd.DataFrame, recent_days: int = 5) -> pd.DataFrame:
        """
        Get summary of recent signals.

        Args:
            df: DataFrame with signals
            recent_days: Number of recent days to show

        Returns:
            DataFrame with signal summary
        """
        recent_df = df.tail(recent_days).copy()

        signal_cols = ['date', 'close', 'composite_signal', 'trading_signal',
                      'strong_trend', 'pattern_strength']

        available_cols = [col for col in signal_cols if col in recent_df.columns]

        return recent_df[available_cols]


class StockRanker:
    """
    Rank stocks by signal strength for portfolio selection.
    """

    @staticmethod
    def rank_by_signal_strength(signals_dict: Dict[str, pd.DataFrame],
                               top_n: int = 10) -> pd.DataFrame:
        """
        Rank stocks by current signal strength.

        Args:
            signals_dict: Dictionary mapping symbols to DataFrames with signals
            top_n: Number of top stocks to return

        Returns:
            DataFrame with ranked stocks
        """
        rankings = []

        for symbol, df in signals_dict.items():
            if df.empty or 'composite_signal' not in df.columns:
                continue

            latest = df.iloc[-1]

            rankings.append({
                'symbol': symbol,
                'signal_strength': latest.get('composite_signal', 0),
                'trend_signal': latest.get('avg_trend_signal', 0),
                'momentum_signal': latest.get('avg_momentum_signal', 0),
                'volume_signal': latest.get('avg_volume_signal', 0),
                'pattern_strength': latest.get('pattern_strength', 0),
                'close': latest.get('close', 0),
                'adx': latest.get('adx', 0)
            })

        rankings_df = pd.DataFrame(rankings)

        if rankings_df.empty:
            return rankings_df

        # Sort by signal strength
        rankings_df = rankings_df.sort_values('signal_strength', ascending=False)

        return rankings_df.head(top_n)


if __name__ == "__main__":
    # Example usage
    from ..data.loader import DataLoader

    loader = DataLoader()
    df = loader.load_stock_data('RELIANCE.NS')

    if df is not None:
        # Generate signals
        signal_gen = SignalGenerator()
        df_with_signals = signal_gen.generate_all_signals(df)

        print("\nSignal Summary (Last 10 days):")
        print(signal_gen.get_signal_summary(df_with_signals, recent_days=10))

        # Show recent trading signals
        recent_trades = df_with_signals[df_with_signals['trading_signal'] != 0].tail(5)
        if not recent_trades.empty:
            print("\nRecent Trading Signals:")
            print(recent_trades[['date', 'close', 'trading_signal', 'composite_signal']])
