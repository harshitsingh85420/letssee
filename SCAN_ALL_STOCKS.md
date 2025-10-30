# 🎯 Scan ALL Stocks - Complete Guide

**Your system now scans ALL NSE stocks (500+) to find the absolute BEST picks!**

---

## ⚡ Quick Commands

### **Scan ALL Stocks (Recommended)**

```cmd
REM Train model first (one time)
python run_stock_picker.py --mode train --stocks 100

REM Scan ALL stocks and get top 15 picks
python run_stock_picker.py --mode predict
```

**This will:**
- ✅ Scan 500+ NSE stocks automatically
- ✅ Apply risk filters (liquidity, F&O ban, price)
- ✅ Compute features for all stocks
- ✅ Find the BEST 15 picks from entire market
- ✅ Auto-adjust threshold to get quality picks

---

## 📊 What You Get

### **Stock Universe Coverage:**

| Category | Stocks | Included |
|----------|--------|----------|
| **Nifty 50** | 50 | ✅ Yes |
| **Nifty Next 50** | 50 | ✅ Yes |
| **Nifty Midcap 100** | 100 | ✅ Yes |
| **Nifty Smallcap** | 250+ | ✅ Yes |
| **Total Coverage** | **500+** | **✅ All scanned!** |

---

## 🚀 Complete Workflow

### **Step 0: Install Packages (One Time)**

```cmd
pip install -r requirements.txt
```

**Or directly:**
```cmd
pip install numpy pandas yfinance lightgbm scikit-learn requests beautifulsoup4 tqdm joblib imbalanced-learn python-dateutil pytz numba plotly
```

### **Step 1: Train Model (One Time)**

```cmd
REM Quick training (20-50 stocks, 5 minutes)
python run_stock_picker.py --mode train --stocks 50

REM Better model (100 stocks, 10 minutes)
python run_stock_picker.py --mode train --stocks 100

REM Best model (500 stocks, 30-45 minutes)
python run_stock_picker.py --mode train --stocks 500
```

**What happens:**
- Downloads historical data (2 years)
- Computes features (50+ indicators)
- Trains LightGBM model
- Saves model for reuse

**You only need to do this ONCE** (or retrain weekly/monthly)

### **Step 2: Scan ALL Stocks Daily**

```cmd
python run_stock_picker.py --mode predict
```

**What happens:**
- 🎯 Builds universe of 500+ stocks
- 📥 Downloads latest data for ALL
- 🛡️ Applies risk filters (removes unsafe stocks)
- 🔬 Computes features for each stock
- 🤖 Predicts probability for ALL stocks
- 🏆 Auto-adjusts threshold (0.62→0.52)
- 📊 Shows top 15 BEST picks

**Time:** 3-5 minutes (first run), 1-2 minutes (cached)

---

## ⏱️ Performance Expectations

### **First Run (No Cache):**
- Universe building: 30 seconds
- Data download (500+ stocks): 3-4 minutes
- Risk filters: 10 seconds
- Feature computation: 1-2 minutes
- Predictions: 30 seconds
- **Total: ~5-7 minutes**

### **Subsequent Runs (With Cache):**
- Universe building: 10 seconds
- Data download (only new data): 30 seconds
- Risk filters: 5 seconds
- Feature computation: 30 seconds
- Predictions: 20 seconds
- **Total: ~1-2 minutes**

---

## 🎯 Output Example

```
🔮 GENERATING DAILY PREDICTIONS - SCANNING ALL STOCKS
======================================================================

Building comprehensive NSE stock universe...
✅ Built universe: 523 stocks
🎯 Scanning 523 stocks to find the BEST picks

Downloading 523 stocks...
Downloaded 487/523 stocks
Applying risk filters...
Liquidity filter: 342/487 stocks passed
Price filter: 315/342 stocks passed
Final universe: 315 stocks

Computing features and making predictions...
[Progress bar]

Threshold 0.62: 8 picks
Threshold 0.60: 12 picks
Threshold 0.58: 17 picks

🏆 TOP STOCK PICKS
================================================================================
Rank  Symbol         Probability    Price       5D Return %
================================================================================
1     DIXON.NS       0.7856        ₹6234.50    3.45
2     TITAN.NS       0.7634        ₹3456.75    2.87
3     BAJFINANCE.NS  0.7512        ₹7234.20    1.92
4     TATAELXSI.NS   0.7423        ₹8765.30    4.12
5     LTTS.NS        0.7389        ₹4532.15    2.34
6     HDFCBANK.NS    0.7156        ₹1645.80    1.67
7     RELIANCE.NS    0.7089        ₹2567.45    -0.34
8     TCS.NS         0.6934        ₹3789.60    2.12
9     INFY.NS        0.6845        ₹1534.25    1.89
10    ICICIBANK.NS   0.6789        ₹1123.45    0.98
11    ASIANPAINT.NS  0.6723        ₹2987.60    -1.23
12    WIPRO.NS       0.6689        ₹445.75     1.45
13    COFORGE.NS     0.6634        ₹5432.10    3.67
14    PERSISTENT.NS  0.6598        ₹5678.90    2.89
15    LTIM.NS        0.6567        ₹5234.50    1.98
================================================================================

💾 Saved to: ./stock_picker_data/results/picks_2025-10-29_18-30-45.csv

✅ DONE!
```

---

## 🔧 Advanced Options

### **Limit Scan (For Testing)**

```cmd
REM Scan only 100 stocks (faster for testing)
python run_stock_picker.py --mode predict --scan-limit 100
```

### **Train and Predict Together**

```cmd
REM Train with 200 stocks, then scan ALL for predictions
python run_stock_picker.py --mode both --stocks 200
```

### **Custom Data Directory**

```cmd
python run_stock_picker.py --mode predict --data-dir "D:\trading_data"
```

---

## 💡 How It Finds the BEST Stocks

### **1. Universe (500+ stocks)**
Starts with comprehensive NSE coverage

### **2. Risk Filters**
Removes:
- ❌ Stocks in F&O ban
- ❌ Low liquidity (< ₹20L daily turnover)
- ❌ Too cheap (< ₹10) or expensive (> ₹50,000)

**Result:** ~200-350 safe stocks

### **3. Feature Computation**
For each remaining stock:
- 50+ technical indicators
- Volatility measures
- Candlestick patterns
- 5-session specific features

### **4. ML Prediction**
LightGBM predicts probability of gaining ≥1.5% in next 5 sessions

### **5. Auto-Threshold**
- Starts at 0.62 (high confidence)
- Reduces to 0.60, 0.58, 0.56, 0.54, 0.52
- Stops when ≥15 picks found

**Result:** Top 15 BEST stocks from entire market

---

## 📈 Optimization Tips

### **For Speed:**

1. **Cache Helps A Lot**
   - First run: 5-7 minutes
   - Second run: 1-2 minutes
   - System caches downloaded data

2. **Run During Off-Peak Hours**
   - yfinance sometimes rate-limits
   - Early morning or late night = faster

3. **Parallel Downloads**
   - System uses 4 parallel workers
   - Adjust in `stock_picker_pipeline.py` if needed

### **For Better Picks:**

1. **Train with More Stocks**
   ```cmd
   python run_stock_picker.py --mode train --stocks 500
   ```

2. **Retrain Regularly**
   - Weekly: Good
   - Monthly: Minimum
   - After major market moves: Recommended

3. **Track Performance**
   - Keep CSV files
   - Compare predictions vs actual results
   - Adjust threshold based on win rate

---

## 🎯 Best Practices

### **Daily Routine:**

```cmd
REM Every trading day at 9:00 AM
cd C:\Users\CRL\Desktop\harshit\accouting\letssee
venv\Scripts\activate.bat
python run_stock_picker.py --mode predict
```

### **Weekly Routine:**

```cmd
REM Every Sunday
python run_stock_picker.py --mode train --stocks 200
```

### **Monthly Routine:**

```cmd
REM First Sunday of month - comprehensive retraining
python run_stock_picker.py --mode train --stocks 500
```

---

## 🐛 Troubleshooting

### **"Too Slow"**

```cmd
REM First run is always slow (downloading data)
REM Wait for cache to build
REM Next runs will be much faster

REM Or limit scan for testing
python run_stock_picker.py --mode predict --scan-limit 100
```

### **"Some stocks failed to download"**

This is normal:
- yfinance has rate limits
- Some stocks may be delisted
- System continues with others
- Usually 80-90% success rate is good

### **"Memory error"**

```cmd
REM Your computer might need more RAM
REM Reduce stocks:
python run_stock_picker.py --mode predict --scan-limit 200
```

---

## 📊 Understanding Results

### **Probability Scores:**

| Range | Meaning | Action |
|-------|---------|--------|
| **>0.70** | Very High Confidence | Strong Buy Signal |
| **0.65-0.70** | High Confidence | Good Buy Signal |
| **0.60-0.65** | Medium-High | Consider |
| **0.55-0.60** | Medium | Watch |
| **<0.55** | Low | Skip |

### **5D Return %:**
- Shows recent momentum
- Positive = Trending up
- Negative = Trending down
- Model considers both trending up and down stocks

---

## ⚠️ Important Notes

1. **Market Hours**
   - Best to run after market close (3:30 PM)
   - Data updates by 4:00 PM
   - Run anytime after 4 PM for next day

2. **Weekends/Holidays**
   - System works anytime
   - Uses most recent market data
   - Good time for retraining

3. **Not Financial Advice**
   - This is a tool, not a guarantee
   - Always do your own analysis
   - Consult SEBI-registered advisor
   - Paper trade first!

---

## 🎉 Summary

**You asked for:** Scan ALL stocks and get the BEST

**You now have:**
- ✅ Scans 500+ NSE stocks automatically
- ✅ Applies comprehensive risk filters
- ✅ Uses 50+ technical indicators
- ✅ ML-powered probability scores
- ✅ Auto-threshold for quality picks
- ✅ Top 15 BEST stocks from entire market

**Simple command:**
```cmd
python run_stock_picker.py --mode predict
```

**Result:** Top 15 stock picks from scanning 500+ stocks! 🎯

---

**Ready to find the BEST stocks?** Run it now! 🚀
