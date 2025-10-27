"""
Configuration constants for Indian equity trading system.
"""

# NIFTY 50 stock symbols (with .NS suffix for Yahoo Finance)
NIFTY_50_SYMBOLS = [
    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS',
    'HINDUNILVR.NS', 'ITC.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'KOTAKBANK.NS',
    'BAJFINANCE.NS', 'LT.NS', 'ASIANPAINT.NS', 'AXISBANK.NS', 'MARUTI.NS',
    'SUNPHARMA.NS', 'TITAN.NS', 'ULTRACEMCO.NS', 'NESTLEIND.NS', 'WIPRO.NS',
    'HCLTECH.NS', 'TECHM.NS', 'NTPC.NS', 'ONGC.NS', 'POWERGRID.NS',
    'M&M.NS', 'TATAMOTORS.NS', 'COALINDIA.NS', 'TATASTEEL.NS', 'BAJAJFINSV.NS',
    'ADANIPORTS.NS', 'HINDALCO.NS', 'INDUSINDBK.NS', 'CIPLA.NS', 'DRREDDY.NS',
    'EICHERMOT.NS', 'DIVISLAB.NS', 'GRASIM.NS', 'HEROMOTOCO.NS', 'JSWSTEEL.NS',
    'BRITANNIA.NS', 'APOLLOHOSP.NS', 'BPCL.NS', 'TATACONSUM.NS', 'UPL.NS',
    'BAJAJ-AUTO.NS', 'ADANIENT.NS', 'SBILIFE.NS', 'HDFCLIFE.NS', 'LTIM.NS'
]

# Top 10 for testing
TOP_10_NIFTY = NIFTY_50_SYMBOLS[:10]

# Data configuration
DATA_START_DATE = '2020-01-01'  # 3+ years of data
DATA_CACHE_DIR = 'data/storage'
DATA_UPDATE_HOUR = 16  # 4 PM IST for EOD updates

# Trading parameters
TRADING_HORIZON_DAYS = 5
MIN_DAILY_VOLUME = 10_00_00_000  # 10 Crore INR minimum daily volume
MAX_POSITIONS = 10
SECTOR_CONCENTRATION_LIMIT = 0.40
MAX_PORTFOLIO_HEAT = 1.0
MAX_CORRELATION = 0.7

# Technical indicator parameters
# Volatility
YANG_ZHANG_PERIOD = 20
PARKINSON_PERIOD = 20
GARMAN_KLASS_PERIOD = 20

# Trend indicators
SUPERTREND_PERIOD = 7
SUPERTREND_MULTIPLIER = 2.5
ICHIMOKU_TENKAN = 3
ICHIMOKU_KIJUN = 9
ICHIMOKU_SENKOU = 18
ADX_PERIOD = 7
ADX_TREND_THRESHOLD = 30

# Momentum indicators
KST_PERIODS = [3, 5, 8, 10]
KST_SMAS = [3, 5, 8, 10]
ULTIMATE_OSC_PERIODS = [3, 5, 10]
SCHAFF_CYCLE = 5
SCHAFF_FAST = 23
SCHAFF_SLOW = 50

# Volume indicators
CMF_PERIOD = 10
KLINGER_FAST = 34
KLINGER_SLOW = 55
KLINGER_SIGNAL = 13

# Machine Learning
ML_TARGET_RETURN = 0.02  # 2% target for 5-day returns
ML_LOOKBACK_PERIODS = [5, 10, 20]
ML_RSI_PERIOD = 7
ML_MACD_FAST = 5
ML_MACD_SLOW = 10
ML_MACD_SIGNAL = 3
ML_ADX_PERIOD = 7

# Random Forest
RF_N_ESTIMATORS = 100
RF_MAX_DEPTH = 5
RF_MIN_SAMPLES_SPLIT = 20
RF_MIN_SAMPLES_LEAF = 10

# XGBoost
XGB_N_ESTIMATORS = 100
XGB_MAX_DEPTH = 3
XGB_LEARNING_RATE = 0.1
XGB_SUBSAMPLE = 0.8
XGB_COLSAMPLE_BYTREE = 0.8

# Cross-validation
CV_N_SPLITS = 5
CV_PURGE_DAYS = 5
CV_EMBARGO_DAYS = 5

# Walk-forward analysis
WF_TRAIN_MONTHS = 6
WF_TEST_MONTHS = 1

# Transaction costs (in percentage)
BROKERAGE_PCT = 0.03  # 0.03% per leg, max ₹20
STT_SELL_PCT = 0.1  # 0.1% on sell side
EXCHANGE_CHARGES_PCT = 0.00325  # 0.00325% of turnover
GST_RATE = 0.18  # 18% on brokerage + charges
STAMP_DUTY_BUY_PCT = 0.015  # 0.015% on buy side
TOTAL_TRANSACTION_COST_PCT = 0.3  # Approximate round-trip cost

# Slippage
SLIPPAGE_LARGE_CAP = 0.0005  # 0.05%
SLIPPAGE_MID_CAP = 0.001  # 0.1%

# Risk management
STOP_LOSS_ATR_MULTIPLIER = 2.0
STOP_LOSS_PCT = 0.03  # 3%
TAKE_PROFIT_MULTIPLIER = 3.0  # 3:1 reward:risk

# Position sizing
KELLY_FRACTION = 0.25  # Use 1/4 Kelly
MAX_POSITION_SIZE = 0.25  # 25% max per position

# Market regime
REGIME_ADX_THRESHOLD = 25
REGIME_HURST_THRESHOLD = 0.5
MARKET_TRENDING_PCT = 0.35
MARKET_RANGING_PCT = 0.60

# Candlestick patterns (success rates and average returns)
PATTERN_SUCCESS_RATES = {
    'INVERTED_HAMMER': {'success_rate': 0.60, 'avg_return': 0.0112},
    'BEARISH_ENGULFING': {'success_rate': 0.57, 'avg_return': 0.0062},
    'MORNING_STAR': {'success_rate': 0.72, 'avg_return': 0.0145},
    'EVENING_STAR': {'success_rate': 0.68, 'avg_return': -0.0138},
    'THREE_WHITE_SOLDIERS': {'success_rate': 0.65, 'avg_return': 0.0132},
    'THREE_BLACK_CROWS': {'success_rate': 0.61, 'avg_return': -0.0115},
    'GRAVESTONE_DOJI': {'success_rate': 0.57, 'avg_return': -0.0065},
}

# Performance targets
TARGET_WIN_RATE = 0.55
TARGET_SHARPE_RATIO = 1.5
TARGET_MAX_DRAWDOWN = 0.15
TARGET_ANNUAL_RETURN = 0.15  # 15%

# Trading schedule (IST)
PREMARKET_SCAN_HOUR = 8
PREMARKET_SCAN_MINUTE = 30
MARKET_OPEN_HOUR = 9
MARKET_OPEN_MINUTE = 15
MARKET_CLOSE_HOUR = 15
MARKET_CLOSE_MINUTE = 30
EOD_PROCESSING_HOUR = 16
EOD_PROCESSING_MINUTE = 0

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Logging
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
