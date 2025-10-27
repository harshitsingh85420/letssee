"""
Technical indicators for Indian equity trading system.
Includes trend, momentum, and volume indicators optimized for 5-day trading.
"""

import numpy as np
import pandas as pd
from numba import jit
import logging

from ..utils.constants import (
    SUPERTREND_PERIOD, SUPERTREND_MULTIPLIER,
    ICHIMOKU_TENKAN, ICHIMOKU_KIJUN, ICHIMOKU_SENKOU,
    ADX_PERIOD, KST_PERIODS, KST_SMAS,
    ULTIMATE_OSC_PERIODS, SCHAFF_CYCLE, SCHAFF_FAST, SCHAFF_SLOW,
    CMF_PERIOD, KLINGER_FAST, KLINGER_SLOW, KLINGER_SIGNAL
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TrendIndicators:
    """
    Trend indicators optimized for 5-day trading horizon.
    """

    @staticmethod
    def supertrend(df: pd.DataFrame, period: int = SUPERTREND_PERIOD,
                   multiplier: float = SUPERTREND_MULTIPLIER) -> pd.DataFrame:
        """
        Calculate Supertrend indicator.

        Supertrend is a trend-following indicator that works well in trending markets.

        Args:
            df: DataFrame with OHLC columns
            period: ATR period
            multiplier: ATR multiplier

        Returns:
            DataFrame with supertrend columns
        """
        result_df = df.copy()

        # Calculate ATR
        high = df['high']
        low = df['low']
        close = df['close']

        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()

        # Calculate basic bands
        hl_avg = (high + low) / 2
        upper_band = hl_avg + (multiplier * atr)
        lower_band = hl_avg - (multiplier * atr)

        # Initialize supertrend
        supertrend = pd.Series(index=df.index, dtype=float)
        direction = pd.Series(index=df.index, dtype=int)

        # First value
        supertrend.iloc[0] = lower_band.iloc[0]
        direction.iloc[0] = 1

        # Calculate supertrend
        for i in range(1, len(df)):
            if close.iloc[i] > supertrend.iloc[i-1]:
                supertrend.iloc[i] = max(lower_band.iloc[i], supertrend.iloc[i-1])
                direction.iloc[i] = 1
            elif close.iloc[i] < supertrend.iloc[i-1]:
                supertrend.iloc[i] = min(upper_band.iloc[i], supertrend.iloc[i-1])
                direction.iloc[i] = -1
            else:
                supertrend.iloc[i] = supertrend.iloc[i-1]
                direction.iloc[i] = direction.iloc[i-1]

        result_df['supertrend'] = supertrend
        result_df['supertrend_direction'] = direction
        result_df['supertrend_upper'] = upper_band
        result_df['supertrend_lower'] = lower_band

        return result_df

    @staticmethod
    def ichimoku_cloud(df: pd.DataFrame,
                      tenkan_period: int = ICHIMOKU_TENKAN,
                      kijun_period: int = ICHIMOKU_KIJUN,
                      senkou_period: int = ICHIMOKU_SENKOU) -> pd.DataFrame:
        """
        Calculate Ichimoku Cloud with compressed parameters for 5-day trading.

        Args:
            df: DataFrame with OHLC columns
            tenkan_period: Conversion line period
            kijun_period: Base line period
            senkou_period: Leading span period

        Returns:
            DataFrame with Ichimoku components
        """
        result_df = df.copy()

        high = df['high']
        low = df['low']
        close = df['close']

        # Tenkan-sen (Conversion Line)
        tenkan_high = high.rolling(window=tenkan_period).max()
        tenkan_low = low.rolling(window=tenkan_period).min()
        result_df['tenkan_sen'] = (tenkan_high + tenkan_low) / 2

        # Kijun-sen (Base Line)
        kijun_high = high.rolling(window=kijun_period).max()
        kijun_low = low.rolling(window=kijun_period).min()
        result_df['kijun_sen'] = (kijun_high + kijun_low) / 2

        # Senkou Span A (Leading Span A)
        result_df['senkou_span_a'] = ((result_df['tenkan_sen'] + result_df['kijun_sen']) / 2).shift(kijun_period)

        # Senkou Span B (Leading Span B)
        senkou_high = high.rolling(window=senkou_period).max()
        senkou_low = low.rolling(window=senkou_period).min()
        result_df['senkou_span_b'] = ((senkou_high + senkou_low) / 2).shift(kijun_period)

        # Chikou Span (Lagging Span)
        result_df['chikou_span'] = close.shift(-kijun_period)

        return result_df

    @staticmethod
    def adx(df: pd.DataFrame, period: int = ADX_PERIOD) -> pd.DataFrame:
        """
        Calculate Average Directional Index (ADX) for trend strength.

        ADX > 30 indicates strong trend.

        Args:
            df: DataFrame with OHLC columns
            period: ADX period

        Returns:
            DataFrame with ADX, +DI, -DI columns
        """
        result_df = df.copy()

        high = df['high']
        low = df['low']
        close = df['close']

        # Calculate +DM and -DM
        high_diff = high.diff()
        low_diff = -low.diff()

        plus_dm = high_diff.copy()
        plus_dm[(high_diff < 0) | (high_diff < low_diff)] = 0

        minus_dm = low_diff.copy()
        minus_dm[(low_diff < 0) | (low_diff < high_diff)] = 0

        # Calculate True Range
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        # Smooth using Wilder's smoothing
        atr = tr.ewm(alpha=1/period, adjust=False).mean()
        plus_di = 100 * (plus_dm.ewm(alpha=1/period, adjust=False).mean() / atr)
        minus_di = 100 * (minus_dm.ewm(alpha=1/period, adjust=False).mean() / atr)

        # Calculate DX and ADX
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.ewm(alpha=1/period, adjust=False).mean()

        result_df['adx'] = adx
        result_df['plus_di'] = plus_di
        result_df['minus_di'] = minus_di

        return result_df


class MomentumIndicators:
    """
    Momentum indicators optimized for 5-day trading.
    """

    @staticmethod
    def kst(df: pd.DataFrame,
            periods: list = KST_PERIODS,
            smas: list = KST_SMAS) -> pd.DataFrame:
        """
        Calculate Know Sure Thing (KST) indicator.

        KST is a momentum oscillator based on multiple ROC periods.

        Args:
            df: DataFrame with close column
            periods: ROC periods
            smas: SMA periods for each ROC

        Returns:
            DataFrame with KST and signal line
        """
        result_df = df.copy()
        close = df['close']

        # Calculate ROCs
        roc1 = ((close - close.shift(periods[0])) / close.shift(periods[0])) * 100
        roc2 = ((close - close.shift(periods[1])) / close.shift(periods[1])) * 100
        roc3 = ((close - close.shift(periods[2])) / close.shift(periods[2])) * 100
        roc4 = ((close - close.shift(periods[3])) / close.shift(periods[3])) * 100

        # Apply SMAs to ROCs
        rcma1 = roc1.rolling(window=smas[0]).mean()
        rcma2 = roc2.rolling(window=smas[1]).mean()
        rcma3 = roc3.rolling(window=smas[2]).mean()
        rcma4 = roc4.rolling(window=smas[3]).mean()

        # Calculate KST
        kst = rcma1 + rcma2 * 2 + rcma3 * 3 + rcma4 * 4

        result_df['kst'] = kst
        result_df['kst_signal'] = kst.rolling(window=3).mean()

        return result_df

    @staticmethod
    def ultimate_oscillator(df: pd.DataFrame,
                          periods: list = ULTIMATE_OSC_PERIODS) -> pd.DataFrame:
        """
        Calculate Ultimate Oscillator.

        Combines three different timeframes to reduce false signals.

        Args:
            df: DataFrame with OHLC columns
            periods: Three periods for the oscillator

        Returns:
            DataFrame with Ultimate Oscillator
        """
        result_df = df.copy()

        high = df['high']
        low = df['low']
        close = df['close']
        prev_close = close.shift(1)

        # Buying pressure
        bp = close - pd.concat([low, prev_close], axis=1).min(axis=1)

        # True range
        tr = pd.concat([
            high - low,
            abs(high - prev_close),
            abs(low - prev_close)
        ], axis=1).max(axis=1)

        # Calculate averages for each period
        avg1 = bp.rolling(window=periods[0]).sum() / tr.rolling(window=periods[0]).sum()
        avg2 = bp.rolling(window=periods[1]).sum() / tr.rolling(window=periods[1]).sum()
        avg3 = bp.rolling(window=periods[2]).sum() / tr.rolling(window=periods[2]).sum()

        # Ultimate Oscillator
        uo = 100 * ((4 * avg1 + 2 * avg2 + avg3) / 7)

        result_df['ultimate_oscillator'] = uo

        return result_df

    @staticmethod
    def schaff_trend_cycle(df: pd.DataFrame,
                          cycle: int = SCHAFF_CYCLE,
                          fast: int = SCHAFF_FAST,
                          slow: int = SCHAFF_SLOW) -> pd.DataFrame:
        """
        Calculate Schaff Trend Cycle.

        Combines MACD with Stochastic to identify trends earlier.

        Args:
            df: DataFrame with close column
            cycle: Cycle period
            fast: Fast EMA period
            slow: Slow EMA period

        Returns:
            DataFrame with STC values
        """
        result_df = df.copy()
        close = df['close']

        # Calculate MACD
        ema_fast = close.ewm(span=fast, adjust=False).mean()
        ema_slow = close.ewm(span=slow, adjust=False).mean()
        macd = ema_fast - ema_slow

        # First Stochastic
        macd_min = macd.rolling(window=cycle).min()
        macd_max = macd.rolling(window=cycle).max()

        stoch_k = 100 * (macd - macd_min) / (macd_max - macd_min)
        stoch_d = stoch_k.rolling(window=3).mean()

        # Second Stochastic
        stoch_d_min = stoch_d.rolling(window=cycle).min()
        stoch_d_max = stoch_d.rolling(window=cycle).max()

        stc = 100 * (stoch_d - stoch_d_min) / (stoch_d_max - stoch_d_min)

        result_df['stc'] = stc

        return result_df


class VolumeIndicators:
    """
    Volume-based indicators for institutional activity detection.
    """

    @staticmethod
    def cmf(df: pd.DataFrame, period: int = CMF_PERIOD) -> pd.DataFrame:
        """
        Calculate Chaikin Money Flow (CMF).

        CMF identifies divergences and accumulation/distribution.

        Args:
            df: DataFrame with OHLCV columns
            period: CMF period

        Returns:
            DataFrame with CMF values
        """
        result_df = df.copy()

        high = df['high']
        low = df['low']
        close = df['close']
        volume = df['volume']

        # Money Flow Multiplier
        mfm = ((close - low) - (high - close)) / (high - low)
        mfm = mfm.fillna(0)

        # Money Flow Volume
        mfv = mfm * volume

        # Chaikin Money Flow
        cmf = mfv.rolling(window=period).sum() / volume.rolling(window=period).sum()

        result_df['cmf'] = cmf

        return result_df

    @staticmethod
    def klinger_oscillator(df: pd.DataFrame,
                          fast: int = KLINGER_FAST,
                          slow: int = KLINGER_SLOW,
                          signal: int = KLINGER_SIGNAL) -> pd.DataFrame:
        """
        Calculate Klinger Oscillator.

        Detects long-term money flow while remaining sensitive to short-term fluctuations.

        Args:
            df: DataFrame with OHLCV columns
            fast: Fast period
            slow: Slow period
            signal: Signal line period

        Returns:
            DataFrame with Klinger Oscillator and signal line
        """
        result_df = df.copy()

        high = df['high']
        low = df['low']
        close = df['close']
        volume = df['volume']

        # Typical Price
        tp = (high + low + close) / 3

        # Trend
        trend = (tp > tp.shift(1)).astype(int)
        trend = trend.replace(0, -1)

        # Volume Force
        vf = volume * trend * abs(2 * ((tp - tp.shift(1)) / (high - low)) - 1)
        vf = vf.fillna(0)

        # Klinger Oscillator
        ko = vf.ewm(span=fast, adjust=False).mean() - vf.ewm(span=slow, adjust=False).mean()
        ko_signal = ko.ewm(span=signal, adjust=False).mean()

        result_df['klinger'] = ko
        result_df['klinger_signal'] = ko_signal

        return result_df

    @staticmethod
    def obv(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate On Balance Volume (OBV).

        OBV relates volume to price change.

        Args:
            df: DataFrame with close and volume columns

        Returns:
            DataFrame with OBV and volume ratio
        """
        result_df = df.copy()

        close = df['close']
        volume = df['volume']

        # Calculate OBV
        obv = pd.Series(index=df.index, dtype=float)
        obv.iloc[0] = volume.iloc[0]

        for i in range(1, len(df)):
            if close.iloc[i] > close.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] + volume.iloc[i]
            elif close.iloc[i] < close.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] - volume.iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i-1]

        result_df['obv'] = obv

        # Volume ratio (current volume / 20-day average)
        result_df['volume_ratio'] = volume / volume.rolling(window=20).mean()

        return result_df


class TechnicalIndicators:
    """
    Comprehensive technical indicators calculator.
    """

    def __init__(self):
        self.trend = TrendIndicators()
        self.momentum = MomentumIndicators()
        self.volume = VolumeIndicators()

    def calculate_all(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all technical indicators.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with all indicators
        """
        result_df = df.copy()

        logger.info("Calculating trend indicators...")
        result_df = self.trend.supertrend(result_df)
        result_df = self.trend.ichimoku_cloud(result_df)
        result_df = self.trend.adx(result_df)

        logger.info("Calculating momentum indicators...")
        result_df = self.momentum.kst(result_df)
        result_df = self.momentum.ultimate_oscillator(result_df)
        result_df = self.momentum.schaff_trend_cycle(result_df)

        logger.info("Calculating volume indicators...")
        result_df = self.volume.cmf(result_df)
        result_df = self.volume.klinger_oscillator(result_df)
        result_df = self.volume.obv(result_df)

        return result_df


if __name__ == "__main__":
    # Example usage
    from ..data.loader import DataLoader

    loader = DataLoader()
    df = loader.load_stock_data('RELIANCE.NS')

    if df is not None:
        indicators = TechnicalIndicators()
        df_with_indicators = indicators.calculate_all(df)

        print("\nTechnical Indicators:")
        print(df_with_indicators[['date', 'close', 'supertrend_direction',
                                   'adx', 'kst', 'cmf']].tail(10))
