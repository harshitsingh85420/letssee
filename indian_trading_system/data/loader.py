"""
Data loader module for Indian equity markets.
Handles data collection from Yahoo Finance with caching using Parquet files.
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import time

import pandas as pd
import numpy as np
import yfinance as yf
from tqdm import tqdm

from ..utils.constants import (
    DATA_CACHE_DIR, DATA_START_DATE, MAX_RETRIES, RETRY_DELAY,
    NIFTY_50_SYMBOLS, TOP_10_NIFTY
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataLoader:
    """
    Data loader for Indian equity markets with caching support.
    """

    def __init__(self, cache_dir: str = DATA_CACHE_DIR):
        """
        Initialize data loader.

        Args:
            cache_dir: Directory for storing cached Parquet files
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized DataLoader with cache directory: {self.cache_dir}")

    def _get_cache_path(self, symbol: str) -> Path:
        """Get cache file path for a symbol."""
        clean_symbol = symbol.replace('.NS', '').replace('.BO', '')
        return self.cache_dir / f"{clean_symbol}.parquet"

    def _download_with_retry(self, symbol: str, start_date: str,
                            end_date: Optional[str] = None) -> Optional[pd.DataFrame]:
        """
        Download data with retry mechanism.

        Args:
            symbol: Stock symbol (with .NS suffix)
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format (default: today)

        Returns:
            DataFrame with OHLCV data or None if failed
        """
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')

        for attempt in range(MAX_RETRIES):
            try:
                logger.info(f"Downloading {symbol} (attempt {attempt + 1}/{MAX_RETRIES})")
                ticker = yf.Ticker(symbol)
                df = ticker.history(start=start_date, end=end_date, auto_adjust=True)

                if df.empty:
                    logger.warning(f"No data returned for {symbol}")
                    return None

                # Rename columns to lowercase
                df.columns = [col.lower() for col in df.columns]

                # Add symbol column
                df['symbol'] = symbol

                # Reset index to make date a column
                df = df.reset_index()
                df.columns = [col.lower() for col in df.columns]

                logger.info(f"Successfully downloaded {len(df)} rows for {symbol}")
                return df

            except Exception as e:
                logger.error(f"Error downloading {symbol}: {e}")
                if attempt < MAX_RETRIES - 1:
                    sleep_time = RETRY_DELAY * (2 ** attempt)  # Exponential backoff
                    logger.info(f"Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)
                else:
                    logger.error(f"Failed to download {symbol} after {MAX_RETRIES} attempts")
                    return None

        return None

    def _load_from_cache(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        Load data from cache.

        Args:
            symbol: Stock symbol

        Returns:
            Cached DataFrame or None if not found
        """
        cache_path = self._get_cache_path(symbol)

        if not cache_path.exists():
            return None

        try:
            df = pd.read_parquet(cache_path)
            logger.info(f"Loaded {len(df)} rows from cache for {symbol}")
            return df
        except Exception as e:
            logger.error(f"Error loading cache for {symbol}: {e}")
            return None

    def _save_to_cache(self, symbol: str, df: pd.DataFrame) -> bool:
        """
        Save data to cache.

        Args:
            symbol: Stock symbol
            df: DataFrame to cache

        Returns:
            True if successful, False otherwise
        """
        cache_path = self._get_cache_path(symbol)

        try:
            df.to_parquet(cache_path, index=False)
            logger.info(f"Saved {len(df)} rows to cache for {symbol}")
            return True
        except Exception as e:
            logger.error(f"Error saving cache for {symbol}: {e}")
            return False

    def _needs_update(self, df: pd.DataFrame) -> bool:
        """
        Check if cached data needs update.

        Args:
            df: Cached DataFrame

        Returns:
            True if update needed, False otherwise
        """
        if df is None or df.empty:
            return True

        # Get last date in cache
        last_date = pd.to_datetime(df['date']).max()

        # Check if last date is before yesterday (account for market holidays)
        yesterday = datetime.now() - timedelta(days=1)

        if last_date.date() < yesterday.date():
            logger.info(f"Cache outdated: last date {last_date.date()}, yesterday {yesterday.date()}")
            return True

        return False

    def load_stock_data(self, symbol: str, start_date: str = DATA_START_DATE,
                       end_date: Optional[str] = None,
                       force_download: bool = False) -> Optional[pd.DataFrame]:
        """
        Load stock data with caching.

        Args:
            symbol: Stock symbol (with .NS suffix)
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format (default: today)
            force_download: Force download even if cache exists

        Returns:
            DataFrame with OHLCV data or None if failed
        """
        # Try loading from cache first
        if not force_download:
            cached_df = self._load_from_cache(symbol)

            if cached_df is not None:
                # Check if needs update
                if not self._needs_update(cached_df):
                    return cached_df

                # Update with new data
                last_date = pd.to_datetime(cached_df['date']).max()
                update_start = (last_date + timedelta(days=1)).strftime('%Y-%m-%d')

                logger.info(f"Updating {symbol} from {update_start}")
                new_data = self._download_with_retry(symbol, update_start, end_date)

                if new_data is not None and not new_data.empty:
                    # Combine old and new data
                    combined_df = pd.concat([cached_df, new_data], ignore_index=True)
                    combined_df = combined_df.drop_duplicates(subset=['date'], keep='last')
                    combined_df = combined_df.sort_values('date').reset_index(drop=True)

                    # Save to cache
                    self._save_to_cache(symbol, combined_df)
                    return combined_df
                else:
                    # No new data, return cached
                    return cached_df

        # Download fresh data
        df = self._download_with_retry(symbol, start_date, end_date)

        if df is not None:
            self._save_to_cache(symbol, df)

        return df

    def load_multiple_stocks(self, symbols: List[str],
                           start_date: str = DATA_START_DATE,
                           end_date: Optional[str] = None,
                           force_download: bool = False) -> Dict[str, pd.DataFrame]:
        """
        Load data for multiple stocks.

        Args:
            symbols: List of stock symbols
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format (default: today)
            force_download: Force download even if cache exists

        Returns:
            Dictionary mapping symbols to DataFrames
        """
        data_dict = {}

        for symbol in tqdm(symbols, desc="Loading stocks"):
            df = self.load_stock_data(symbol, start_date, end_date, force_download)
            if df is not None:
                data_dict[symbol] = df

            # Small delay to avoid rate limiting
            time.sleep(0.1)

        logger.info(f"Successfully loaded {len(data_dict)}/{len(symbols)} stocks")
        return data_dict

    def load_nifty_50(self, start_date: str = DATA_START_DATE,
                     end_date: Optional[str] = None,
                     force_download: bool = False) -> Dict[str, pd.DataFrame]:
        """
        Load all NIFTY 50 stocks.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format (default: today)
            force_download: Force download even if cache exists

        Returns:
            Dictionary mapping symbols to DataFrames
        """
        return self.load_multiple_stocks(NIFTY_50_SYMBOLS, start_date,
                                        end_date, force_download)

    def load_top_10_nifty(self, start_date: str = DATA_START_DATE,
                         end_date: Optional[str] = None,
                         force_download: bool = False) -> Dict[str, pd.DataFrame]:
        """
        Load top 10 NIFTY stocks for testing.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format (default: today)
            force_download: Force download even if cache exists

        Returns:
            Dictionary mapping symbols to DataFrames
        """
        return self.load_multiple_stocks(TOP_10_NIFTY, start_date,
                                        end_date, force_download)

    def get_latest_prices(self, symbols: List[str]) -> Dict[str, float]:
        """
        Get latest prices for multiple stocks.

        Args:
            symbols: List of stock symbols

        Returns:
            Dictionary mapping symbols to latest prices
        """
        prices = {}

        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period='1d')
                if not data.empty:
                    prices[symbol] = data['Close'].iloc[-1]
            except Exception as e:
                logger.error(f"Error getting price for {symbol}: {e}")

        return prices

    def clear_cache(self, symbol: Optional[str] = None):
        """
        Clear cache for a symbol or all symbols.

        Args:
            symbol: Stock symbol (None to clear all)
        """
        if symbol:
            cache_path = self._get_cache_path(symbol)
            if cache_path.exists():
                cache_path.unlink()
                logger.info(f"Cleared cache for {symbol}")
        else:
            for cache_file in self.cache_dir.glob("*.parquet"):
                cache_file.unlink()
            logger.info("Cleared all cache files")


if __name__ == "__main__":
    # Example usage
    loader = DataLoader()

    # Load top 10 NIFTY stocks
    print("Loading top 10 NIFTY stocks...")
    data = loader.load_top_10_nifty()

    print(f"\nLoaded {len(data)} stocks")
    for symbol, df in data.items():
        print(f"{symbol}: {len(df)} days of data, from {df['date'].min()} to {df['date'].max()}")
