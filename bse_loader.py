"""
BSE Data Loader - Official BSE BhavCopy
Fetches from BSE India using UDiFF and Legacy formats
"""

import io
import os
import time
import zipfile
import warnings
import pickle
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import requests

warnings.filterwarnings("ignore")


class BSEDataFetcher:
    """
    Fetch stock data from BSE India
    Uses official BhavCopy data (UDiFF CSV + Legacy ZIP fallback)
    """

    def __init__(self, cache_dir: str = "./stock_picker_data/cache/bse_data"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # BSE URLs
        self.BSE_UDIFF_URL = "https://www.bseindia.com/download/BhavCopy/Equity/BhavCopy_BSE_CM_0_0_0_{ymd}_F_0000.CSV"
        self.BSE_LEGACY_URL = "https://www.bseindia.com/download/BhavCopy/Equity/EQ{ddmmyy}_CSV.ZIP"

        # Request settings
        self.REQUEST_TIMEOUT = 12
        self.RETRY_TIMES = 3
        self.SLEEP_BETWEEN = 0.75

    @staticmethod
    def ymd(d: date) -> str:
        """Format: 20250131"""
        return d.strftime("%Y%m%d")

    @staticmethod
    def ddmmyy(d: date) -> str:
        """Format: 310125"""
        return d.strftime("%d%m%y")

    @staticmethod
    def is_weekend(d: date) -> bool:
        return d.weekday() >= 5

    @staticmethod
    def prev_bday(d: date) -> date:
        """Get previous business day"""
        x = d
        while BSEDataFetcher.is_weekend(x):
            x -= timedelta(days=1)
        return x

    def safe_get(self, url: str) -> Optional[requests.Response]:
        """Safe HTTP GET with retries"""
        err = None
        for attempt in range(self.RETRY_TIMES):
            try:
                r = requests.get(
                    url,
                    timeout=self.REQUEST_TIMEOUT,
                    headers={"User-Agent": "Mozilla/5.0"}
                )
                if r.ok and r.content:
                    return r
            except Exception as e:
                err = e
            time.sleep(self.SLEEP_BETWEEN)

        if err:
            print(f"⚠️ GET failed: {url} | {err}")
        return None

    def normalize_bse_bhav(self, df: pd.DataFrame, target_date: date) -> pd.DataFrame:
        """Normalize BSE BhavCopy to canonical format"""
        # BSE column mappings
        bse_map = {
            # UDiFF format
            'TckrSymb': 'SC_NAME',
            'ISIN': 'ISIN',
            'FinInstrmId': 'SC_CODE',
            'OpnPric': 'Open',
            'HghPric': 'High',
            'LwPric': 'Low',
            'ClsPric': 'Close',
            'TtlTradgVol': 'Volume',
            'TtlTrfVal': 'ValueTraded',
            'DATE': 'DATE',
            # Legacy format
            'SC_CODE': 'SC_CODE',
            'SC_NAME': 'SC_NAME',
            'OPEN': 'Open',
            'HIGH': 'High',
            'LOW': 'Low',
            'CLOSE': 'Close',
            'NO_OF_SHRS': 'Volume',
            'NET_TURNOV': 'ValueTraded'
        }

        out = pd.DataFrame()
        for src, tgt in bse_map.items():
            if src in df.columns:
                out[tgt] = df[src].copy()

        # Handle SC_CODE
        if 'SC_CODE' not in out and 'ISIN' in out:
            out['SC_CODE'] = out['ISIN']
        if 'SC_NAME' not in out and 'TckrSymb' in df.columns:
            out['SC_NAME'] = df['TckrSymb']

        # Numeric conversions
        for c in ['Open', 'High', 'Low', 'Close', 'Volume', 'ValueTraded']:
            if c in out.columns:
                out[c] = pd.to_numeric(out[c], errors='coerce')

        # Set date
        out['DATE'] = pd.to_datetime(target_date).date()

        # Required columns
        required = ['SC_CODE', 'SC_NAME', 'Open', 'High', 'Low', 'Close', 'Volume', 'ValueTraded', 'DATE']

        # Drop rows with NaN
        out = out.dropna(subset=['Close', 'High', 'Low', 'Open'])
        out['SC_CODE'] = out['SC_CODE'].astype(str)

        return out[required]

    def fetch_bse_bhav_for(self, d: date) -> Optional[pd.DataFrame]:
        """Fetch BSE BhavCopy for a specific date"""
        # Try UDiFF CSV first
        url = self.BSE_UDIFF_URL.format(ymd=self.ymd(d))
        r = self.safe_get(url)
        if r and r.ok:
            try:
                df = pd.read_csv(io.BytesIO(r.content))
                normalized = self.normalize_bse_bhav(df, d)
                print(f"✅ BSE (UDiFF): {d} → {len(normalized)} stocks")
                return normalized
            except Exception as e:
                print(f"⚠️ BSE UDiFF parse failed {d}: {e}")

        # Fallback to legacy ZIP
        url = self.BSE_LEGACY_URL.format(ddmmyy=self.ddmmyy(d))
        r = self.safe_get(url)
        if r and r.ok:
            try:
                with zipfile.ZipFile(io.BytesIO(r.content)) as zf:
                    csv_name = [n for n in zf.namelist() if n.lower().endswith('.csv')][0]
                    with zf.open(csv_name) as f:
                        df = pd.read_csv(f)
                normalized = self.normalize_bse_bhav(df, d)
                print(f"✅ BSE (Legacy): {d} → {len(normalized)} stocks")
                return normalized
            except Exception as e:
                print(f"⚠️ BSE legacy parse failed {d}: {e}")

        return None

    def fetch_bhav_for(self, d: date) -> Optional[pd.DataFrame]:
        """
        Fetch BhavCopy for a date from BSE
        """
        # Skip weekends
        if self.is_weekend(d):
            return None

        # Fetch from BSE
        df_bse = self.fetch_bse_bhav_for(d)
        if df_bse is not None and len(df_bse) > 0:
            df_bse['Source'] = 'BSE'
            return df_bse

        print(f"❌ BSE data not available for {d}")
        return None

    def fetch_bhav_range(self, start_date: date, end_date: date) -> pd.DataFrame:
        """
        Fetch BhavCopy data for a date range with caching
        """
        # Check cache first
        cache_key = f"bhav_bse_{self.ymd(start_date)}_{self.ymd(end_date)}.pkl"
        cache_file = self.cache_dir / cache_key

        if cache_file.exists():
            print(f"✅ Loading from cache: {cache_key}")
            with open(cache_file, 'rb') as f:
                return pickle.load(f)

        # Fetch fresh data
        print(f"📥 Fetching BSE data: {start_date} → {end_date}")
        got = []
        cur = start_date

        while cur <= end_date:
            df = self.fetch_bhav_for(cur)
            if df is not None and len(df) > 0:
                got.append(df)
            cur += timedelta(days=1)

        if not got:
            raise SystemExit("❌ No BhavCopy data fetched from BSE")

        # Combine all
        result = pd.concat(got, ignore_index=True)

        # Cache it
        print(f"💾 Caching to: {cache_key}")
        with open(cache_file, 'wb') as f:
            pickle.dump(result, f, protocol=pickle.HIGHEST_PROTOCOL)

        print(f"✅ Total rows: {len(result):,} | Dates: {result['DATE'].min()} → {result['DATE'].max()}")
        return result

    def get_stock_universe(self, bhav_df: pd.DataFrame, min_days: int = 200) -> list:
        """
        Extract stock universe from BhavCopy data
        Returns stocks that have at least min_days of data
        """
        stock_counts = bhav_df.groupby('SC_CODE').size()
        qualified = stock_counts[stock_counts >= min_days].index.tolist()
        print(f"📊 Stock universe: {len(qualified)} stocks with ≥{min_days} days of data")
        return qualified


# Quick test
if __name__ == "__main__":
    fetcher = BSEDataFetcher()

    # Test: fetch last 5 business days
    end_d = fetcher.prev_bday(date.today())
    start_d = end_d - timedelta(days=7)

    print(f"Testing BSE fetcher for {start_d} to {end_d}")
    df = fetcher.fetch_bhav_range(start_d, end_d)

    print(f"\nResult:")
    print(f"Rows: {len(df):,}")
    print(f"Unique stocks: {df['SC_CODE'].nunique()}")
    print(f"Date range: {df['DATE'].min()} → {df['DATE'].max()}")
    print(f"\nSample:")
    print(df.head(10))

    # Check source
    if 'Source' in df.columns:
        print(f"\nData source:")
        print(df['Source'].value_counts())
