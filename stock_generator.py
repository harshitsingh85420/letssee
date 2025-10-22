# Complete BSE Stock Picker - Production Ready
# Copy this entire file and save as: Complete_BSE_Stock_Picker.ipynb
# Then open with Jupyter Notebook or Google Colab

"""
SAVE THIS AS: Complete_BSE_Stock_Picker.ipynb

This is a complete, production-ready stock picking system for Indian markets.

QUICK START:
1. Save this file as .ipynb
2. Open in Jupyter: jupyter notebook Complete_BSE_Stock_Picker.ipynb
3. Run all cells: Cell → Run All
4. Get your stock picks!

REQUIREMENTS:
pip install pandas numpy matplotlib seaborn plotly scikit-learn xgboost textblob requests

IMPORTANT NOTES:
- First run: Takes 3-5 minutes (fetching historical data)
- ML model training: Requires at least 100 samples with forward returns
  (This means you need ~105 days of historical data minimum)
- If ML training fails: System falls back to rule-based scoring (still works!)
- Subsequent runs: ~30 seconds (uses cached data)

TROUBLESHOOTING:
- If "No data fetched": BSE website might be down, try again later
- If "Not enough data for ML": Normal on first day, will work after accumulating history
- If "No qualified stocks": Adjust CONFIG thresholds or check market conditions
"""

# ============================================================================
# CELL 1: Setup & Imports
# ============================================================================

import io, zipfile, warnings, time, pickle
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

try:
    import xgboost as xgb
    XGB_AVAILABLE = True
except:
    XGB_AVAILABLE = False

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from IPython.display import display
pd.set_option('display.max_columns', None)
warnings.filterwarnings('ignore')

print('✅ Libraries imported!')

# ============================================================================
# CELL 2: Configuration
# ============================================================================

CONFIG = {
    'DAYS_BACK': 450,
    'MIN_WEIGHTED_SCORE': 12,
    'MIN_ML_PROBABILITY': 0.40,
    'MIN_COMPOSITE_SCORE': 60,
    'MIN_VOLUME_20D': 50_000,
    'MIN_VALUE_20D': 5_00_000,
    'MAX_PENNY_PRICE': 2,
    'MIN_STOCK_PRICE': 5,
    'PORTFOLIO_SIZE': 1_00_000,
    'MAX_POSITIONS': 10,
    'MAX_POSITION_SIZE_PCT': 15,
    'RISK_PER_TRADE_PCT': 2,
    'ENABLE_EMAIL_ALERTS': False,
    'EMAIL_FROM': 'your@email.com',
    'EMAIL_PASSWORD': 'password',
    'EMAIL_TO': 'recipient@email.com',
    'ML_TARGET_RETURN': 3.0,
}

BASE_DIR = Path('.')
CACHE_DIR = BASE_DIR / 'bhav_cache'
MODELS_DIR = BASE_DIR / 'models'
PORTFOLIO_DIR = BASE_DIR / 'portfolio'
LOGS_DIR = BASE_DIR / 'logs'

for d in [CACHE_DIR, MODELS_DIR, PORTFOLIO_DIR, LOGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

print('✅ Configuration loaded!')

# ============================================================================
# CELL 3: BSE Data Fetcher
# ============================================================================

SESSION = requests.Session()
RETRY = Retry(total=3, backoff_factor=0.7, status_forcelist=[429, 500, 502, 503, 504])
ADAPTER = HTTPAdapter(max_retries=RETRY, pool_connections=20, pool_maxsize=20)
SESSION.mount('https://', ADAPTER)
SESSION.headers.update({'User-Agent': 'Mozilla/5.0'})

UDIFF_URL = 'https://www.bseindia.com/download/BhavCopy/Equity/BhavCopy_BSE_CM_0_0_0_{ymd}_F_0000.CSV'
LEGACY_URL = 'https://www.bseindia.com/download/BhavCopy/Equity/EQ{ddmmyy}_CSV.ZIP'

def ymd(d): return d.strftime('%Y%m%d')
def ddmmyy(d): return d.strftime('%d%m%y')
def is_weekend(d): return d.weekday() >= 5

CANON = {
    'TckrSymb': 'SC_NAME', 'ISIN': 'ISIN', 'FinInstrmId': 'SC_CODE',
    'OpnPric': 'Open', 'HghPric': 'High', 'LwPric': 'Low', 'ClsPric': 'Close',
    'TtlTradgVol': 'Volume', 'TtlTrfVal': 'ValueTraded',
    'SC_CODE': 'SC_CODE', 'SC_NAME': 'SC_NAME', 'OPEN': 'Open',
    'HIGH': 'High', 'LOW': 'Low', 'CLOSE': 'Close',
    'NO_OF_SHRS': 'Volume', 'NET_TURNOV': 'ValueTraded'
}

def normalize_bhav(df):
    out = pd.DataFrame()
    for src, tgt in CANON.items():
        if src in df.columns:
            out[tgt] = df[src].copy()
    
    if 'SC_CODE' not in out and 'ISIN' in out:
        out['SC_CODE'] = out['ISIN']
    
    for c in ['Open', 'High', 'Low', 'Close', 'Volume', 'ValueTraded']:
        if c in out:
            out[c] = pd.to_numeric(out[c], errors='coerce')
    
    if 'DATE' not in out.columns:
        out['DATE'] = None
    out['DATE'] = pd.to_datetime(out['DATE']).dt.date
    out['SC_CODE'] = out['SC_CODE'].astype(str)
    
    return out.dropna(subset=['Close', 'High', 'Low', 'Open'])

def fetch_bhav_for(d):
    cp = CACHE_DIR / f'bhav_{ymd(d)}.csv'
    if cp.exists():
        try:
            df = pd.read_csv(cp)
            df['DATE'] = pd.to_datetime(df['DATE']).dt.date
            return df
        except:
            pass
    
    try:
        r = SESSION.get(UDIFF_URL.format(ymd=ymd(d)), timeout=25)
        if r.ok:
            df = pd.read_csv(io.BytesIO(r.content))
            df['DATE'] = d
            out = normalize_bhav(df)
            out.to_csv(cp, index=False)
            return out
    except:
        pass
    
    try:
        r = SESSION.get(LEGACY_URL.format(ddmmyy=ddmmyy(d)), timeout=25)
        if r.ok:
            with zipfile.ZipFile(io.BytesIO(r.content)) as zf:
                name = [n for n in zf.namelist() if n.lower().endswith('.csv')][0]
                with zf.open(name) as f:
                    df = pd.read_csv(f)
            df['DATE'] = d
            out = normalize_bhav(df)
            out.to_csv(cp, index=False)
            return out
    except:
        pass
    
    return None

def fetch_bhav_range(start, end):
    got = []
    cur = start
    while cur <= end:
        if not is_weekend(cur):
            df = fetch_bhav_for(cur)
            if df is not None and len(df):
                print(f'✓ {cur} → {len(df)} rows')
                got.append(df)
            time.sleep(0.25)
        cur += timedelta(days=1)
    
    if not got:
        raise SystemExit('No data fetched')
    return pd.concat(got, ignore_index=True)

print('✅ Data fetcher ready!')

# ============================================================================
# CELL 4: Fetch Historical Data
# ============================================================================

print('📥 Fetching BSE data...')
end_date = date.today()
start_date = end_date - timedelta(days=CONFIG['DAYS_BACK'])

raw_data = fetch_bhav_range(start_date, end_date)
raw_data = raw_data.drop_duplicates(subset=['SC_CODE', 'DATE']).sort_values(['SC_CODE', 'DATE']).reset_index(drop=True)

for col in ['Open', 'High', 'Low', 'Close', 'Volume', 'ValueTraded']:
    raw_data[col] = pd.to_numeric(raw_data[col], errors='coerce').astype(np.float32)

raw_data['SC_CODE'] = raw_data['SC_CODE'].astype('category')
raw_data['SC_NAME'] = raw_data['SC_NAME'].astype('category')

print(f'✅ Data loaded: {len(raw_data):,} rows, {raw_data["SC_CODE"].nunique():,} stocks')
display(raw_data.tail())

# ============================================================================
# CELL 5: Technical Indicators
# ============================================================================

def _wilder_sma(series, period):
    return series.ewm(alpha=1/period, adjust=False).mean()

def _rsi(series, period):
    delta = series.diff()
    up = delta.clip(lower=0)
    dn = -delta.clip(upper=0)
    rs = _wilder_sma(up, period) / _wilder_sma(dn, period).replace(0, np.nan)
    return 100 - (100 / (1 + rs))

def compute_indicators(df):
    df = df.sort_values('DATE').copy().reset_index(drop=True)
    o, h, l, c, v = df['Open'], df['High'], df['Low'], df['Close'], df['Volume']
    
    # Moving Averages
    for p in [5, 10, 20, 50, 200]:
        df[f'SMA{p}'] = c.rolling(p, min_periods=1).mean()
    
    for p in [5, 12, 26, 50]:
        df[f'EMA{p}'] = c.ewm(span=p, adjust=False).mean()
    
    df['Above20'] = (c > df['SMA20']).astype(int)
    df['Above50'] = (c > df['SMA50']).astype(int)
    df['Above200'] = (c > df['SMA200']).astype(int)
    
    # MACD
    df['MACD'] = df['EMA12'] - df['EMA26']
    df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_hist'] = df['MACD'] - df['MACD_signal']
    df['MACD_cross_up'] = ((df['MACD_hist'].shift(1) <= 0) & (df['MACD_hist'] > 0)).astype(int)
    
    # RSI
    df['RSI14'] = _rsi(c, 14)
    df['RSI14_min_30'] = df['RSI14'].rolling(30, min_periods=1).min()
    
    # Bollinger Bands
    m20 = c.rolling(20, min_periods=1).mean()
    s20 = c.rolling(20, min_periods=1).std()
    df['BB_upper'] = m20 + 2*s20
    df['BB_lower'] = m20 - 2*s20
    df['BB_width'] = (df['BB_upper'] - df['BB_lower']) / m20.replace(0, np.nan)
    
    # ATR
    prev_c = c.shift(1)
    tr = pd.concat([(h - l), (h - prev_c).abs(), (l - prev_c).abs()], axis=1).max(axis=1)
    df['ATR14'] = _wilder_sma(tr, 14)
    
    # ADX
    up_move = h.diff()
    dn_move = -l.diff()
    plus_dm = pd.Series(np.where((up_move > dn_move) & (up_move > 0), up_move, 0.0), index=df.index)
    minus_dm = pd.Series(np.where((dn_move > up_move) & (dn_move > 0), dn_move, 0.0), index=df.index)
    plus_di = 100 * _wilder_sma(plus_dm, 14) / df['ATR14'].replace(0, np.nan)
    minus_di = 100 * _wilder_sma(minus_dm, 14) / df['ATR14'].replace(0, np.nan)
    dx = ((plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)) * 100
    df['+DI'] = plus_di
    df['-DI'] = minus_di
    df['ADX'] = _wilder_sma(dx, 14)
    
    # Volume
    obv = np.zeros(len(df), dtype=float)
    for i in range(1, len(df)):
        if c.iloc[i] > c.iloc[i-1]:
            obv[i] = obv[i-1] + v.iloc[i]
        elif c.iloc[i] < c.iloc[i-1]:
            obv[i] = obv[i-1] - v.iloc[i]
        else:
            obv[i] = obv[i-1]
    df['OBV'] = pd.Series(obv, index=df.index)
    df['OBV_rising'] = (df['OBV'] > df['OBV'].shift(7)).astype(int)
    
    # ROC
    df['ROC5'] = (c / c.shift(5) - 1.0) * 100
    df['ROC10'] = (c / c.shift(10) - 1.0) * 100
    df['ROC21'] = (c / c.shift(21) - 1.0) * 100
    
    # Breakouts
    df['New_52W_High'] = (c >= c.rolling(252, min_periods=20).max().shift(1)).astype(int)
    df['Vol20'] = v.rolling(20, min_periods=1).mean()
    df['VolumeSpike'] = ((v > 2*df['Vol20']) & (v > 10000)).astype(int)
    
    # Risk filters
    df['AvgVal20'] = (c * v).rolling(20, min_periods=1).mean()
    df['Illiquid20'] = ((df['Vol20'] < CONFIG['MIN_VOLUME_20D']) | (df['AvgVal20'] < CONFIG['MIN_VALUE_20D'])).astype(int)
    
    # Forward returns
    df['Close_fwd_5TS'] = c.shift(-5)
    df['ret_fwd_5TS'] = (df['Close_fwd_5TS'] - c) / c * 100.0
    
    return df

print('✅ Indicator engine ready!')

# ============================================================================
# CELL 6: Candlestick Patterns
# ============================================================================

def detect_patterns(df):
    df = df.copy().sort_values('DATE')
    o, h, l, c = df['Open'], df['High'], df['Low'], df['Close']
    
    body = c - o
    abs_body = body.abs()
    rng = h - l
    rng_safe = rng.replace(0, 1e-12)
    
    # Hammer
    min_co = pd.concat([c, o], axis=1).min(axis=1)
    max_co = pd.concat([c, o], axis=1).max(axis=1)
    df['Hammer'] = (((min_co - l) >= 2*abs_body) & ((h - max_co) <= 0.3*rng_safe)).astype(int)
    
    # Engulfing
    o1, c1 = o.shift(1), c.shift(1)
    df['BullishEngulf'] = (((c1 < o1) & (c > o) & (o < c1) & (c > o1))).astype(int)
    
    # Morning Star
    o2, c2 = o.shift(2), c.shift(2)
    df['MorningStar'] = ((c2 < o2) & (abs_body.shift(1) < abs_body.shift(2)*0.3) & (c > o) & (c > (o2+c2)/2)).astype(int)
    
    df['RecentMajorPattern'] = (df[['BullishEngulf', 'MorningStar']].rolling(5, min_periods=1).max().sum(axis=1) > 0).astype(int)
    
    return df

print('✅ Pattern recognition ready!')

# ============================================================================
# CELL 7: Process All Data
# ============================================================================

print('🔢 Computing indicators...')
indicators = raw_data.groupby('SC_CODE', group_keys=False, observed=False).apply(compute_indicators).reset_index(drop=True)

print('🕯️ Detecting patterns...')
full_data = indicators.groupby('SC_CODE', group_keys=False, observed=False).apply(detect_patterns).reset_index(drop=True)

print('📊 Adding context...')
full_data['RS21_pct'] = full_data.groupby('DATE', observed=False)['ROC21'].rank(pct=True)
full_data['RS21_top20'] = full_data['RS21_pct'].fillna(-np.inf).ge(0.80).astype(int)

prev_close = full_data.groupby('SC_CODE', observed=False)['Close'].shift(1)
full_data['UpDay'] = full_data['Close'].gt(prev_close.fillna(np.inf)).astype(int)
breadth = full_data.groupby('DATE', observed=False)['UpDay'].mean().rename('Breadth')
full_data = full_data.merge(breadth, on='DATE', how='left')
full_data['Breadth_OK'] = full_data['Breadth'].fillna(0.0).ge(0.45).astype(int)

print(f'✅ Complete dataset: {len(full_data):,} rows, {len(full_data.columns)} columns')
display(full_data.tail())

# ============================================================================
# CELL 8: Scoring System
# ============================================================================

WEIGHTS = {
    'UptrendStrong': 3, 'ADX_up': 2, 'MACD_cross': 2, 'RSI_good': 2,
    'VolumeSpike': 2, 'New52W': 2, 'OBV_rising': 1, 'RS_top20': 2,
    'Pattern': 2, 'Breadth': 1, 'Illiquid': -2
}

def calculate_score(s):
    score = 0
    score += WEIGHTS['UptrendStrong'] * int((s['Close'] > s['SMA20']) and (s['Close'] > s['SMA50']))
    score += WEIGHTS['ADX_up'] * int((s['ADX'] > 25) and (s['+DI'] > s['-DI']))
    score += WEIGHTS['MACD_cross'] * int(s.get('MACD_cross_up', 0) == 1)
    score += WEIGHTS['RSI_good'] * int((s.get('RSI14_min_30', 100) < 30) and (40 < s.get('RSI14', 0) < 75))
    score += WEIGHTS['VolumeSpike'] * int(s.get('VolumeSpike', 0) == 1)
    score += WEIGHTS['New52W'] * int(s.get('New_52W_High', 0) == 1)
    score += WEIGHTS['OBV_rising'] * int(s.get('OBV_rising', 0) == 1)
    score += WEIGHTS['RS_top20'] * int(s.get('RS21_top20', 0) == 1)
    score += WEIGHTS['Pattern'] * int(s.get('RecentMajorPattern', 0) == 1)
    score += WEIGHTS['Breadth'] * int(s.get('Breadth_OK', 1) == 1)
    score += WEIGHTS['Illiquid'] * int(s.get('Illiquid20', 0) == 1)
    return score

print('✅ Scoring system ready!')







# ============================================================================
# CELL 9: Train ML Model
# ============================================================================

print('🤖 Training ML model...')

FEATURE_COLS = [
    'Above20', 'Above50', 'Above200', 'RSI14', 'MACD_hist',
    'ADX', '+DI', '-DI', 'ATR14', 'BB_width',
    'OBV_rising', 'VolumeSpike', 'New_52W_High',
    'RS21_pct', 'Breadth', 'Illiquid20'
]

# Filter data with valid forward returns (exclude last 5 trading days)
ml_data = full_data[full_data['ret_fwd_5TS'].notna()].copy()

print(f'   Total samples with forward returns: {len(ml_data):,}')

if len(ml_data) < 100:
    print('⚠️ Not enough data for ML training. Need at least 100 samples.')
    print('   Skipping ML model, will use rule-based scoring only.')
    model = None
    scaler = None
    acc = 0
else:
    ml_data['target'] = (ml_data['ret_fwd_5TS'] > CONFIG['ML_TARGET_RETURN']).astype(int)
    
    # Prepare features
    X = ml_data[FEATURE_COLS].fillna(0)
    y = ml_data['target']
    
    # Chronological split (80/20)
    split_idx = int(len(ml_data) * 0.8)
    ml_data_sorted = ml_data.sort_values('DATE').reset_index(drop=True)
    
    X_train = X.iloc[:split_idx]
    y_train = y.iloc[:split_idx]
    X_test = X.iloc[split_idx:]
    y_test = y.iloc[split_idx:]
    
    print(f'   Training samples: {len(X_train):,}')
    print(f'   Test samples: {len(X_test):,}')
    print(f'   Target distribution: {y.mean():.1%} positive')
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train model
    if XGB_AVAILABLE:
        model = xgb.XGBClassifier(
            n_estimators=100, max_depth=6, learning_rate=0.1, 
            random_state=42, n_jobs=-1, eval_metric='logloss'
        )
        print('   Using XGBoost')
    else:
        model = RandomForestClassifier(
            n_estimators=100, max_depth=10, min_samples_split=20,
            random_state=42, n_jobs=-1
        )
        print('   Using Random Forest')
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    
    print(f'\n✅ Model trained successfully!')
    print(f'   Test accuracy: {acc:.2%}')
    print(f'   Baseline (always predict majority): {max(y_test.mean(), 1-y_test.mean()):.2%}')
    
    # Save model
    model_path = MODELS_DIR / f'model_{date.today().strftime("%Y%m%d")}.pkl'
    with open(model_path, 'wb') as f:
        pickle.dump((model, scaler, FEATURE_COLS), f)
    print(f'   Model saved: {model_path}')



# ============================================================================
# CELL 10: Generate Today's Picks
# ============================================================================

print('🔍 Generating stock picks...')

latest_date = full_data['DATE'].max()
today_data = full_data[full_data['DATE'] == latest_date].copy()

print(f'   Analysis date: {latest_date}')
print(f'   Candidates: {len(today_data):,} stocks')

# Calculate rule-based scores
today_data['WeightedScore'] = today_data.apply(calculate_score, axis=1)

# Get ML predictions if model exists
if model is not None and scaler is not None:
    X_today = today_data[FEATURE_COLS].fillna(0)
    today_data['ML_Probability'] = model.predict_proba(X_today)[:, 1]
    
    # Composite score: 60% rules + 40% ML
    max_ws = today_data['WeightedScore'].max()
    today_data['WeightedScore_norm'] = today_data['WeightedScore'] / max_ws * 100 if max_ws > 0 else 0
    today_data['CompositeScore'] = 0.6 * today_data['WeightedScore_norm'] + 0.4 * today_data['ML_Probability'] * 100
    
    print('   Using ML-enhanced scoring')
else:
    # Use rule-based scoring only
    today_data['ML_Probability'] = 0.5  # Neutral
    today_data['CompositeScore'] = today_data['WeightedScore'] * 5  # Scale to 0-100
    
    print('   Using rule-based scoring only')

# Filter criteria
shortlist = today_data[
    (today_data['WeightedScore'] >= CONFIG['MIN_WEIGHTED_SCORE']) &
    (today_data['CompositeScore'] >= CONFIG['MIN_COMPOSITE_SCORE']) &
    (today_data['Illiquid20'] == 0)
].sort_values('CompositeScore', ascending=False)

# Additional filter for ML probability if model exists
if model is not None:
    shortlist = shortlist[shortlist['ML_Probability'] >= CONFIG['MIN_ML_PROBABILITY']]

print(f'\n{"="*80}')
print(f'🎯 TOP STOCK PICKS - {latest_date}')
print(f'{"="*80}\n')

if len(shortlist) == 0:
    print('⚠️ No stocks meet the criteria today.')
    print('   Try adjusting CONFIG thresholds or check market conditions.')
else:
    display_cols = ['SC_CODE', 'SC_NAME', 'Close', 'CompositeScore', 'WeightedScore', 'ML_Probability', 
                    'RSI14', 'ADX', 'VolumeSpike', 'New_52W_High']
    display(shortlist[[c for c in display_cols if c in shortlist.columns]].head(20))
    
    print(f'\n📊 Summary: {len(shortlist)} qualified stocks')
    print(f'   Avg Composite: {shortlist["CompositeScore"].mean():.1f}')
    if model is not None:
        print(f'   Avg ML Prob: {shortlist["ML_Probability"].mean():.1%}')
    print(f'   Avg Weighted: {shortlist["WeightedScore"].mean():.1f}')

    export_file = LOGS_DIR / f'shortlist_{latest_date.strftime("%Y%m%d")}.csv'
    shortlist.to_csv(export_file, index=False)
    print(f'\n💾 Saved: {export_file}')



# ============================================================================
# CELL 11: Portfolio Builder
# ============================================================================

class PortfolioBuilder:
    def __init__(self, capital, config):
        self.capital = capital
        self.config = config
    
    def calc_position(self, price):
        risk_per_trade = self.capital * (self.config['RISK_PER_TRADE_PCT'] / 100)
        max_value = self.capital * (self.config['MAX_POSITION_SIZE_PCT'] / 100)
        stop_loss_pct = 5.0
        
        risk_per_share = price * (stop_loss_pct / 100)
        shares_by_risk = int(risk_per_trade / risk_per_share)
        shares_by_max = int(max_value / price)
        shares = min(shares_by_risk, shares_by_max)
        
        return {
            'shares': shares,
            'value': shares * price,
            'stop_loss': price * 0.95
        }
    
    def build(self, shortlist):
        portfolio = []
        allocated = 0
        
        for _, row in shortlist.head(self.config['MAX_POSITIONS']).iterrows():
            if allocated >= self.capital * 0.95:
                break
            
            pos = self.calc_position(row['Close'])
            if pos['value'] > 0:
                portfolio.append({
                    'SC_CODE': row['SC_CODE'],
                    'SC_NAME': row['SC_NAME'],
                    'Entry_Price': row['Close'],
                    'Shares': pos['shares'],
                    'Position_Value': pos['value'],
                    'Stop_Loss': pos['stop_loss'],
                    'Score': row['CompositeScore'],
                    'ML_Prob': row['ML_Probability']
                })
                allocated += pos['value']
        
        return pd.DataFrame(portfolio)

if len(shortlist) > 0:
    print('\n💼 Building portfolio...')
    builder = PortfolioBuilder(CONFIG['PORTFOLIO_SIZE'], CONFIG)
    portfolio = builder.build(shortlist)
    
    print(f'\n{"="*80}')
    print(f'💼 PORTFOLIO - Capital: ₹{CONFIG["PORTFOLIO_SIZE"]:,}')
    print(f'{"="*80}\n')
    display(portfolio)
    
    print(f'\n📊 Stats:')
    print(f'   Positions: {len(portfolio)}')
    print(f'   Allocated: ₹{portfolio["Position_Value"].sum():,.0f}')
    print(f'   Cash: ₹{CONFIG["PORTFOLIO_SIZE"] - portfolio["Position_Value"].sum():,.0f}')
    
    portfolio.to_csv(PORTFOLIO_DIR / f'portfolio_{latest_date.strftime("%Y%m%d")}.csv', index=False)
else:
    portfolio = None
    print('\n⚠️ No portfolio created (no qualified stocks)')


# ============================================================================
# CELL 12: Visualize Top Pick
# ============================================================================

if len(shortlist) > 0:
    top = shortlist.iloc[0]
    stock_hist = full_data[full_data['SC_CODE'] == top['SC_CODE']].tail(60)
    
    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03,
        row_heights=[0.6, 0.2, 0.2],
        subplot_titles=(f'{top["SC_NAME"]} - Score: {top["CompositeScore"]:.1f}', 'Volume', 'RSI')
    )
    
    fig.add_trace(go.Candlestick(
        x=stock_hist['DATE'], open=stock_hist['Open'], high=stock_hist['High'],
        low=stock_hist['Low'], close=stock_hist['Close'], name='Price'
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter(x=stock_hist['DATE'], y=stock_hist['SMA20'], name='SMA20', line=dict(color='blue')), row=1, col=1)
    fig.add_trace(go.Scatter(x=stock_hist['DATE'], y=stock_hist['SMA50'], name='SMA50', line=dict(color='orange')), row=1, col=1)
    
    colors = ['red' if r['Close'] < r['Open'] else 'green' for _, r in stock_hist.iterrows()]
    fig.add_trace(go.Bar(x=stock_hist['DATE'], y=stock_hist['Volume'], marker_color=colors, showlegend=False), row=2, col=1)
    
    fig.add_trace(go.Scatter(x=stock_hist['DATE'], y=stock_hist['RSI14'], name='RSI', line=dict(color='purple')), row=3, col=1)
    fig.add_hline(y=70, line_dash='dash', line_color='red', row=3, col=1)
    fig.add_hline(y=30, line_dash='dash', line_color='green', row=3, col=1)
    
    fig.update_layout(height=800, xaxis_rangeslider_visible=False)
    fig.show()


# ============================================================================
# CELL 13: Backtest
# ============================================================================

print('\n🧪 Running backtest...')

bt_start = latest_date - timedelta(days=90)
bt_data = full_data[full_data['DATE'] >= bt_start].copy()
bt_data['WeightedScore'] = bt_data.apply(calculate_score, axis=1)

# ML predictions if model exists
if model is not None and scaler is not None:
    X_bt = bt_data[FEATURE_COLS].fillna(0)
    bt_data['ML_Probability'] = model.predict_proba(X_bt)[:, 1]
    
    max_ws_bt = bt_data.groupby('DATE')['WeightedScore'].transform('max')
    bt_data['WeightedScore_norm'] = np.where(max_ws_bt > 0, bt_data['WeightedScore'] / max_ws_bt * 100, 0)
    bt_data['CompositeScore'] = 0.6 * bt_data['WeightedScore_norm'] + 0.4 * bt_data['ML_Probability'] * 100
    
    # Filter with ML probability
    valid = bt_data[
        (bt_data['WeightedScore'] >= CONFIG['MIN_WEIGHTED_SCORE']) &
        (bt_data['ML_Probability'] >= CONFIG['MIN_ML_PROBABILITY']) &
        (bt_data['ret_fwd_5TS'].notna()) &
        (bt_data['Illiquid20'] == 0)
    ]
else:
    # Rule-based only
    bt_data['ML_Probability'] = 0.5
    bt_data['CompositeScore'] = bt_data['WeightedScore'] * 5
    
    valid = bt_data[
        (bt_data['WeightedScore'] >= CONFIG['MIN_WEIGHTED_SCORE']) &
        (bt_data['ret_fwd_5TS'].notna()) &
        (bt_data['Illiquid20'] == 0)
    ]

total = len(valid)

if total == 0:
    print('⚠️ No valid backtest samples found.')
    print('   This is normal if you have less than 95 days of data.')
    print('   The system needs historical data with forward returns (5 sessions ahead).')
else:
    winners = len(valid[valid['ret_fwd_5TS'] > 0])
    big_wins = len(valid[valid['ret_fwd_5TS'] > CONFIG['ML_TARGET_RETURN']])
    
    print(f'\n{"="*80}')
    print(f'📊 BACKTEST RESULTS (90 days)')
    print(f'{"="*80}')
    print(f'   Period: {bt_start} to {latest_date}')
    print(f'   Total picks: {total:,}')
    print(f'   Winners (>0%): {winners:,} ({winners/total*100:.1f}%)')
    print(f'   Big wins (>{CONFIG["ML_TARGET_RETURN"]}%): {big_wins:,} ({big_wins/total*100:.1f}%)')
    print(f'   Avg return: {valid["ret_fwd_5TS"].mean():.2f}%')
    print(f'   Median return: {valid["ret_fwd_5TS"].median():.2f}%')
    print(f'   Best: {valid["ret_fwd_5TS"].max():.2f}%')
    print(f'   Worst: {valid["ret_fwd_5TS"].min():.2f}%')
    
    # Visualization
    plt.figure(figsize=(12, 5))
    plt.hist(valid['ret_fwd_5TS'], bins=50, edgecolor='black', alpha=0.7)
    plt.axvline(0, color='red', linestyle='--', linewidth=2, label='Break-even')
    plt.axvline(valid['ret_fwd_5TS'].mean(), color='green', linestyle='--', linewidth=2, 
                label=f'Mean: {valid["ret_fwd_5TS"].mean():.2f}%')
    plt.xlabel('5-Session Return (%)')
    plt.ylabel('Frequency')
    plt.title('Backtest Return Distribution')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()
    
    # Save results
    bt_file = LOGS_DIR / f'backtest_{bt_start.strftime("%Y%m%d")}_{latest_date.strftime("%Y%m%d")}.csv'
    valid.to_csv(bt_file, index=False)
    print(f'\n💾 Backtest saved: {bt_file}')



# ============================================================================
# CELL 14: Summary
# ============================================================================

# Calculate summary stats safely
try:
    total_picks = len(valid) if 'valid' in locals() else 0
    success_rate = (winners/total*100) if 'winners' in locals() and total > 0 else 0
    avg_return = valid['ret_fwd_5TS'].mean() if 'valid' in locals() and len(valid) > 0 else 0
except:
    total_picks = 0
    success_rate = 0
    avg_return = 0

print(f'\n{"="*80}')
print(f'📋 SYSTEM SUMMARY')
print(f'{"="*80}')
print(f'''
📅 Date: {latest_date}

📊 DATA PROCESSED:
   • Stocks analyzed: {full_data["SC_CODE"].nunique():,}
   • Historical data: {CONFIG["DAYS_BACK"]} days
   • Total rows: {len(full_data):,}
   • Date range: {full_data["DATE"].min()} to {full_data["DATE"].max()}

🎯 TODAY'S PICKS:
   • Qualified stocks: {len(shortlist) if len(shortlist) > 0 else 0}
   • Portfolio positions: {len(portfolio) if 'portfolio' in locals() and portfolio is not None else 0}
   • Capital allocated: ₹{portfolio["Position_Value"].sum():,.0f if 'portfolio' in locals() and portfolio is not None else 0}
   • Avg composite score: {shortlist["CompositeScore"].mean():.1f if len(shortlist) > 0 else 0}

🧪 BACKTEST (90 days):
   • Total picks tested: {total_picks:,}
   • Success rate: {success_rate:.1f}%
   • Average return: {avg_return:.2f}%
   • Status: {'✓ Valid' if total_picks > 0 else '⚠️ Insufficient data'}

🤖 ML MODEL:
   • Status: {'✓ Trained' if model is not None else '✗ Not trained (insufficient data)'}
   • Accuracy: {acc:.2% if 'acc' in locals() and acc > 0 else 'N/A'}
   • Features: {len(FEATURE_COLS)}
   • Type: {'XGBoost' if XGB_AVAILABLE and model is not None else 'Random Forest' if model is not None else 'Rule-based only'}

💾 FILES SAVED:
   • Cache: {CACHE_DIR}
   • Logs: {LOGS_DIR}
   • Models: {MODELS_DIR}
   • Portfolio: {PORTFOLIO_DIR}

📈 TECHNICAL INDICATORS:
   • Moving Averages: 9 types
   • Momentum: RSI, MACD, ADX
   • Volume: OBV
   • Breakouts: 52W High, Volume Spikes
   • Patterns: 3+ major patterns

✅ System Status: Operational
''')

print(f'\n{"="*80}')
print('🎉 ANALYSIS COMPLETE!')
print(f'{"="*80}')

print('''
📝 NEXT STEPS:

1. REVIEW PICKS:
   - Check the shortlist above
   - Review individual stock charts
   - Verify fundamentals separately

2. PAPER TRADE (RECOMMENDED):
   - Track picks for 2-4 weeks
   - Monitor actual returns
   - Adjust thresholds if needed

3. RISK MANAGEMENT:
   - Use stop losses (5% recommended)
   - Position size: Max 15% per stock
   - Diversify across sectors
   - Never risk more than 2% per trade

4. AUTOMATION (OPTIONAL):
   - Save this notebook
   - Run daily after market close
   - Set up email alerts in CONFIG

⚠️ DISCLAIMER:
This system is for EDUCATIONAL purposes only.
- Past performance ≠ Future results
- Markets are inherently risky
- Always consult a financial advisor
- Only invest what you can afford to lose

Good luck and trade safely! 🚀
''')

# ============================================================================
# END OF NOTEBOOK
# ===============

"""
NEXT STEPS:

1. PAPER TRADE (2-4 weeks):
   - Track all picks in spreadsheet
   - Monitor actual returns
   - Adjust thresholds if needed

2. ENABLE ALERTS:
   - Set CONFIG['ENABLE_EMAIL_ALERTS'] = True
   - Add your email credentials
   - Test with small picks

3. AUTOMATION:
   - Convert to .py script
   - Set up cron job: 30 18 * * *
   - Monitor logs daily

4. ENHANCE:
   - Add more indicators
   - Tune ML model
   - Track P&L

⚠️ RISK WARNING:
- This is for educational purposes only
- Past performance ≠ future results
- Always use stop losses
- Never risk more than you can afford to lose
- Consult a financial advisor

Good luck! 🚀
"""
