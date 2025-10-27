"""
Candlestick pattern recognition with success rate scoring.
Optimized for 5-day trading horizon in Indian equity markets.
"""

import numpy as np
import pandas as pd
from numba import jit
import logging

from ..utils.constants import PATTERN_SUCCESS_RATES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CandlestickPatterns:
    """
    Candlestick pattern recognition with historical success rate scoring.
    """

    def __init__(self):
        self.pattern_scores = PATTERN_SUCCESS_RATES

    @staticmethod
    def _body_size(open_price: float, close_price: float) -> float:
        """Calculate candle body size."""
        return abs(close_price - open_price)

    @staticmethod
    def _is_bullish(open_price: float, close_price: float) -> bool:
        """Check if candle is bullish."""
        return close_price > open_price

    @staticmethod
    def _upper_shadow(high: float, open_price: float, close_price: float) -> float:
        """Calculate upper shadow length."""
        return high - max(open_price, close_price)

    @staticmethod
    def _lower_shadow(low: float, open_price: float, close_price: float) -> float:
        """Calculate lower shadow length."""
        return min(open_price, close_price) - low

    def inverted_hammer(self, df: pd.DataFrame) -> pd.Series:
        """
        Detect Inverted Hammer pattern.

        Success rate: 60%, Average return: 1.12%
        Bullish reversal pattern with small body and long upper shadow.

        Args:
            df: DataFrame with OHLC data

        Returns:
            Series with 1 for pattern detected, 0 otherwise
        """
        open_prices = df['open']
        high = df['high']
        low = df['low']
        close = df['close']

        pattern = pd.Series(0, index=df.index)

        for i in range(1, len(df)):
            body = self._body_size(open_prices.iloc[i], close.iloc[i])
            upper_shadow = self._upper_shadow(high.iloc[i], open_prices.iloc[i], close.iloc[i])
            lower_shadow = self._lower_shadow(low.iloc[i], open_prices.iloc[i], close.iloc[i])

            # Inverted hammer: long upper shadow (2x body), small lower shadow
            if upper_shadow >= 2 * body and lower_shadow <= body * 0.3:
                # Should appear after downtrend
                if close.iloc[i-1] < close.iloc[i-5] if i >= 5 else True:
                    pattern.iloc[i] = 1

        return pattern

    def bearish_engulfing(self, df: pd.DataFrame) -> pd.Series:
        """
        Detect Bearish Engulfing pattern.

        Success rate: 57%, Average return: 0.62%
        Bearish reversal with large bearish candle engulfing previous bullish candle.

        Args:
            df: DataFrame with OHLC data

        Returns:
            Series with 1 for pattern detected, 0 otherwise
        """
        open_prices = df['open']
        close = df['close']

        pattern = pd.Series(0, index=df.index)

        for i in range(1, len(df)):
            # Previous candle should be bullish
            prev_bullish = self._is_bullish(open_prices.iloc[i-1], close.iloc[i-1])

            # Current candle should be bearish
            curr_bearish = not self._is_bullish(open_prices.iloc[i], close.iloc[i])

            if prev_bullish and curr_bearish:
                # Current candle should engulf previous
                if (open_prices.iloc[i] > close.iloc[i-1] and
                    close.iloc[i] < open_prices.iloc[i-1]):
                    pattern.iloc[i] = 1

        return pattern

    def morning_star(self, df: pd.DataFrame) -> pd.Series:
        """
        Detect Morning Star pattern.

        Success rate: 72%, Average return: 1.45%
        Bullish reversal with 3 candles: bearish, small body, bullish.

        Args:
            df: DataFrame with OHLC data

        Returns:
            Series with 1 for pattern detected, 0 otherwise
        """
        open_prices = df['open']
        close = df['close']

        pattern = pd.Series(0, index=df.index)

        for i in range(2, len(df)):
            # First candle: bearish
            first_bearish = not self._is_bullish(open_prices.iloc[i-2], close.iloc[i-2])
            first_body = self._body_size(open_prices.iloc[i-2], close.iloc[i-2])

            # Second candle: small body (gap down)
            second_body = self._body_size(open_prices.iloc[i-1], close.iloc[i-1])
            gap_down = max(open_prices.iloc[i-1], close.iloc[i-1]) < close.iloc[i-2]

            # Third candle: bullish
            third_bullish = self._is_bullish(open_prices.iloc[i], close.iloc[i])
            third_body = self._body_size(open_prices.iloc[i], close.iloc[i])

            if (first_bearish and gap_down and third_bullish and
                second_body < first_body * 0.3 and
                close.iloc[i] > (close.iloc[i-2] + open_prices.iloc[i-2]) / 2):
                pattern.iloc[i] = 1

        return pattern

    def evening_star(self, df: pd.DataFrame) -> pd.Series:
        """
        Detect Evening Star pattern.

        Success rate: 68%, Average return: -1.38%
        Bearish reversal with 3 candles: bullish, small body, bearish.

        Args:
            df: DataFrame with OHLC data

        Returns:
            Series with 1 for pattern detected, 0 otherwise
        """
        open_prices = df['open']
        close = df['close']

        pattern = pd.Series(0, index=df.index)

        for i in range(2, len(df)):
            # First candle: bullish
            first_bullish = self._is_bullish(open_prices.iloc[i-2], close.iloc[i-2])
            first_body = self._body_size(open_prices.iloc[i-2], close.iloc[i-2])

            # Second candle: small body (gap up)
            second_body = self._body_size(open_prices.iloc[i-1], close.iloc[i-1])
            gap_up = min(open_prices.iloc[i-1], close.iloc[i-1]) > close.iloc[i-2]

            # Third candle: bearish
            third_bearish = not self._is_bullish(open_prices.iloc[i], close.iloc[i])
            third_body = self._body_size(open_prices.iloc[i], close.iloc[i])

            if (first_bullish and gap_up and third_bearish and
                second_body < first_body * 0.3 and
                close.iloc[i] < (close.iloc[i-2] + open_prices.iloc[i-2]) / 2):
                pattern.iloc[i] = 1

        return pattern

    def three_white_soldiers(self, df: pd.DataFrame) -> pd.Series:
        """
        Detect Three White Soldiers pattern.

        Success rate: 65%, Average return: 1.32%
        Bullish continuation with three consecutive bullish candles.

        Args:
            df: DataFrame with OHLC data

        Returns:
            Series with 1 for pattern detected, 0 otherwise
        """
        open_prices = df['open']
        close = df['close']

        pattern = pd.Series(0, index=df.index)

        for i in range(2, len(df)):
            # All three candles should be bullish
            all_bullish = (
                self._is_bullish(open_prices.iloc[i-2], close.iloc[i-2]) and
                self._is_bullish(open_prices.iloc[i-1], close.iloc[i-1]) and
                self._is_bullish(open_prices.iloc[i], close.iloc[i])
            )

            # Each open should be within previous body
            opens_progressive = (
                open_prices.iloc[i-1] > open_prices.iloc[i-2] and
                open_prices.iloc[i-1] < close.iloc[i-2] and
                open_prices.iloc[i] > open_prices.iloc[i-1] and
                open_prices.iloc[i] < close.iloc[i-1]
            )

            # Each close should be higher
            closes_higher = (
                close.iloc[i-1] > close.iloc[i-2] and
                close.iloc[i] > close.iloc[i-1]
            )

            if all_bullish and opens_progressive and closes_higher:
                pattern.iloc[i] = 1

        return pattern

    def three_black_crows(self, df: pd.DataFrame) -> pd.Series:
        """
        Detect Three Black Crows pattern.

        Success rate: 61%, Average return: -1.15%
        Bearish continuation with three consecutive bearish candles.

        Args:
            df: DataFrame with OHLC data

        Returns:
            Series with 1 for pattern detected, 0 otherwise
        """
        open_prices = df['open']
        close = df['close']

        pattern = pd.Series(0, index=df.index)

        for i in range(2, len(df)):
            # All three candles should be bearish
            all_bearish = (
                not self._is_bullish(open_prices.iloc[i-2], close.iloc[i-2]) and
                not self._is_bullish(open_prices.iloc[i-1], close.iloc[i-1]) and
                not self._is_bullish(open_prices.iloc[i], close.iloc[i])
            )

            # Each open should be within previous body
            opens_progressive = (
                open_prices.iloc[i-1] < open_prices.iloc[i-2] and
                open_prices.iloc[i-1] > close.iloc[i-2] and
                open_prices.iloc[i] < open_prices.iloc[i-1] and
                open_prices.iloc[i] > close.iloc[i-1]
            )

            # Each close should be lower
            closes_lower = (
                close.iloc[i-1] < close.iloc[i-2] and
                close.iloc[i] < close.iloc[i-1]
            )

            if all_bearish and opens_progressive and closes_lower:
                pattern.iloc[i] = 1

        return pattern

    def gravestone_doji(self, df: pd.DataFrame) -> pd.Series:
        """
        Detect Gravestone Doji pattern.

        Success rate: 57%, Average return: -0.65%
        Bearish reversal with long upper shadow and no lower shadow.

        Args:
            df: DataFrame with OHLC data

        Returns:
            Series with 1 for pattern detected, 0 otherwise
        """
        open_prices = df['open']
        high = df['high']
        low = df['low']
        close = df['close']

        pattern = pd.Series(0, index=df.index)

        for i in range(len(df)):
            body = self._body_size(open_prices.iloc[i], close.iloc[i])
            upper_shadow = self._upper_shadow(high.iloc[i], open_prices.iloc[i], close.iloc[i])
            lower_shadow = self._lower_shadow(low.iloc[i], open_prices.iloc[i], close.iloc[i])

            # Small body, long upper shadow, minimal lower shadow
            candle_range = high.iloc[i] - low.iloc[i]

            if candle_range > 0:
                if (body / candle_range < 0.1 and
                    upper_shadow / candle_range > 0.6 and
                    lower_shadow / candle_range < 0.1):
                    pattern.iloc[i] = 1

        return pattern

    def detect_all_patterns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect all candlestick patterns.

        Args:
            df: DataFrame with OHLC data

        Returns:
            DataFrame with pattern columns
        """
        result_df = df.copy()

        logger.info("Detecting candlestick patterns...")

        result_df['pattern_inverted_hammer'] = self.inverted_hammer(df)
        result_df['pattern_bearish_engulfing'] = self.bearish_engulfing(df)
        result_df['pattern_morning_star'] = self.morning_star(df)
        result_df['pattern_evening_star'] = self.evening_star(df)
        result_df['pattern_three_white_soldiers'] = self.three_white_soldiers(df)
        result_df['pattern_three_black_crows'] = self.three_black_crows(df)
        result_df['pattern_gravestone_doji'] = self.gravestone_doji(df)

        return result_df

    def calculate_pattern_strength(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate overall pattern strength score based on historical success rates.

        Args:
            df: DataFrame with pattern columns

        Returns:
            DataFrame with pattern strength score
        """
        result_df = df.copy()

        # Bullish patterns
        bullish_score = (
            result_df['pattern_inverted_hammer'] * self.pattern_scores['INVERTED_HAMMER']['success_rate'] +
            result_df['pattern_morning_star'] * self.pattern_scores['MORNING_STAR']['success_rate'] +
            result_df['pattern_three_white_soldiers'] * self.pattern_scores['THREE_WHITE_SOLDIERS']['success_rate']
        )

        # Bearish patterns
        bearish_score = (
            result_df['pattern_bearish_engulfing'] * self.pattern_scores['BEARISH_ENGULFING']['success_rate'] +
            result_df['pattern_evening_star'] * self.pattern_scores['EVENING_STAR']['success_rate'] +
            result_df['pattern_three_black_crows'] * self.pattern_scores['THREE_BLACK_CROWS']['success_rate'] +
            result_df['pattern_gravestone_doji'] * self.pattern_scores['GRAVESTONE_DOJI']['success_rate']
        )

        # Net pattern strength (-1 to 1)
        result_df['pattern_strength'] = bullish_score - bearish_score

        return result_df

    def get_pattern_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Get summary of detected patterns.

        Args:
            df: DataFrame with pattern columns

        Returns:
            DataFrame with pattern detection summary
        """
        pattern_cols = [col for col in df.columns if col.startswith('pattern_') and col != 'pattern_strength']

        summary = []
        for col in pattern_cols:
            pattern_name = col.replace('pattern_', '').upper()
            count = df[col].sum()

            if count > 0:
                info = self.pattern_scores.get(pattern_name, {})
                success_rate = info.get('success_rate', 0)
                avg_return = info.get('avg_return', 0)

                summary.append({
                    'pattern': pattern_name,
                    'count': count,
                    'success_rate': f"{success_rate:.1%}",
                    'avg_return': f"{avg_return:.2%}"
                })

        return pd.DataFrame(summary)


if __name__ == "__main__":
    # Example usage
    from ..data.loader import DataLoader

    loader = DataLoader()
    df = loader.load_stock_data('RELIANCE.NS')

    if df is not None:
        scanner = CandlestickPatterns()

        # Detect patterns
        df_with_patterns = scanner.detect_all_patterns(df)
        df_with_patterns = scanner.calculate_pattern_strength(df_with_patterns)

        # Get summary
        summary = scanner.get_pattern_summary(df_with_patterns)

        print("\nPattern Detection Summary:")
        print(summary)

        print("\nRecent patterns detected:")
        pattern_cols = [col for col in df_with_patterns.columns if col.startswith('pattern_')]
        recent_patterns = df_with_patterns[df_with_patterns[pattern_cols].sum(axis=1) > 0].tail(10)

        if not recent_patterns.empty:
            print(recent_patterns[['date', 'close'] + pattern_cols])
        else:
            print("No patterns detected recently")
