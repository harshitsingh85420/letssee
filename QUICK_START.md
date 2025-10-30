# 🚀 Quick Start Guide - 5-Session Stock Picker

**Your system is now fully functional!** This guide shows you how to use it.

---

## ✅ What You Have Now

You have **TWO ways** to run the system:

1. **Standalone Python Script** (Recommended for daily use)
2. **Jupyter Notebook** (Good for learning and experimentation)

---

## 🎯 Option 1: Standalone Python Script (Production Ready)

### **Quick Test (Start Here)**

```cmd
REM Train a small model first (uses 20 stocks, takes 2-3 minutes)
python run_stock_picker.py --mode train --stocks 20

REM Generate predictions
python run_stock_picker.py --mode predict

REM Or do both
python run_stock_picker.py --mode both --stocks 20
```

### **Production Usage**

```cmd
REM Train with more stocks (better accuracy)
python run_stock_picker.py --mode train --stocks 100

REM Daily: Generate picks (uses saved model)
python run_stock_picker.py --mode predict

REM Save to custom location
python run_stock_picker.py --mode predict --data-dir "D:\trading_data"
```

### **What It Does:**

**Training Mode** (`--mode train`):
1. ✅ Downloads stock data (2 years history)
2. ✅ Applies risk filters (liquidity, price range, F&O ban)
3. ✅ Computes 50+ technical features
4. ✅ Trains LightGBM model
5. ✅ Saves model to `stock_picker_data/models/`

**Prediction Mode** (`--mode predict`):
1. ✅ Loads trained model
2. ✅ Downloads latest stock data
3. ✅ Computes features
4. ✅ Generates predictions
5. ✅ Auto-adjusts threshold (starts at 0.62)
6. ✅ Displays ALL qualifying stocks (no limits!)
7. ✅ Includes penny stocks to expensive stocks
8. ✅ Saves to CSV in `stock_picker_data/results/`

---

## 🎓 Option 2: Jupyter Notebook (Interactive)

### **Start Jupyter:**

```cmd
jupyter notebook
```

### **In Browser:**
1. Navigate to `5Session_Stock_Picker_Production.ipynb`
2. Run cells one by one to understand the system
3. Experiment with parameters
4. Good for learning!

---

## ⚡ First Time Setup (5 Minutes)

### **0. Install Packages (One Time)**

```cmd
pip install -r requirements.txt
```

**Or install directly:**
```cmd
pip install numpy pandas yfinance lightgbm scikit-learn requests beautifulsoup4 tqdm joblib imbalanced-learn python-dateutil pytz numba plotly
```

### **1. Quick Test with 10 Stocks:**

```cmd
python run_stock_picker.py --mode train --stocks 10
```

**What to expect:**
- Downloads 10 stocks (30 seconds)
- Computes features (30 seconds)
- Trains model (1 minute)
- Shows training summary

### **2. Generate First Predictions:**

```cmd
python run_stock_picker.py --mode predict
```

**You'll see:**
```
🏆 ALL 18 QUALIFYING STOCK PICKS
================================================================================

Rank  Symbol         Probability    Price       5D Return %
================================================================================
1     RELIANCE.NS    0.7234        ₹2456.50    2.34
2     TCS.NS         0.7012        ₹3678.20    1.89
3     HDFCBANK.NS    0.6845        ₹1534.75    -0.45
...
18    PENNYSTOCK.NS  0.6201        ₹15.50      3.21
================================================================================

📊 Qualifying stocks: 18 (from penny stocks to expensive)
💾 Saved to: ./stock_picker_data/results/picks_2025-10-29_18-15-30.csv
```

---

## 📅 Daily Automation

### **Windows Task Scheduler:**

Create a batch file `run_daily_picks.bat`:

```batch
@echo off
cd path\to\letssee
python run_stock_picker.py --mode predict
pause
```

**Replace `path\to\letssee` with your actual project path**

Schedule it to run daily at 9:00 AM.

### **Manual Daily Run:**

```cmd
REM Every morning:
cd path\to\letssee
python run_stock_picker.py --mode predict
```

**Replace `path\to\letssee` with your actual project path**

---

## 🔧 Customization

### **Change Target Gain:**

Edit `stock_picker_pipeline.py`:

```python
self.TARGET_GAIN = 2.0  # Change from 1.5% to 2.0%
```

### **Change Holding Period:**

```python
self.HOLDING_PERIOD = 10  # Change from 5 to 10 sessions
```

### **Change Probability Threshold:**

```python
self.INITIAL_THRESHOLD = 0.70  # Change from 0.62 to 0.70 (stricter)
self.MIN_THRESHOLD = 0.60      # Change from 0.52 to 0.60
```

**Note:** System shows ALL stocks that pass criteria - no artificial limits on count or price!

---

## 📁 Directory Structure

After running, you'll have:

```
stock_picker_data/
├── models/
│   ├── 5session_model.txt           # Trained LightGBM model
│   └── 5session_model_features.json # Feature names
├── results/
│   └── picks_2025-10-29_18-15-30.csv # Daily picks
├── cache/
│   └── joblib/                       # Cached downloads
└── data/
    └── stock_histories/              # Downloaded data
```

---

## 🐛 Troubleshooting

### **"No trained model found"**

```cmd
REM Train a model first
python run_stock_picker.py --mode train --stocks 50
```

### **"No stocks passed filters"**

- Market might be closed
- Try with fewer filters (edit `stock_picker_pipeline.py`)
- Check internet connection

### **"Error downloading..."**

- Normal for a few stocks
- System continues with others
- yfinance sometimes has rate limits

### **Slow Performance**

```cmd
REM Start with fewer stocks
python run_stock_picker.py --mode train --stocks 30
```

---

## 🎯 Recommended Workflow

### **Week 1: Testing**
```cmd
REM Day 1: Quick test
python run_stock_picker.py --mode train --stocks 10

REM Day 2-7: Generate predictions daily, don't trade yet
python run_stock_picker.py --mode predict
```

### **Week 2: Small Training**
```cmd
REM Weekend: Train with more stocks
python run_stock_picker.py --mode train --stocks 50

REM Weekdays: Generate picks
python run_stock_picker.py --mode predict
```

### **Week 3+: Production**
```cmd
REM Monthly: Retrain model
python run_stock_picker.py --mode train --stocks 100

REM Daily: Get picks
python run_stock_picker.py --mode predict
```

---

## 📊 Understanding the Output

### **Probability Column:**
- **>0.65**: High confidence
- **0.60-0.65**: Good confidence
- **0.55-0.60**: Moderate confidence
- **<0.55**: Lower confidence

### **5D Return %:**
- Recent 5-day performance
- Positive = trending up
- Negative = trending down

### **Number of Results:**
- Shows ALL stocks above probability threshold
- Could be 5 stocks, could be 50+ stocks
- No artificial limits on count
- Includes penny stocks to expensive stocks

### **Auto-Threshold:**
- Starts at 0.62 (high confidence only)
- Uses highest threshold that gives results
- Shows ALL stocks at that threshold level

---

## 💡 Tips

### **Best Practices:**

1. ✅ **Retrain weekly/monthly** with fresh data
2. ✅ **Start small** (10-20 stocks for testing)
3. ✅ **Paper trade first** (track without real money)
4. ✅ **Review picks** (don't blindly follow)
5. ✅ **Keep logs** (track performance over time)

### **Performance Tips:**

- First run is slow (downloads data)
- Subsequent runs are fast (uses cache)
- Train on weekend (takes longer)
- Predict daily (very fast)

### **Safety Tips:**

- ⚠️ Never invest more than you can afford to lose
- ⚠️ Diversify (don't put all money in one pick)
- ⚠️ Set stop losses
- ⚠️ This is a tool, not financial advice

---

## 🆘 Need Help?

### **Check These First:**

1. ✅ All packages installed? `pip list`
2. ✅ In correct directory? `cd letssee`
3. ✅ Virtual environment active? See `(venv)` in prompt
4. ✅ Internet connection working?

### **Common Commands:**

```cmd
REM Check what you have
python --version
pip list | findstr lightgbm

REM Test imports
python -c "from stock_picker_pipeline import *; print('OK')"

REM See help
python run_stock_picker.py --help
```

---

## 🎉 You're Ready!

Your trading system is fully functional. Start with:

```cmd
python run_stock_picker.py --mode train --stocks 20
python run_stock_picker.py --mode predict
```

And you'll see your first stock picks!

**Happy Trading!** 📈💰

---

**Remember:** This is for educational purposes. Always do your own research and consult a financial advisor before trading!
