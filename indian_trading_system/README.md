# Indian Equity Trading System

A comprehensive short-term trading system for Indian equity markets (NSE/BSE) with a 5-day trading horizon. The system implements advanced technical indicators, machine learning models, and proper backtesting with Indian market-specific considerations.

## Features

### 1. Advanced Technical Analysis
- **Volatility Indicators**
  - Yang-Zhang volatility estimator (8-15% more accurate)
  - Parkinson volatility using high-low data
  - Garman-Klass volatility with gap adjustment
  - All optimized with Numba JIT compilation

- **Trend Indicators**
  - Supertrend (period=7, multiplier=2.5)
  - Ichimoku Cloud with compressed parameters
  - ADX for trend strength identification

- **Momentum Indicators**
  - Know Sure Thing (KST) optimized for 5-day trading
  - Ultimate Oscillator (3-5-10 periods)
  - Schaff Trend Cycle

- **Volume Indicators**
  - Chaikin Money Flow (CMF)
  - Klinger Oscillator
  - On Balance Volume (OBV) with volume ratio

### 2. Candlestick Pattern Recognition
Detects patterns with historical success rates:
- Inverted Hammer (60% success, 1.12% avg return)
- Bearish Engulfing (57% success, 0.62% return)
- Morning/Evening Star (68-72% success)
- Three White Soldiers/Black Crows
- Gravestone Doji

### 3. Machine Learning Models
- **Random Forest** (100 trees, max_depth=5)
- **XGBoost** (100 estimators, optimized parameters)
- Purged cross-validation with 5-day purge/embargo
- SMOTE for handling class imbalance
- Feature engineering with 50+ technical features

### 4. Backtesting Framework
- Vectorized backtesting for speed
- Transaction costs: 0.3% round-trip (discount broker model)
- Slippage: 0.05% for large-caps, 0.1% for mid-caps
- Performance metrics: Sharpe, Sortino, Max DD, Win Rate

### 5. Portfolio Management
- Position sizing: Equal weight, Volatility parity, Kelly Criterion
- Risk management: Max 10 positions, sector limits, stop-losses
- Portfolio heat tracking
- Correlation monitoring

### 6. Indian Market Features
- Detailed transaction cost calculator (STT, GST, stamp duty)
- Market regime identification (trending vs ranging)
- Trading hours and holiday calendar
- Surveillance list monitoring (ASM/GSM)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd indian_trading_system
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

### Basic Usage

```python
from main import TradingSystem

# Initialize system with top 10 NIFTY stocks
system = TradingSystem(symbols=TOP_10_NIFTY, initial_capital=1000000)

# Run complete workflow
results = system.run_complete_workflow(train_ml=True, backtest=True)

# View top trading opportunities
print(results['rankings'])
```

### Running the Main Script

```bash
cd indian_trading_system
python main.py
```

This will:
1. Download and cache data for top 10 NIFTY stocks
2. Calculate all technical indicators
3. Train ML models with cross-validation
4. Generate trading signals
5. Rank stocks by signal strength
6. Run backtests and display results

## Module Structure

```
indian_trading_system/
├── data/
│   ├── loader.py          # Data collection with caching
│   ├── cleaner.py         # Data validation and cleaning
│   └── storage/           # Parquet cache files
├── indicators/
│   ├── technical.py       # Technical indicators
│   ├── patterns.py        # Candlestick patterns
│   └── volatility.py      # Volatility estimators
├── models/
│   ├── features.py        # Feature engineering (50+ features)
│   ├── ml_models.py       # RF, XGBoost with purged CV
│   └── validation.py      # Purged cross-validation
├── backtesting/
│   ├── engine.py          # Vectorized backtesting
│   └── metrics.py         # Performance calculations
├── portfolio/
│   ├── manager.py         # Portfolio management
│   ├── signals.py         # Signal generation
│   └── risk.py           # Risk management
├── utils/
│   ├── indian_market.py  # Indian market utilities
│   ├── constants.py      # Configuration
│   └── optimization.py   # Numba optimizations
└── main.py               # Main execution script
```

## Usage Examples

### 1. Data Loading

```python
from data.loader import DataLoader

loader = DataLoader()

# Load single stock
df = loader.load_stock_data('RELIANCE.NS')

# Load NIFTY 50
data_dict = loader.load_nifty_50()

# Load top 10 for testing
data_dict = loader.load_top_10_nifty()
```

### 2. Technical Indicators

```python
from indicators.technical import TechnicalIndicators
from indicators.volatility import VolatilityEstimators

technical = TechnicalIndicators()
volatility = VolatilityEstimators()

# Calculate all indicators
df = technical.calculate_all(df)
df = volatility.calculate_all(df)
```

### 3. ML Model Training

```python
from models.features import FeatureEngineer
from models.ml_models import MLModels

# Create features
engineer = FeatureEngineer()
df_with_features = engineer.create_all_features(df)
X, y, feature_names = engineer.prepare_ml_data(df_with_features)

# Train models with cross-validation
ml_models = MLModels()
rf_cv_results = ml_models.cross_validate(X, y, model_type='rf')

# Train final models
ml_models.train_final_models(X, y, feature_names)

# Make predictions
predictions = ml_models.predict(X, model_type='ensemble')
```

### 4. Signal Generation

```python
from portfolio.signals import SignalGenerator

signal_gen = SignalGenerator()

# Generate all signals
df_with_signals = signal_gen.generate_all_signals(df)

# View recent signals
summary = signal_gen.get_signal_summary(df_with_signals, recent_days=10)
print(summary)
```

### 5. Backtesting

```python
from backtesting.engine import BacktestEngine

engine = BacktestEngine(initial_capital=1000000)

# Run backtest
results = engine.run_backtest(df, signals, position_size=0.3)

# Print results
engine.print_results(results)
```

### 6. Portfolio Management

```python
from portfolio.manager import PortfolioManager

portfolio = PortfolioManager(capital=1000000, max_positions=10)

# Add position
portfolio.add_position('RELIANCE.NS', 100, 2500, stop_loss=2400)

# Update prices
portfolio.update_position('RELIANCE.NS', 2550)

# Check stop losses
if portfolio.check_stop_loss('RELIANCE.NS'):
    portfolio.remove_position('RELIANCE.NS')

# View portfolio
portfolio.print_portfolio()
```

## Configuration

Edit `utils/constants.py` to customize:
- Stock universe (NIFTY 50, custom list)
- Technical indicator parameters
- ML model hyperparameters
- Risk management rules
- Transaction costs
- Position sizing methods

## Performance Targets

- Win rate: 55-70% with proper indicator confirmation
- Sharpe ratio: > 1.5 in backtests
- Maximum drawdown: < 15%
- Annual returns: 15-20% after costs
- Processing speed: Full NSE universe in < 1 minute (with optimizations)

## Key Performance Metrics

The system calculates:
- **Return Metrics**: Total return, CAGR, daily/monthly returns
- **Risk Metrics**: Sharpe ratio, Sortino ratio, Max drawdown, Calmar ratio
- **Trade Metrics**: Win rate, profit factor, avg win/loss, number of trades
- **Portfolio Metrics**: Portfolio heat, sector exposure, correlation

## Indian Market Specifics

### Transaction Costs
```
Buy Side:
- Brokerage: 0.03% or ₹20 (whichever lower)
- Exchange charges: 0.00325%
- GST: 18% on (brokerage + exchange charges)
- Stamp duty: 0.015%
- SEBI charges: 0.0001%

Sell Side:
- Brokerage: 0.03% or ₹20 (whichever lower)
- STT: 0.1%
- Exchange charges: 0.00325%
- GST: 18% on (brokerage + exchange charges)
- SEBI charges: 0.0001%

Total Round Trip: ~0.3-0.5%
```

### Market Hours
- Pre-market: 9:00 AM - 9:15 AM IST
- Regular session: 9:15 AM - 3:30 PM IST
- Post-market: 3:40 PM - 4:00 PM IST

## Testing

### Unit Tests
```bash
pytest tests/
```

### Backtesting Validation
```bash
python -m backtesting.engine
```

## Important Notes

⚠️ **Disclaimer**: This system is for educational and research purposes only. Always:
1. Start with paper trading
2. Test thoroughly on historical data
3. Understand all components before using real money
4. Monitor performance continuously
5. Adjust for changing market conditions

## Production Deployment

For production use:
1. Set up data refresh schedule (daily at 4:00 PM IST)
2. Implement proper logging and monitoring
3. Add alerting for risk limit breaches
4. Use real-time data feeds (not just EOD)
5. Implement circuit breakers
6. Add disaster recovery procedures

## Performance Optimization

- Data caching with Parquet format
- Numba JIT compilation for indicators
- Vectorized backtesting
- Parallel processing for multiple stocks
- Efficient memory management

## Future Enhancements

- [ ] Real-time data integration
- [ ] Interactive dashboard with Plotly
- [ ] Walk-forward analysis
- [ ] LSTM for sequential pattern learning
- [ ] Options strategies integration
- [ ] API for live trading
- [ ] Mobile alerts
- [ ] Performance reports

## Support

For issues, questions, or contributions:
- Create an issue on GitHub
- Read the documentation
- Check examples in each module

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Yahoo Finance for data
- NSE/BSE for market data
- Open source libraries: pandas, numpy, scikit-learn, XGBoost

---

**Built with ❤️ for Indian equity traders**
