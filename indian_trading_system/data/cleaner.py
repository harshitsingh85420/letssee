"""
Data cleaning and validation module for Indian equity markets.
"""

import logging
from typing import Dict, List, Optional
import pandas as pd
import numpy as np

from ..utils.constants import MIN_DAILY_VOLUME

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataCleaner:
    """
    Data cleaning and validation for stock market data.
    """

    def __init__(self, min_daily_volume: float = MIN_DAILY_VOLUME):
        """
        Initialize data cleaner.

        Args:
            min_daily_volume: Minimum daily volume threshold
        """
        self.min_daily_volume = min_daily_volume

    def validate_ohlcv(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate OHLCV data for consistency.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            Cleaned DataFrame
        """
        if df.empty:
            return df

        df = df.copy()
        initial_rows = len(df)

        # Ensure date is datetime
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])

        # Check for required columns
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        missing_cols = [col for col in required_cols if col not in df.columns]

        if missing_cols:
            logger.error(f"Missing required columns: {missing_cols}")
            return pd.DataFrame()

        # Remove rows with NaN values
        df = df.dropna(subset=required_cols)

        # Remove rows with zero or negative prices
        price_cols = ['open', 'high', 'low', 'close']
        df = df[(df[price_cols] > 0).all(axis=1)]

        # Validate OHLC relationships
        # High should be >= Open, Close, Low
        df = df[df['high'] >= df['open']]
        df = df[df['high'] >= df['close']]
        df = df[df['high'] >= df['low']]

        # Low should be <= Open, Close, High
        df = df[df['low'] <= df['open']]
        df = df[df['low'] <= df['close']]
        df = df[df['low'] <= df['high']]

        # Remove rows with zero volume
        df = df[df['volume'] > 0]

        # Check for outliers using price changes
        df = self._remove_price_outliers(df)

        # Sort by date
        df = df.sort_values('date').reset_index(drop=True)

        rows_removed = initial_rows - len(df)
        if rows_removed > 0:
            logger.info(f"Removed {rows_removed} invalid rows ({rows_removed/initial_rows*100:.2f}%)")

        return df

    def _remove_price_outliers(self, df: pd.DataFrame, threshold: float = 10.0) -> pd.DataFrame:
        """
        Remove outliers based on extreme price changes.

        Args:
            df: DataFrame with price data
            threshold: Maximum allowed price change (as multiple of std dev)

        Returns:
            Cleaned DataFrame
        """
        if len(df) < 2:
            return df

        df = df.copy()

        # Calculate daily returns
        df['returns'] = df['close'].pct_change()

        # Calculate z-scores
        mean_return = df['returns'].mean()
        std_return = df['returns'].std()

        if std_return > 0:
            df['z_score'] = np.abs((df['returns'] - mean_return) / std_return)

            # Remove extreme outliers
            initial_len = len(df)
            df = df[df['z_score'] <= threshold]

            removed = initial_len - len(df)
            if removed > 0:
                logger.info(f"Removed {removed} outlier rows based on price changes")

        # Drop temporary columns
        df = df.drop(columns=['returns', 'z_score'], errors='ignore')

        return df

    def filter_by_liquidity(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter stocks by liquidity requirements.

        Args:
            df: DataFrame with price and volume data

        Returns:
            Filtered DataFrame
        """
        if df.empty or 'volume' not in df.columns or 'close' not in df.columns:
            return df

        df = df.copy()

        # Calculate average daily volume in rupees
        df['daily_value'] = df['close'] * df['volume']

        # Calculate rolling average (20 days)
        df['avg_daily_value'] = df['daily_value'].rolling(window=20, min_periods=1).mean()

        # Filter by minimum daily value
        initial_len = len(df)
        df = df[df['avg_daily_value'] >= self.min_daily_volume]

        removed = initial_len - len(df)
        if removed > 0:
            logger.info(f"Removed {removed} rows due to low liquidity")

        # Drop temporary columns
        df = df.drop(columns=['daily_value', 'avg_daily_value'], errors='ignore')

        return df

    def handle_corporate_actions(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle corporate actions (splits, bonuses).

        Args:
            df: DataFrame with price data

        Returns:
            Adjusted DataFrame
        """
        if df.empty or len(df) < 2:
            return df

        df = df.copy()

        # Detect potential splits/bonuses by looking for large price jumps
        df['price_ratio'] = df['close'] / df['close'].shift(1)

        # Common split ratios: 2:1, 5:1, 10:1, etc.
        common_ratios = [0.5, 0.2, 0.1, 2.0, 5.0, 10.0]

        for idx, row in df.iterrows():
            if pd.notna(row['price_ratio']):
                # Check if ratio is close to a common split ratio
                for ratio in common_ratios:
                    if abs(row['price_ratio'] - ratio) < 0.05:
                        logger.warning(f"Potential corporate action detected at {row['date']}: "
                                     f"price ratio {row['price_ratio']:.2f}")

        # Drop temporary column
        df = df.drop(columns=['price_ratio'], errors='ignore')

        return df

    def fill_missing_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Fill missing dates (market holidays) with forward fill.

        Args:
            df: DataFrame with date column

        Returns:
            DataFrame with filled dates
        """
        if df.empty or 'date' not in df.columns:
            return df

        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])

        # Create date range
        date_range = pd.date_range(start=df['date'].min(), end=df['date'].max(), freq='D')

        # Reindex to include all dates
        df = df.set_index('date').reindex(date_range)

        # Forward fill for missing dates (market holidays)
        price_cols = ['open', 'high', 'low', 'close']
        df[price_cols] = df[price_cols].fillna(method='ffill')

        # Set volume to 0 for missing dates
        df['volume'] = df['volume'].fillna(0)

        # Reset index
        df = df.reset_index()
        df = df.rename(columns={'index': 'date'})

        return df

    def clean_stock_data(self, df: pd.DataFrame,
                        validate: bool = True,
                        filter_liquidity: bool = False,
                        handle_corp_actions: bool = True) -> pd.DataFrame:
        """
        Apply all cleaning steps to stock data.

        Args:
            df: DataFrame with raw stock data
            validate: Whether to validate OHLCV data
            filter_liquidity: Whether to filter by liquidity
            handle_corp_actions: Whether to check for corporate actions

        Returns:
            Cleaned DataFrame
        """
        if df.empty:
            return df

        logger.info(f"Cleaning data: initial rows = {len(df)}")

        # Validate OHLCV
        if validate:
            df = self.validate_ohlcv(df)

        # Filter by liquidity
        if filter_liquidity:
            df = self.filter_by_liquidity(df)

        # Check corporate actions
        if handle_corp_actions:
            df = self.handle_corporate_actions(df)

        logger.info(f"Cleaning complete: final rows = {len(df)}")

        return df

    def clean_multiple_stocks(self, data_dict: Dict[str, pd.DataFrame],
                            **kwargs) -> Dict[str, pd.DataFrame]:
        """
        Clean data for multiple stocks.

        Args:
            data_dict: Dictionary mapping symbols to DataFrames
            **kwargs: Arguments to pass to clean_stock_data

        Returns:
            Dictionary with cleaned DataFrames
        """
        cleaned_dict = {}

        for symbol, df in data_dict.items():
            logger.info(f"\nCleaning {symbol}")
            cleaned_df = self.clean_stock_data(df, **kwargs)

            if not cleaned_df.empty:
                cleaned_dict[symbol] = cleaned_df

        logger.info(f"\nCleaned {len(cleaned_dict)}/{len(data_dict)} stocks successfully")

        return cleaned_dict

    def get_data_quality_report(self, df: pd.DataFrame) -> Dict:
        """
        Generate data quality report.

        Args:
            df: DataFrame with stock data

        Returns:
            Dictionary with quality metrics
        """
        if df.empty:
            return {'status': 'empty'}

        report = {
            'total_rows': len(df),
            'date_range': {
                'start': df['date'].min() if 'date' in df.columns else None,
                'end': df['date'].max() if 'date' in df.columns else None,
            },
            'missing_values': df.isnull().sum().to_dict(),
            'price_stats': {
                'mean_close': df['close'].mean() if 'close' in df.columns else None,
                'std_close': df['close'].std() if 'close' in df.columns else None,
                'min_close': df['close'].min() if 'close' in df.columns else None,
                'max_close': df['close'].max() if 'close' in df.columns else None,
            },
            'volume_stats': {
                'mean_volume': df['volume'].mean() if 'volume' in df.columns else None,
                'zero_volume_days': (df['volume'] == 0).sum() if 'volume' in df.columns else None,
            }
        }

        # Calculate average daily returns
        if 'close' in df.columns:
            returns = df['close'].pct_change().dropna()
            report['returns_stats'] = {
                'mean': returns.mean(),
                'std': returns.std(),
                'min': returns.min(),
                'max': returns.max(),
            }

        return report


if __name__ == "__main__":
    # Example usage
    from .loader import DataLoader

    loader = DataLoader()
    cleaner = DataCleaner()

    # Load and clean a stock
    symbol = 'RELIANCE.NS'
    df = loader.load_stock_data(symbol)

    if df is not None:
        print(f"\nOriginal data: {len(df)} rows")

        cleaned_df = cleaner.clean_stock_data(df, filter_liquidity=False)
        print(f"Cleaned data: {len(cleaned_df)} rows")

        report = cleaner.get_data_quality_report(cleaned_df)
        print("\nData Quality Report:")
        for key, value in report.items():
            print(f"{key}: {value}")
