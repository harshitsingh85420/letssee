"""
BSE (Bombay Stock Exchange) data loader with official BhavCopy data.
Fetches from official BSE website, calculates indicators, and caches everything.
"""

import io
import zipfile
import pickle
from datetime import date, datetime, timedelta
from typing import Optional, Dict, List
from pathlib import Path
import logging

import pandas as pd
import numpy as np
import requests
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# BSE BhavCopy URLs
UDIFF_URL = "https://www.bseindia.com/download/BhavCopy/Equity/BhavCopy_BSE_CM_0_0_0_{ymd}_F_0000.CSV"
LEGACY_URL = "https://www.bseindia.com/download/BhavCopy/Equity/EQ{ddmmyy}_CSV.ZIP"

# Column mapping for normalization
CANON = {
    # UDiFF format -> canonical names
    "TckrSymb": "SC_NAME",
    "ISIN": "ISIN",
    "FinInstrmId": "SC_CODE",
    "OpnPric": "Open",
    "HghPric": "High",
    "LwPric": "Low",
    "ClsPric": "Close",
    "TtlTradgVol": "Volume",
    "TtlTrfVal": "ValueTraded",
    "DATE": "DATE",
    # Legacy format -> canonical names
    "SC_CODE": "SC_CODE",
    "SC_NAME": "SC_NAME",
    "OPEN": "Open",
    "HIGH": "High",
    "LOW": "Low",
    "CLOSE": "Close",
    "NO_OF_SHRS": "Volume",
    "NET_TURNOV": "ValueTraded"
}

REQUIRED_COLS = ["SC_CODE", "SC_NAME", "Open", "High", "Low", "Close", "Volume", "ValueTraded", "DATE"]


class BSEDataLoader:
    """
    BSE data loader with automatic indicator calculation and caching.
    """

    def __init__(self, cache_dir: str = "data/storage/bse_cache"):
        """
        Initialize BSE data loader.

        Args:
            cache_dir: Directory for caching data
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        logger.info(f"Initialized BSE loader with cache: {self.cache_dir}")

    @staticmethod
    def ymd(d: date) -> str:
        """Format date as YYYYMMDD."""
        return d.strftime("%Y%m%d")

    @staticmethod
    def ddmmyy(d: date) -> str:
        """Format date as DDMMYY."""
        return d.strftime("%d%m%y")

    @staticmethod
    def is_weekend(d: date) -> bool:
        """Check if date is weekend."""
        return d.weekday() >= 5

    def safe_get(self, url: str, timeout: int = 10) -> Optional[requests.Response]:
        """
        Safe HTTP GET with error handling.

        Args:
            url: URL to fetch
            timeout: Request timeout

        Returns:
            Response or None
        """
        try:
            response = self.session.get(url, timeout=timeout)
            return response if response.ok else None
        except Exception as e:
            logger.debug(f"Request failed: {e}")
            return None

    def normalize_bhav(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize BhavCopy data to standard format.

        Args:
            df: Raw BhavCopy DataFrame

        Returns:
            Normalized DataFrame
        """
        out = pd.DataFrame()

        # Map columns
        for src, tgt in CANON.items():
            if src in df.columns:
                out[tgt] = df[src].copy()

        # Handle missing SC_CODE/SC_NAME
        if "SC_CODE" not in out and "ISIN" in out:
            out["SC_CODE"] = out["ISIN"]
        if "SC_NAME" not in out and "TckrSymb" in df.columns:
            out["SC_NAME"] = df["TckrSymb"]

        # Convert numeric columns
        for c in ["Open", "High", "Low", "Close", "Volume", "ValueTraded"]:
            if c in out:
                out[c] = pd.to_numeric(out[c], errors="coerce")

        # Convert date
        if "DATE" in out:
            out["DATE"] = pd.to_datetime(out["DATE"]).dt.date

        # Check required columns
        missing = [c for c in REQUIRED_COLS if c not in out.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        # Clean data
        out = out.dropna(subset=["Close", "High", "Low", "Open"])
        out["SC_CODE"] = out["SC_CODE"].astype(str)

        return out[REQUIRED_COLS]

    def fetch_bhav_for_date(self, d: date) -> Optional[pd.DataFrame]:
        """
        Fetch BhavCopy for a specific date.

        Args:
            d: Date to fetch

        Returns:
            DataFrame or None
        """
        # Try UDiFF CSV first
        url = UDIFF_URL.format(ymd=self.ymd(d))
        response = self.safe_get(url)

        if response and response.ok:
            try:
                df = pd.read_csv(io.BytesIO(response.content))
                df["DATE"] = pd.to_datetime(d).date()
                return self.normalize_bhav(df)
            except Exception as e:
                logger.debug(f"UDiFF parse failed for {d}: {e}")

        # Fallback to legacy ZIP
        url = LEGACY_URL.format(ddmmyy=self.ddmmyy(d))
        response = self.safe_get(url)

        if response and response.ok:
            try:
                with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
                    csv_name = [n for n in zf.namelist() if n.lower().endswith(".csv")][0]
                    with zf.open(csv_name) as f:
                        df = pd.read_csv(f)

                df["DATE"] = pd.to_datetime(d).date()
                return self.normalize_bhav(df)
            except Exception as e:
                logger.debug(f"Legacy parse failed for {d}: {e}")

        logger.debug(f"No data available for {d}")
        return None

    def fetch_bhav_range(self, start_date: date, end_date: date) -> pd.DataFrame:
        """
        Fetch BhavCopy data for a date range.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            Combined DataFrame
        """
        data_frames = []
        current = start_date

        logger.info(f"Fetching BSE data from {start_date} to {end_date}")

        while current <= end_date:
            if not self.is_weekend(current):
                df = self.fetch_bhav_for_date(current)
                if df is not None and len(df) > 0:
                    logger.info(f"  {current}: {len(df)} stocks")
                    data_frames.append(df)
            current += timedelta(days=1)

        if not data_frames:
            raise ValueError("No BhavCopy data fetched")

        combined = pd.concat(data_frames, ignore_index=True)
        logger.info(f"Total: {len(combined)} records")

        return combined

    def get_stock_data(self, sc_code: str, start_date: date, end_date: date) -> pd.DataFrame:
        """
        Get data for a specific stock.

        Args:
            sc_code: BSE stock code
            start_date: Start date
            end_date: End date

        Returns:
            Stock DataFrame
        """
        # Check cache first
        cache_file = self.cache_dir / f"{sc_code}_{self.ymd(start_date)}_{self.ymd(end_date)}.pkl"

        if cache_file.exists():
            logger.info(f"Loading {sc_code} from cache")
            with open(cache_file, 'rb') as f:
                return pickle.load(f)

        # Fetch data
        full_data = self.fetch_bhav_range(start_date, end_date)

        # Filter for specific stock
        stock_data = full_data[full_data['SC_CODE'] == str(sc_code)].copy()

        if stock_data.empty:
            raise ValueError(f"No data found for stock code: {sc_code}")

        # Sort by date
        stock_data = stock_data.sort_values('DATE').reset_index(drop=True)

        # Rename columns to match our system
        stock_data = stock_data.rename(columns={
            'DATE': 'date',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        })

        # Add symbol column
        stock_data['symbol'] = stock_data['SC_NAME'].iloc[0]

        # Cache it
        with open(cache_file, 'wb') as f:
            pickle.dump(stock_data, f)

        logger.info(f"Cached {len(stock_data)} days for {sc_code}")

        return stock_data

    def calculate_and_cache_indicators(self, df: pd.DataFrame, sc_code: str) -> pd.DataFrame:
        """
        Calculate all indicators and cache the result.

        Args:
            df: Stock DataFrame
            sc_code: Stock code

        Returns:
            DataFrame with indicators
        """
        cache_file = self.cache_dir / f"{sc_code}_indicators.pkl"

        # Check if indicators already calculated
        if cache_file.exists():
            cache_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
            if (datetime.now() - cache_time).days < 1:  # Cache valid for 1 day
                logger.info(f"Loading pre-calculated indicators for {sc_code}")
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)

        logger.info(f"Calculating indicators for {sc_code}...")

        # Import indicator modules
        from ..indicators.technical import TechnicalIndicators
        from ..indicators.volatility import VolatilityEstimators
        from ..indicators.patterns import CandlestickPatterns

        # Calculate indicators
        technical = TechnicalIndicators()
        volatility = VolatilityEstimators()
        patterns = CandlestickPatterns()

        df_with_indicators = technical.calculate_all(df)
        df_with_indicators = volatility.calculate_all(df_with_indicators)
        df_with_indicators = patterns.detect_all_patterns(df_with_indicators)
        df_with_indicators = patterns.calculate_pattern_strength(df_with_indicators)

        # Cache indicators
        with open(cache_file, 'wb') as f:
            pickle.dump(df_with_indicators, f)

        logger.info(f"Cached indicators for {sc_code}")

        return df_with_indicators

    def get_nifty_50_codes(self) -> Dict[str, str]:
        """
        Get BSE codes for NIFTY 50 stocks.

        Returns:
            Dictionary mapping NSE symbol to BSE code
        """
        # Mapping of NSE symbols to BSE codes
        return {
            'RELIANCE': '500325',
            'TCS': '532540',
            'HDFCBANK': '500180',
            'INFY': '500209',
            'ICICIBANK': '532174',
            'HINDUNILVR': '500696',
            'ITC': '500875',
            'SBIN': '500112',
            'BHARTIARTL': '532454',
            'KOTAKBANK': '500247',
            'BAJFINANCE': '500034',
            'LT': '500510',
            'ASIANPAINT': '500820',
            'AXISBANK': '532215',
            'MARUTI': '532500',
            'SUNPHARMA': '524715',
            'TITAN': '500114',
            'ULTRACEMCO': '532538',
            'NESTLEIND': '500790',
            'WIPRO': '507685',
            'HCLTECH': '532281',
            'TECHM': '532755',
            'NTPC': '532555',
            'ONGC': '500312',
            'POWERGRID': '532898',
            'M&M': '500520',
            'TATAMOTORS': '500570',
            'COALINDIA': '533278',
            'TATASTEEL': '500470',
            'BAJAJFINSV': '532978'
        }

    def load_nifty_50_data(self, start_date: date, end_date: date) -> Dict[str, pd.DataFrame]:
        """
        Load data for NIFTY 50 stocks with pre-calculated indicators.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            Dictionary mapping symbols to DataFrames with indicators
        """
        nifty_codes = self.get_nifty_50_codes()
        result = {}

        for symbol, code in tqdm(nifty_codes.items(), desc="Loading NIFTY 50"):
            try:
                # Get stock data
                df = self.get_stock_data(code, start_date, end_date)

                # Calculate indicators (or load from cache)
                df_with_indicators = self.calculate_and_cache_indicators(df, code)

                result[symbol] = df_with_indicators
                logger.info(f"  ✓ {symbol} ({code}): {len(df)} days")

            except Exception as e:
                logger.error(f"  ✗ {symbol} ({code}): {e}")

        return result

    def clear_cache(self, older_than_days: int = 7):
        """
        Clear old cache files.

        Args:
            older_than_days: Remove files older than this many days
        """
        cutoff = datetime.now() - timedelta(days=older_than_days)
        removed = 0

        for cache_file in self.cache_dir.glob("*.pkl"):
            if datetime.fromtimestamp(cache_file.stat().st_mtime) < cutoff:
                cache_file.unlink()
                removed += 1

        logger.info(f"Removed {removed} old cache files")


if __name__ == "__main__":
    # Example usage
    loader = BSEDataLoader()

    # Fetch data for a specific stock
    start = date(2024, 1, 1)
    end = date.today()

    # Reliance Industries (BSE code: 500325)
    print("\nFetching Reliance data from BSE...")
    df = loader.get_stock_data('500325', start, end)

    print(f"\nData shape: {df.shape}")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    print("\nRecent data:")
    print(df[['date', 'open', 'high', 'low', 'close', 'volume']].tail())

    # Calculate indicators
    print("\nCalculating indicators...")
    df_with_indicators = loader.calculate_and_cache_indicators(df, '500325')

    print(f"\nTotal columns: {len(df_with_indicators.columns)}")
    print(f"Indicator columns: {[c for c in df_with_indicators.columns if c not in ['date', 'open', 'high', 'low', 'close', 'volume', 'symbol']][:10]}...")

    # Load NIFTY 50 (top 5 for demo)
    print("\n\nLoading top 5 NIFTY stocks...")
    nifty_data = {}
    for symbol, code in list(loader.get_nifty_50_codes().items())[:5]:
        try:
            df = loader.get_stock_data(code, start, end)
            df_ind = loader.calculate_and_cache_indicators(df, code)
            nifty_data[symbol] = df_ind
            print(f"  ✓ {symbol}: {len(df)} days")
        except Exception as e:
            print(f"  ✗ {symbol}: {e}")

    print(f"\nTotal stocks loaded: {len(nifty_data)}")
