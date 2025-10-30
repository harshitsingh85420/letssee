# 🎯 START HERE - Foolproof Setup

**Follow these exact steps. Copy-paste commands. Takes 5 minutes.**

---

## ✅ Step 1: Pull Latest Code

```cmd
cd C:\Users\CRL\Desktop\harshit\accouting\letssee
git pull origin claude/indian-equity-trading-system-011CUX7MGPY37GwYWmG29cb6
```

---

## ✅ Step 2: Install Packages

**Copy-paste this ENTIRE command:**

```cmd
pip install -r requirements.txt
```

**If that worked:** Skip to Step 3

**If you got an error:** Use this instead:

```cmd
pip install numpy pandas yfinance lightgbm scikit-learn requests beautifulsoup4 tqdm joblib imbalanced-learn python-dateutil pytz numba plotly
```

---

## ✅ Step 3: Train Model (5-10 minutes)

```cmd
python run_stock_picker.py --mode train --stocks 50
```

**You'll see:**
```
🎓 TRAINING NEW MODEL
Building comprehensive NSE stock universe...
✅ Built universe: 523 stocks
Training on up to 50 stocks

Downloading 50 stocks...
[Progress bar]
Downloaded 45/50 stocks

Applying risk filters...
Final universe: 42 stocks

Computing features and preparing ML dataset...
Dataset: 8543 samples, 87 features
Positive samples: 1234 (14.4%)

Training LightGBM model...
✅ Model training complete!
Model saved: ./stock_picker_data/models/5session_model.txt

✅ DONE!
```

---

## ✅ Step 4: Scan ALL Stocks (5 minutes)

```cmd
python run_stock_picker.py --mode predict
```

**You'll see:**
```
🔮 GENERATING DAILY PREDICTIONS - SCANNING ALL STOCKS
======================================================================

Building comprehensive NSE stock universe...
✅ Built universe: 523 stocks
🎯 Scanning 523 stocks to find the BEST picks

Downloading 523 stocks...
[Progress bar]
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
...
15    LTIM.NS        0.6567        ₹5234.50    1.98
================================================================================

💾 Saved to: ./stock_picker_data/results/picks_2025-10-29_19-30-45.csv

✅ DONE!
```

---

## 🎉 That's It!

You now have:
- ✅ Fully trained model
- ✅ Top 15 stock picks from scanning 500+ stocks
- ✅ Picks saved to CSV file

---

## 📅 Daily Use (Every Morning)

```cmd
cd C:\Users\CRL\Desktop\harshit\accouting\letssee
venv\Scripts\activate.bat
python run_stock_picker.py --mode predict
```

Takes 1-2 minutes after first run (cached).

---

## 🔄 Retrain Model (Weekly)

```cmd
python run_stock_picker.py --mode train --stocks 100
```

---

## 🐛 If You Get Errors

### **"No trained model found"**
```cmd
python run_stock_picker.py --mode train --stocks 50
```

### **"Package not found"**
```cmd
pip install numpy pandas yfinance lightgbm scikit-learn requests beautifulsoup4 tqdm joblib
```

### **"Import error"**
```cmd
python -c "import pandas, numpy, lightgbm; print('Packages OK')"
```

If this works, your packages are fine. Error is something else.

---

## 📊 Files Created

After running, you'll have:

```
stock_picker_data/
├── models/
│   ├── 5session_model.txt           # Your trained model
│   └── 5session_model_features.json # Feature names
├── results/
│   └── picks_2025-10-29_19-30-45.csv # Your stock picks
└── cache/
    └── joblib/                       # Cached downloads
```

---

## ✅ Success Checklist

- [ ] Git pulled latest code
- [ ] Packages installed (no errors)
- [ ] Model trained (5-10 minutes)
- [ ] Predictions generated (5 minutes)
- [ ] CSV file created with picks
- [ ] Ready for daily use!

---

## 🚀 Next Steps

Read the detailed guides:
- **SCAN_ALL_STOCKS.md** - How the scanning works
- **QUICK_START.md** - Daily usage guide
- **LOCAL_SETUP_GUIDE.md** - Complete setup guide

---

**Any issues? Share the exact error message and I'll help!**
