"""
Feature engineering for machine learning models.
Optimized for 5-day return prediction in Indian equity markets.
"""

import numpy as np
import pandas as pd
import logging

from ..utils.constants import (
    ML_TARGET_RETURN, ML_LOOKBACK_PERIODS,
    ML_RSI_PERIOD, ML_MACD_FAST, ML_MACD_SLOW, ML_MACD_SIGNAL,
    ML_ADX_PERIOD, TRADING_HORIZON_DAYS
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeatureEngineer:
    """
    Feature engineering for machine learning models.
    """

    def __init__(self, target_return: float = ML_TARGET_RETURN,
                 horizon_days: int = TRADING_HORIZON_DAYS):
        """
        Initialize feature engineer.

        Args:
            target_return: Target return threshold for classification
            horizon_days: Forward-looking horizon for returns
        """
        self.target_return = target_return
        self.horizon_days = horizon_days

    def create_price_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create price-based features.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with price features
        """
        result_df = df.copy()

        # Returns for different periods
        for period in ML_LOOKBACK_PERIODS:
            result_df[f'returns_{period}d'] = df['close'].pct_change(period)
            result_df[f'log_returns_{period}d'] = np.log(df['close'] / df['close'].shift(period))

        # Moving averages
        for period in [5, 10, 20]:
            result_df[f'sma_{period}'] = df['close'].rolling(window=period).mean()
            result_df[f'ema_{period}'] = df['close'].ewm(span=period, adjust=False).mean()

            # Price relative to moving average
            result_df[f'price_to_sma_{period}'] = df['close'] / result_df[f'sma_{period}']
            result_df[f'price_to_ema_{period}'] = df['close'] / result_df[f'ema_{period}']

        # High-low range
        result_df['hl_range'] = (df['high'] - df['low']) / df['close']

        # Close position within daily range
        result_df['close_position'] = (df['close'] - df['low']) / (df['high'] - df['low'])
        result_df['close_position'] = result_df['close_position'].fillna(0.5)

        # Gap (open vs previous close)
        result_df['gap'] = (df['open'] - df['close'].shift(1)) / df['close'].shift(1)

        return result_df

    def create_technical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create technical indicator features.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with technical features
        """
        result_df = df.copy()

        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=ML_RSI_PERIOD).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=ML_RSI_PERIOD).mean()
        rs = gain / loss
        result_df['rsi'] = 100 - (100 / (1 + rs))

        # MACD
        ema_fast = df['close'].ewm(span=ML_MACD_FAST, adjust=False).mean()
        ema_slow = df['close'].ewm(span=ML_MACD_SLOW, adjust=False).mean()
        result_df['macd'] = ema_fast - ema_slow
        result_df['macd_signal'] = result_df['macd'].ewm(span=ML_MACD_SIGNAL, adjust=False).mean()
        result_df['macd_hist'] = result_df['macd'] - result_df['macd_signal']

        # Bollinger Bands
        bb_period = 20
        bb_std = 2
        sma = df['close'].rolling(window=bb_period).mean()
        std = df['close'].rolling(window=bb_period).std()
        result_df['bb_upper'] = sma + (bb_std * std)
        result_df['bb_lower'] = sma - (bb_std * std)
        result_df['bb_position'] = (df['close'] - result_df['bb_lower']) / (result_df['bb_upper'] - result_df['bb_lower'])

        # Stochastic Oscillator
        stoch_period = 14
        low_min = df['low'].rolling(window=stoch_period).min()
        high_max = df['high'].rolling(window=stoch_period).max()
        result_df['stoch_k'] = 100 * (df['close'] - low_min) / (high_max - low_min)
        result_df['stoch_d'] = result_df['stoch_k'].rolling(window=3).mean()

        # ADX (simplified)
        high_diff = df['high'].diff()
        low_diff = -df['low'].diff()

        plus_dm = high_diff.where((high_diff > 0) & (high_diff > low_diff), 0)
        minus_dm = low_diff.where((low_diff > 0) & (low_diff > high_diff), 0)

        tr1 = df['high'] - df['low']
        tr2 = abs(df['high'] - df['close'].shift(1))
        tr3 = abs(df['low'] - df['close'].shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        atr = tr.ewm(alpha=1/ML_ADX_PERIOD, adjust=False).mean()
        plus_di = 100 * (plus_dm.ewm(alpha=1/ML_ADX_PERIOD, adjust=False).mean() / atr)
        minus_di = 100 * (minus_dm.ewm(alpha=1/ML_ADX_PERIOD, adjust=False).mean() / atr)

        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        result_df['adx'] = dx.ewm(alpha=1/ML_ADX_PERIOD, adjust=False).mean()

        return result_df

    def create_volume_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create volume-based features.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with volume features
        """
        result_df = df.copy()

        # Volume ratios
        for period in [5, 10, 20]:
            result_df[f'volume_ratio_{period}d'] = df['volume'] / df['volume'].rolling(window=period).mean()

        # Volume change
        result_df['volume_change'] = df['volume'].pct_change()

        # On Balance Volume (OBV)
        obv = pd.Series(index=df.index, dtype=float)
        obv.iloc[0] = df['volume'].iloc[0]

        for i in range(1, len(df)):
            if df['close'].iloc[i] > df['close'].iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] + df['volume'].iloc[i]
            elif df['close'].iloc[i] < df['close'].iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] - df['volume'].iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i-1]

        result_df['obv'] = obv
        result_df['obv_change'] = obv.pct_change(5)

        # Volume-weighted average price (approximation)
        result_df['vwap_ratio'] = df['close'] / ((df['high'] + df['low'] + df['close']) / 3)

        return result_df

    def create_volatility_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create volatility features.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with volatility features
        """
        result_df = df.copy()

        # Historical volatility
        for period in [5, 10, 20]:
            returns = df['close'].pct_change()
            result_df[f'volatility_{period}d'] = returns.rolling(window=period).std() * np.sqrt(252)

        # ATR-based volatility
        tr1 = df['high'] - df['low']
        tr2 = abs(df['high'] - df['close'].shift(1))
        tr3 = abs(df['low'] - df['close'].shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        for period in [7, 14]:
            atr = tr.ewm(alpha=1/period, adjust=False).mean()
            result_df[f'atr_{period}'] = atr
            result_df[f'atr_pct_{period}'] = atr / df['close']

        return result_df

    def create_momentum_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create momentum features.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with momentum features
        """
        result_df = df.copy()

        # Rate of change
        for period in [3, 5, 10]:
            result_df[f'roc_{period}d'] = ((df['close'] - df['close'].shift(period)) /
                                           df['close'].shift(period)) * 100

        # Momentum
        for period in [5, 10]:
            result_df[f'momentum_{period}d'] = df['close'] - df['close'].shift(period)

        # Relative performance vs moving average
        sma_20 = df['close'].rolling(window=20).mean()
        result_df['relative_strength'] = df['close'] / sma_20 - 1

        return result_df

    def create_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create time-based features.

        Args:
            df: DataFrame with date column

        Returns:
            DataFrame with time features
        """
        result_df = df.copy()

        if 'date' in result_df.columns:
            result_df['date'] = pd.to_datetime(result_df['date'])

            # Day of week (0 = Monday, 4 = Friday)
            result_df['day_of_week'] = result_df['date'].dt.dayofweek

            # Day of month
            result_df['day_of_month'] = result_df['date'].dt.day

            # Month
            result_df['month'] = result_df['date'].dt.month

            # Week of year
            result_df['week_of_year'] = result_df['date'].dt.isocalendar().week

            # Is month end (last 3 trading days)
            result_df['is_month_end'] = (result_df['day_of_month'] >= 28).astype(int)

        return result_df

    def create_target(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create target variable for classification.

        Args:
            df: DataFrame with close prices

        Returns:
            DataFrame with target variable
        """
        result_df = df.copy()

        # Forward returns
        result_df['forward_returns'] = (df['close'].shift(-self.horizon_days) /
                                       df['close']) - 1

        # Binary target: 1 if forward return > target_return, else 0
        result_df['target'] = (result_df['forward_returns'] > self.target_return).astype(int)

        return result_df

    def create_all_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create all features.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with all features
        """
        logger.info("Creating features...")

        result_df = df.copy()

        result_df = self.create_price_features(result_df)
        result_df = self.create_technical_features(result_df)
        result_df = self.create_volume_features(result_df)
        result_df = self.create_volatility_features(result_df)
        result_df = self.create_momentum_features(result_df)
        result_df = self.create_time_features(result_df)
        result_df = self.create_target(result_df)

        logger.info(f"Created {len(result_df.columns)} total columns")

        return result_df

    def get_feature_columns(self, df: pd.DataFrame) -> list:
        """
        Get list of feature columns (excluding OHLCV, date, symbol, target).

        Args:
            df: DataFrame with features

        Returns:
            List of feature column names
        """
        exclude_cols = ['open', 'high', 'low', 'close', 'volume',
                       'date', 'symbol', 'target', 'forward_returns',
                       'adj close', 'dividends', 'stock splits']

        feature_cols = [col for col in df.columns
                       if col.lower() not in [c.lower() for c in exclude_cols]]

        return feature_cols

    def prepare_ml_data(self, df: pd.DataFrame) -> tuple:
        """
        Prepare data for machine learning (features and target).

        Args:
            df: DataFrame with all features

        Returns:
            Tuple of (X, y, feature_names) where X is features, y is target
        """
        # Get feature columns
        feature_cols = self.get_feature_columns(df)

        # Remove rows with NaN in features or target
        df_clean = df[feature_cols + ['target']].dropna()

        logger.info(f"Prepared {len(df_clean)} samples with {len(feature_cols)} features")
        logger.info(f"Target distribution: {df_clean['target'].value_counts().to_dict()}")

        X = df_clean[feature_cols].values
        y = df_clean['target'].values

        return X, y, feature_cols


if __name__ == "__main__":
    # Example usage
    from ..data.loader import DataLoader

    loader = DataLoader()
    df = loader.load_stock_data('RELIANCE.NS')

    if df is not None:
        engineer = FeatureEngineer()

        # Create features
        df_with_features = engineer.create_all_features(df)

        print(f"\nCreated {len(df_with_features.columns)} columns")
        print(f"Features: {engineer.get_feature_columns(df_with_features)[:10]}...")

        # Prepare ML data
        X, y, feature_names = engineer.prepare_ml_data(df_with_features)

        print(f"\nML Data:")
        print(f"X shape: {X.shape}")
        print(f"y shape: {y.shape}")
        print(f"Positive samples: {y.sum()} ({y.mean():.1%})")
