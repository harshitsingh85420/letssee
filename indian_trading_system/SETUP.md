# Setup Guide - Indian Equity Trading System

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (for version control)
- 4GB+ RAM recommended
- Stable internet connection for data downloads

## Installation Steps

### 1. Clone or Navigate to the Project

```bash
cd indian_trading_system
```

### 2. Create Virtual Environment

**On Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install:
- yfinance (data collection)
- pandas, numpy (data manipulation)
- scikit-learn, xgboost (machine learning)
- numba (performance optimization)
- plotly, matplotlib, seaborn (visualization)
- And other dependencies

### 4. Verify Installation

```bash
python -c "import pandas, numpy, sklearn, xgboost, numba; print('All dependencies installed successfully!')"
```

## Quick Test

### Test 1: Data Loading

```bash
cd indian_trading_system
python -c "from data.loader import DataLoader; loader = DataLoader(); df = loader.load_stock_data('RELIANCE.NS'); print(f'Loaded {len(df)} rows')"
```

Expected output: "Loaded XXX rows" (should be 700+ rows)

### Test 2: Run Examples

```bash
python example_usage.py
```

This will run through all the basic examples and verify that the system works.

### Test 3: Run Main Script

```bash
python main.py
```

This will:
1. Download data for top 10 NIFTY stocks
2. Calculate indicators
3. Train ML models
4. Generate signals
5. Run backtests

**Note:** First run will take 5-10 minutes as it downloads and caches data. Subsequent runs will be much faster.

## Directory Structure After Setup

```
indian_trading_system/
├── data/
│   ├── storage/           # Created automatically - cache files
│   ├── loader.py
│   └── cleaner.py
├── indicators/
├── models/
├── backtesting/
├── portfolio/
├── utils/
├── visualization/
├── tests/
├── main.py
├── example_usage.py
├── requirements.txt
├── README.md
└── SETUP.md
```

## Common Issues and Solutions

### Issue 1: NumPy/Pandas Version Conflicts

**Error:** `ImportError: numpy.core.multiarray failed to import`

**Solution:**
```bash
pip uninstall numpy pandas
pip install numpy==1.24.0 pandas==2.0.0
```

### Issue 2: XGBoost Installation Fails

**Error:** `ERROR: Could not build wheels for xgboost`

**Solution (Linux/Mac):**
```bash
# Install build tools
sudo apt-get install build-essential  # Ubuntu/Debian
brew install gcc  # Mac

pip install xgboost
```

**Solution (Windows):**
```bash
# Install Visual C++ Build Tools
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
pip install xgboost
```

### Issue 3: Numba Installation Issues

**Error:** `ImportError: Numba could not be imported`

**Solution:**
```bash
pip install numba==0.57.0 --no-cache-dir
```

### Issue 4: Yahoo Finance Connection Issues

**Error:** `Connection timeout` or `No data returned`

**Solution:**
- Check internet connection
- Try again after a few minutes (Yahoo Finance rate limiting)
- Use force_download=True to bypass cache

```python
loader.load_stock_data('RELIANCE.NS', force_download=True)
```

### Issue 5: Memory Issues

**Error:** `MemoryError` during ML training

**Solution:**
- Use smaller stock universe (TOP_10_NIFTY instead of NIFTY_50)
- Reduce ML training data
- Close other applications

## Performance Optimization

### 1. Enable Numba JIT Compilation

Numba is automatically used for volatility calculations. To verify:

```python
from indicators.volatility import VolatilityEstimators
# If no errors, Numba is working correctly
```

### 2. Configure Data Caching

Data is automatically cached in `data/storage/` as Parquet files.

To clear cache:
```python
from data.loader import DataLoader
loader = DataLoader()
loader.clear_cache()  # Clear all
loader.clear_cache('RELIANCE.NS')  # Clear specific stock
```

### 3. Parallel Processing

The system automatically uses all CPU cores for:
- Multiple stock processing
- Random Forest training
- XGBoost training

## Configuration

### Customize Stock Universe

Edit `utils/constants.py`:

```python
# Use custom stock list
CUSTOM_STOCKS = [
    'RELIANCE.NS', 'TCS.NS', 'INFY.NS',
    # Add your stocks here
]
```

Then in your code:
```python
from utils.constants import CUSTOM_STOCKS
system = TradingSystem(symbols=CUSTOM_STOCKS)
```

### Adjust Risk Parameters

Edit `utils/constants.py`:

```python
MAX_POSITIONS = 10  # Maximum positions
STOP_LOSS_PCT = 0.03  # 3% stop loss
MAX_POSITION_SIZE = 0.25  # 25% max per position
```

### Change ML Parameters

Edit `utils/constants.py`:

```python
RF_N_ESTIMATORS = 100  # Random Forest trees
XGB_LEARNING_RATE = 0.1  # XGBoost learning rate
```

## Testing

### Run Unit Tests

```bash
# Install pytest if not already installed
pip install pytest

# Run tests
pytest tests/
```

### Run Specific Example

```bash
python -c "from example_usage import example_1_data_loading; example_1_data_loading()"
```

## Development Setup

### Install Development Dependencies

```bash
pip install jupyter ipython pytest black flake8
```

### Launch Jupyter Notebook

```bash
jupyter notebook
```

Then open `analysis.ipynb` (if created) or create your own notebook.

### Code Formatting

```bash
# Format code
black indian_trading_system/

# Check style
flake8 indian_trading_system/
```

## Production Deployment

### 1. Set Up Scheduled Tasks

**Linux/Mac (cron):**
```bash
# Edit crontab
crontab -e

# Add daily data update at 4:30 PM IST
30 16 * * 1-5 cd /path/to/indian_trading_system && python main.py
```

**Windows (Task Scheduler):**
- Open Task Scheduler
- Create new task
- Set trigger: Daily at 4:30 PM, weekdays only
- Set action: Run `python main.py`

### 2. Enable Logging

Create `logging_config.py`:

```python
import logging

logging.basicConfig(
    filename='trading_system.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 3. Set Up Monitoring

Use system monitoring to track:
- Daily data updates
- Signal generation
- Risk limit breaches
- System errors

## Getting Help

- Check README.md for usage examples
- Review example_usage.py for code samples
- Check module docstrings: `help(DataLoader)`
- Create issue on GitHub for bugs

## Next Steps

1. Run `python example_usage.py` to verify setup
2. Run `python main.py` for complete workflow
3. Review README.md for detailed documentation
4. Customize configuration in `utils/constants.py`
5. Start with paper trading before using real money

## Security Notes

- Never commit API keys or credentials to Git
- Use environment variables for sensitive data
- Keep your trading strategies private
- Regular backups of configuration and models

## Performance Benchmarks

On a typical system (i5/Ryzen 5, 8GB RAM):
- Data loading (10 stocks): 30-60 seconds (first time), <5 seconds (cached)
- Indicator calculation (10 stocks): 10-20 seconds
- ML training (1 stock, 3 years data): 2-5 minutes
- Backtesting (1 stock): <1 second
- Complete workflow (10 stocks): 5-10 minutes

## Support

For issues or questions:
- Review this setup guide
- Check README.md
- Examine example_usage.py
- Search existing issues
- Create new issue with details

---

**Ready to trade? Start with `python main.py`!**
