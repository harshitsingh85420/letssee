# 🎯 START HERE - Foolproof Setup

**Follow these exact steps. Copy-paste commands. Takes 5 minutes.**

## 🧠 How This System Works

The stock picker uses **machine learning** to learn from historical patterns:

1. 📊 **Trains on 2 years of data** (up to TODAY) - learns which indicator patterns preceded 5-session gains
2. 🔮 **Predicts from today's indicators** - finds stocks matching past winners
3. 🔄 **Retrains daily** with latest data - model adapts and self-corrects

**💡 Recommended: Use `--mode daily` to retrain + predict every day!**

**See [DAILY_RETRAINING.md](DAILY_RETRAINING.md) for full explanation.**

---

## ✅ Step 1: Pull Latest Code

```cmd
cd path\to\letssee
git pull origin claude/indian-equity-trading-system-011CUX7MGPY37GwYWmG29cb6
```

**Replace `path\to\letssee` with your actual project path**

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

📂 Loading trained model...
✅ Model loaded with 42 features

----------------------------------------------------------------------
STEP 1: Building Stock Universe
----------------------------------------------------------------------
🎯 Target universe: 523 stocks
📊 Sources: Nifty 50, Next 50, Midcap 100, Smallcap 250

----------------------------------------------------------------------
STEP 2: Downloading Historical Data
----------------------------------------------------------------------
📅 Date range: 2023-10-31 to 2025-10-30 (730 days)
Downloading: 100%|████████████| 523/523 [02:34<00:00, 3.4stock/s]
✅ Downloaded: 487/523 stocks
❌ Failed/Insufficient data: 36 stocks

----------------------------------------------------------------------
STEP 3: Applying Risk Filters
----------------------------------------------------------------------
📊 Filter summary:
   • Started with: 487 stocks
   • Filtered out: 152 stocks
   • ✅ Passed all filters: 335 stocks

----------------------------------------------------------------------
STEP 4: Computing Features & Making Predictions
----------------------------------------------------------------------
🔬 Processing 335 stocks with 42 features each...
Analyzing stocks: 100%|██████| 335/335 [01:23<00:00, 4.0stock/s]
✅ Generated predictions for 335 stocks

----------------------------------------------------------------------
STEP 5: Filtering by Threshold (Finding ALL Qualifying Stocks)
----------------------------------------------------------------------
📊 Probability distribution:
   • Max probability: 0.7842
   • Mean probability: 0.4523
   • Min probability: 0.1234

🎯 Applying thresholds to find ALL qualifying stocks:
   🔍 Threshold 0.62: 23 stocks qualify
   🔍 Threshold 0.60: 35 stocks qualify
   🔍 Threshold 0.58: 47 stocks qualify

✅ Final threshold: 0.62
✅ Total qualifying stocks: 23
📊 Note: Showing ALL stocks that pass the criteria (from penny stocks to expensive)

================================================================================
🏆 ALL 23 QUALIFYING STOCK PICKS FOR 2025-10-30
================================================================================

📊 Qualifying Stocks Statistics:
   • Total qualifying stocks: 23
   • Average probability: 0.6734
   • Highest probability: 0.7842
   • Lowest probability: 0.6201
   • Price range: ₹12.50 to ₹6,234.50
   • Average price: ₹1,234.56
   • Average 5D return: 2.34%

--------------------------------------------------------------------------------

Rank  Symbol         Probability    Price       Volume(20D)    5D Return%
================================================================================
1     DIXON.NS       0.7856        ₹6234.50    15.23M         3.45
2     TITAN.NS       0.7634        ₹3456.75    8.67M          2.87
3     BAJFINANCE.NS  0.7512        ₹7234.20    12.45M         1.92
...
15    LTIM.NS        0.6567        ₹5234.50    3.21M          1.98
================================================================================

💾 Results saved to: ./stock_picker_data/results/picks_2025-10-30_14-40-09.csv
📁 Full results directory: ./stock_picker_data/results

================================================================================
✅ PREDICTION COMPLETE!
================================================================================
📊 Scanned: 523 stocks
✅ Generated predictions: 335 stocks
🎯 Qualifying stocks (passed all criteria): 23 stocks
📊 Price range included: Penny stocks to expensive (no limits)
⚠️  Note: This is for educational purposes only. Always do your own research!
================================================================================
```

---

## 🎉 That's It!

You now have:
- ✅ Fully trained model
- ✅ ALL qualifying stock picks from scanning 500+ stocks (zero limits!)
- ✅ Includes all prices (₹1 to ₹50,000+), all volumes, all liquidity levels
- ✅ Picks saved to CSV file

---

## 📅 Daily Use (Recommended)

**🔥 Option 1: Daily Retraining (Best Results)**

```cmd
cd path\to\letssee
python run_stock_picker.py --mode daily --stocks 100
```

- Retrains model with today's data
- Model learns latest patterns and self-corrects
- Takes 5-10 min first run, 2-3 min cached
- **Recommended for best accuracy!**

**⚡ Option 2: Quick Prediction (Faster)**

```cmd
cd path\to\letssee
python run_stock_picker.py --mode predict
```

- Uses yesterday's saved model
- Takes 1-2 minutes
- Good for quick checks, but model doesn't adapt

**💡 See [DAILY_RETRAINING.md](DAILY_RETRAINING.md) to understand why daily retraining gives better results!**

**Replace `path\to\letssee` with your actual project path**

---

## 🔄 Weekly Deep Retraining (Optional)

```cmd
python run_stock_picker.py --mode train --stocks 500
```

Train on more stocks (500 vs 100) for more comprehensive model. Do this monthly.

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
