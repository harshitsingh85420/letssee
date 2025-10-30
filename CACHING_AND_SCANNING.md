# 💾 Data Caching & Full Stock Scanning

## ✅ Caching is Built-In!

The system **automatically caches** all BSE data downloads. You don't need to do anything!

### How It Works:

**First Run (Training):**
```cmd
python run_stock_picker.py --mode train --stocks 50
```
```
📥 Downloading BSE data from 2024-01-01 to 2025-10-30...
  bhav 2024-01-02 → 3,245 stocks
  bhav 2024-01-03 → 3,268 stocks
  ... (3-5 minutes)
💾 Caching data to: bhav_20240101_20251030.pkl
```

**Second Run (Same Day/Next Run):**
```cmd
python run_stock_picker.py --mode train --stocks 50
```
```
✅ Loading from cache: bhav_20240101_20251030.pkl
(Loads in 5-10 seconds!)
```

### Cache Location:
```
stock_picker_data/
└── cache/
    └── bse/
        └── bhav_20240101_20251030.pkl  (your cached data)
```

---

## 🎯 Scanning ALL Stocks (Complete Universe)

The system **automatically scans ALL stocks** when you run predictions!

### Default Behavior:

```cmd
python run_stock_picker.py --mode predict
```

**What Happens:**
1. ✅ Builds universe from ALL NSE indices (~500-700 stocks)
2. ✅ Downloads latest data for ALL stocks (from cache if available)
3. ✅ Applies risk filters (liquidity, price, F&O ban)
4. ✅ Computes features for ALL qualified stocks
5. ✅ Runs ML model on ALL stocks
6. ✅ Shows which stocks pass algo criteria
7. ✅ Returns top 15 picks

### Output Shows Everything:

```
======================================================================
STEP 1: Building Stock Universe
----------------------------------------------------------------------
🎯 Target universe: 523 stocks
📊 Sources: Nifty 50, Next 50, Midcap 100, Smallcap 250

----------------------------------------------------------------------
STEP 2: Downloading Historical Data
----------------------------------------------------------------------
✅ Loading from cache: bhav_20231101_20251030.pkl (FAST!)
✅ Downloaded: 487/523 stocks
❌ Failed/Insufficient data: 36 stocks

----------------------------------------------------------------------
STEP 3: Applying Risk Filters
----------------------------------------------------------------------
📊 Filter summary:
   • Started with: 487 stocks
   • Filtered out: 152 stocks (low liquidity, wrong price range, F&O ban)
   • ✅ Passed all filters: 335 stocks

----------------------------------------------------------------------
STEP 4: Computing Features & Making Predictions
----------------------------------------------------------------------
🔬 Processing 335 stocks with 42 features each...
Analyzing stocks: 100%|██████████| 335/335 [01:23<00:00, 4.0stock/s]
✅ Generated predictions for 335 stocks

----------------------------------------------------------------------
STEP 5: Auto-Threshold Adjustment (Finding Best Picks)
----------------------------------------------------------------------
📊 Probability distribution:
   • Max probability: 0.7842
   • Mean probability: 0.4523
   • Min probability: 0.1234

🎯 Searching for 15 picks (threshold: 0.62 → 0.52):
   🔍 Threshold 0.62: 8 picks
   🔍 Threshold 0.60: 12 picks
   ✅ Threshold 0.58: 17 picks

✅ Final threshold: 0.58 with 17 picks
```

**You can see:**
- How many stocks started (523)
- How many got filtered out (152)
- Why they were filtered (liquidity, price, F&O ban)
- How many passed criteria (335)
- Final picks (15)

---

## 📊 Understanding the Filters (Algo Criteria)

### 1. **Data Availability Filter**
- ✅ Stock must have sufficient historical data
- ❌ Removes: Newly listed stocks, delisted stocks

### 2. **F&O Ban Filter**
- ✅ Stock not in F&O ban period
- ❌ Removes: Stocks currently banned from F&O trading

### 3. **Liquidity Filter**
- ✅ Average daily turnover ≥ ₹20 lakh
- ❌ Removes: Low-liquidity, hard-to-trade stocks

### 4. **Price Range Filter**
- ✅ Stock price between ₹10 and ₹50,000
- ❌ Removes: Penny stocks, extremely expensive stocks

### 5. **ML Model Prediction**
- ✅ Probability score ≥ threshold (0.62 → 0.52)
- ❌ Removes: Low-probability predictions
- 🎯 Picks: Top 15 stocks with highest probabilities

---

## 🎮 Common Commands

### Train on ALL available data:
```cmd
python run_stock_picker.py --mode train --stocks 500
```
(Uses cache if available - fast!)

### Scan ALL stocks for daily picks:
```cmd
python run_stock_picker.py --mode predict
```
(Default behavior - scans complete universe)

### Force re-download (ignore cache):
```cmd
# Delete cache directory
rm -rf stock_picker_data/cache/bse/
# Then run as normal
python run_stock_picker.py --mode train --stocks 50
```

### View cache size:
```cmd
ls -lh stock_picker_data/cache/bse/
```

---

## 💡 Performance Tips

### First Time Setup:
1. Train with 50 stocks (fast, 5-10 min)
2. Data gets cached automatically
3. Next training uses cache (10 seconds!)
4. Predictions are always fast with cache

### Daily Workflow:
```cmd
# Morning routine (assuming model trained):
python run_stock_picker.py --mode predict

# Output:
# ✅ Loading from cache (instant!)
# ✅ Processed 335 stocks
# 🎯 Top 15 picks ready!
```

### Weekly Retraining:
```cmd
# Weekend - retrain with more stocks:
python run_stock_picker.py --mode train --stocks 200

# Uses cached BSE data - only ML training takes time
```

---

## ❓ FAQ

**Q: Does it scan all ~500 stocks every time?**
A: YES! By default, predicts mode scans ALL stocks in the universe.

**Q: Is the data re-downloaded every time?**
A: NO! Data is cached. First download takes 3-5 min, subsequent runs load from cache in 5-10 seconds.

**Q: Can I see which stocks failed the filters?**
A: YES! The output shows filter progression at each step.

**Q: How do I know if a stock passed the algo criteria?**
A: Check the "Passed all filters" count and final picks. Only stocks passing ALL criteria get predictions.

**Q: Where are the picks saved?**
A: `stock_picker_data/results/picks_YYYY-MM-DD_HH-MM-SS.csv`

**Q: How often should I retrain?**
A: Weekly recommended. Cache makes it fast!

---

## 🎯 You're All Set!

**Caching:** ✅ Automatic
**Scanning:** ✅ All stocks by default
**Filters:** ✅ Clear output shows what passed
**Performance:** ✅ Fast after first run

Just run:
```cmd
python run_stock_picker.py --mode train --stocks 50
python run_stock_picker.py --mode predict
```

And watch the magic happen! 🚀
