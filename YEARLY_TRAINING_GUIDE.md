# Yearly Training System - Complete Guide

## 🎯 Overview

This system trains the 5-Session Stock Picker model on **every business day** in a year, allowing the model to learn from each date and continuously improve its predictions.

### Key Features

✅ **Comprehensive Caching** - Downloads data once, never again!
- Per-date BSE data caching
- Feature computation caching (saves 10-15 minutes per run)
- Smart cache reuse across runs

✅ **Yearly Training** - Train on all dates in a year
- Automatic tracking of trained dates
- Resume from interruptions
- Progress reporting

✅ **Model Versioning** - Smart model management
- Detects when model is updated
- Tracks training history
- Automatic retraining when needed

✅ **Incremental Learning** - Model learns from each date
- Saves model after each training date
- Builds knowledge over time
- Improves prediction accuracy

---

## 📊 How It Works

### 1. Data Download (One-Time Per Date)

```
First run: Downloads all dates in range
  ├─ 2024-01-01 → Downloaded → Cached ✅
  ├─ 2024-01-02 → Downloaded → Cached ✅
  └─ ... → Downloaded → Cached ✅

Second run: Uses cache (instant!)
  ├─ 2024-01-01 → From cache 📦
  ├─ 2024-01-02 → From cache 📦
  └─ Only new dates are downloaded!
```

### 2. Feature Computation (Cached)

```
First computation: ~10-15 minutes
  └─ Computes 50+ technical indicators
  └─ Cached for future ✅

Second run: < 1 second
  └─ Loads from cache 📦
```

### 3. Model Training

For each date in the year:
1. Fetches data up to that date (from cache!)
2. Computes features (from cache!)
3. Trains model using data before that date
4. Saves model with version tracking
5. Marks date as "trained" ✅

---

## 🚀 Quick Start

### Daily Stock Picking (Fast Mode)

```bash
# Run daily picks using existing model (fast!)
python run_5session_picker.py --stocks 500

# Force retrain if needed
python run_5session_picker.py --stocks 500 --retrain
```

This will:
- Load existing model (no training needed!)
- Fetch latest data (from cache if available)
- Generate today's stock picks
- **Takes ~30 seconds instead of 10 minutes!**

---

### Yearly Training

#### Train on Specific Year

```bash
# Train on all business days in 2024
python run_yearly_training.py --year 2024 --stocks 500
```

#### Train on Year Range

```bash
# Train on 2023-2024
python run_yearly_training.py --year-start 2023 --year-end 2024 --stocks 500
```

#### Check Training Status

```bash
# Show which dates have been trained
python run_yearly_training.py --status
```

Output:
```
================================================================================
📊 MODEL TRAINING STATUS
================================================================================

🤖 Model Version: 2024-11-06
   Last Updated: 2024-11-06
   Signature: a3f7b9c2d8e1f6a4...

📅 Training Progress by Year:

   2024:
      Total business days: 252
      Trained: 187
      Missing: 65
      Completion: 74.2%
      First 10 missing: 2024-11-01, 2024-11-02, ...
```

---

## 🎓 What `--stocks 500` Means

The `--stocks` parameter controls the **training universe**:

- **200** (default): Trains on top 200 most liquid stocks (faster, good quality)
- **500** (recommended): Trains on top 500 most liquid stocks (best quality)
- **1000+**: All available stocks (very comprehensive, but slower)

**Note**: Predictions are made on **ALL stocks**, regardless of training size!

### Example Performance:

| Stocks | Training Time (First) | Training Time (Cached) | Quality |
|--------|----------------------|------------------------|---------|
| 200    | ~8 minutes           | ~30 seconds            | Good    |
| 500    | ~12 minutes          | ~45 seconds            | Better  |
| 1000   | ~20 minutes          | ~90 seconds            | Best    |

---

## 📦 Caching System

### What Gets Cached?

1. **BSE Data** (per date)
   - Location: `./stock_picker_data/cache/bse_data/`
   - Format: `bhav_bse_YYYYMMDD.pkl`
   - **Downloaded once, never again!**

2. **Features** (per date range + stock universe)
   - Location: `./stock_picker_data/cache/features/`
   - Format: `features_STARTDATE_ENDDATE_NSTOCKS_NROWS.pkl`
   - Computed once, reused forever

3. **Models** (versioned)
   - Location: `./stock_picker_data/models/`
   - Format: `model_5session_YYYY-MM-DD.pkl` (dated) + `model_5session.pkl` (latest)

### Manage Cache

```bash
# View cache status
python cache_manager.py
# Then select option 1

# Clear specific cache
python cache_manager.py
# Then select option 3, 4, or 5
```

---

## 🔄 Training Progress Tracking

### How It Works

The system tracks:
- ✅ Which dates have been trained
- 📊 Model version and signature
- 📈 Performance metrics per date
- 🕒 Training history

### Resume After Interruption

Training can be interrupted (Ctrl+C) and resumed:

```bash
# Start training
python run_yearly_training.py --year 2024 --stocks 500

# ... trains 100 dates ...
# (Press Ctrl+C to stop)

# Resume later (continues from date 101!)
python run_yearly_training.py --year 2024 --stocks 500
```

### Check If Year is Complete

```bash
python run_yearly_training.py --status
```

If all dates trained, you'll see:
```
   2024:
      Total business days: 252
      Trained: 252
      Missing: 0
      Completion: 100.0% ✅
```

The system will prompt:
```
✅ All dates in 2024 already trained!
```

---

## 🔧 Model Updates & Retraining

### When Model is Updated

If you modify the model (change features, parameters, etc.), the system **automatically detects** the change:

```
⚠️  Model has been updated since last training!
   All dates for this year will be retrained.
```

### Force Retrain

```bash
# Force retrain all dates (ignores completion status)
python run_yearly_training.py --year 2024 --stocks 500 --force
```

Use this when:
- Model structure changed
- Want to retrain with different stock universe
- Want to improve existing model

---

## 📈 Model Learning Strategy

### Incremental Training

For each date:
1. **Data Window**: Uses 2 years of historical data before that date
2. **Training**: Trains model on data **before** the date (no lookahead!)
3. **Validation**: Uses time-series cross-validation
4. **Save**: Saves model with metadata

Example for 2024-06-15:
```
Training data: 2022-06-15 to 2024-06-14
Validation: Time-series CV (3 folds)
Model saved: model_5session_2024-06-15.pkl
```

### Why This Matters

- **Realistic**: Model only sees data it would have had on that date
- **No Lookahead Bias**: Can't cheat by seeing future data
- **Continuous Learning**: Model improves as it sees more dates
- **Backtestable**: Can test model performance on historical dates

---

## 🎯 Typical Workflow

### Initial Setup (One-Time)

```bash
# 1. Train model on recent year
python run_yearly_training.py --year 2024 --stocks 500

# This will:
# - Download all 2024 data (cached!)
# - Train on each business day
# - Save model versions
# - Takes ~4-6 hours for full year (mostly first-time downloads)
```

### Daily Usage (Fast!)

```bash
# Every day, run this for stock picks
python run_5session_picker.py --stocks 500

# Uses existing model → takes ~30 seconds!
# Only downloads today's new data
```

### Weekly/Monthly Updates

```bash
# Update model with recent dates
python run_yearly_training.py --year 2024 --stocks 500

# Only trains new untrained dates
# Very fast since data is cached!
```

---

## 📋 Command Reference

### Daily Stock Picker

```bash
# Basic (uses existing model)
python run_5session_picker.py

# With more stocks
python run_5session_picker.py --stocks 500

# Force retrain
python run_5session_picker.py --stocks 500 --retrain
```

### Yearly Training

```bash
# Train specific year
python run_yearly_training.py --year 2024 --stocks 500

# Train year range
python run_yearly_training.py --year-start 2023 --year-end 2024 --stocks 500

# Check status
python run_yearly_training.py --status

# Force retrain all
python run_yearly_training.py --year 2024 --stocks 500 --force
```

### Cache Management

```bash
# Interactive cache manager
python cache_manager.py
```

### Training Status

```bash
# Python API
from model_trainer import ModelTracker
tracker = ModelTracker()
tracker.display_status([2023, 2024])
```

---

## ❓ FAQ

### Q: Why does first run take so long?

**A:** First run downloads data and computes features. This is cached, so subsequent runs are **instant**!

### Q: Do I need to retrain every day?

**A:** No! Use the existing model for daily picks:
```bash
python run_5session_picker.py --stocks 500
```

Only retrain when you want to update the model with recent market patterns.

### Q: What if I stop training midway?

**A:** No problem! The system tracks progress. Just run the same command again and it will continue from where it left off.

### Q: How do I know if a year is complete?

**A:** Run `python run_yearly_training.py --status` and check the completion percentage.

### Q: Can I train multiple years?

**A:** Yes!
```bash
python run_yearly_training.py --year-start 2023 --year-end 2024 --stocks 500
```

### Q: What if model gets updated?

**A:** The system automatically detects model changes and prompts you to retrain. You can also force retrain with `--force`.

### Q: How much disk space needed?

**A:** Approximately:
- BSE data: ~500 MB per year
- Features: ~1 GB per year
- Models: ~50 MB per year
- **Total: ~1.5 GB per year**

---

## 🎉 Summary

### Benefits of This System

1. **⚡ Speed**: First run is slow, all subsequent runs are instant!
2. **📦 Efficiency**: Data downloaded once, cached forever
3. **🎓 Learning**: Model learns from every date in history
4. **🔄 Resumable**: Can stop and continue anytime
5. **📊 Tracking**: Always know what's trained and what's not
6. **🔧 Smart**: Detects model updates and handles retraining

### Daily Workflow

```bash
# Morning: Get today's stock picks (30 seconds!)
python run_5session_picker.py --stocks 500

# Weekend: Update model with recent dates (optional)
python run_yearly_training.py --year 2024 --stocks 500
```

---

## 🚀 Next Steps

1. **First Time**: Train on recent year
   ```bash
   python run_yearly_training.py --year 2024 --stocks 500
   ```

2. **Daily**: Get stock picks
   ```bash
   python run_5session_picker.py --stocks 500
   ```

3. **Check Progress**:
   ```bash
   python run_yearly_training.py --status
   ```

4. **Update Model** (monthly):
   ```bash
   python run_yearly_training.py --year 2024 --stocks 500
   ```

---

**Happy Trading! 📈**
