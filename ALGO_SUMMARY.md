# 🎯 5-Session Stock Picker - Algorithm Summary

## 📋 Table of Contents
1. [Core Intention](#core-intention)
2. [How It Works](#how-it-works)
3. [Learning Process](#learning-process)
4. [What Gets Cached](#what-gets-cached)
5. [Complete Data Flow](#complete-data-flow)
6. [Model Training Process](#model-training-process)
7. [Backtesting & Validation](#backtesting--validation)
8. [Daily Usage Workflow](#daily-usage-workflow)

---

## 🎯 Core Intention

**Simple Goal**: Run today → tells which stocks to buy tomorrow → expects positive close in 5 sessions

**Not**: Predict exact returns or timing
**Yes**: Identify stocks with high probability of positive 5-session outcome

---

## 🔧 How It Works

### Step-by-Step Process

```
TODAY (Monday)
├─ 1. Fetch BSE data (last 2 years)
├─ 2. Compute 50+ technical indicators per stock
├─ 3. Create labels: "Did stock go positive after 5 sessions?" (historical data)
├─ 4. Train ML model: Learn which indicator patterns → positive outcomes
├─ 5. Apply model to Monday's closing prices
├─ 6. Show ALL stocks with >62% probability
└─ 7. Save: picks, model, parameters, metadata

TOMORROW (Tuesday)
├─ Buy the recommended stocks
└─ Hold for 5 trading sessions

5 SESSIONS LATER (Next Monday)
├─ Check: Did they close positive?
└─ System learns from this outcome next time
```

---

## 🧠 Learning Process

### What the Model Learns

The model is trained on **historical patterns**:

```python
# For each day in the past 2 years:
for historical_date in past_dates:
    # Get today's indicators
    indicators = compute_indicators(historical_date)

    # Look forward 5 sessions
    future_close = get_close_5_sessions_later(historical_date)

    # Create label
    label = 1 if (future_close > today_close) else 0

    # Model learns: "These indicator values → positive outcome"
```

### Key Insight

Model learns **associations** like:
- "When ADX = 28 + RS_Composite = 0.85 + VolMult = 3.2 → 72% went positive"
- "When ADX = 18 + RS_Composite = 0.45 + VolMult = 1.1 → 42% went positive"

It finds **complex combinations** humans would miss!

---

## 💾 What Gets Cached

### 3-Layer Caching System

#### Layer 1: BSE Raw Data ✅
```
Location: stock_picker_data/cache/bse_data/
File: bhav_bse_20230101_20250101.pkl
Contains: Raw OHLCV data from BSE
Speed: 3-5 min → 5-10 sec
```

#### Layer 2: Computed Features ✅
```
Location: stock_picker_data/cache/features/
File: features_2023-01-01_2025-01-01_4706_232450.pkl
Contains: All 50+ technical indicators pre-computed
Speed: 10-15 min → Instant
```

#### Layer 3: Trained Model ✅
```
Location: stock_picker_data/models/
File: model_5session.pkl
Contains:
  • LightGBM model object
  • Feature column names
  • Configuration (thresholds, lookback, etc.)
  • Training metadata (CV scores, feature importance)
  • Data statistics (positive ratio, sample count)
Speed: 2-3 min training → Instant load
```

### What Gets Saved on Each Run

```python
{
    'model': <LightGBM object>,
    'feature_cols': ['EMA20', 'RSI14', 'ADX14', ...],

    'config': {
        'LOOKBACK_DAYS': 730,
        'FORWARD_PERIOD': 5,
        'INITIAL_THRESHOLD': 0.62,
        'MIN_THRESHOLD': 0.52,
        ...
    },

    'metadata': {
        'train_date': '2025-11-04',
        'cv_scores': [0.68, 0.69, 0.67, 0.70, 0.68],
        'cv_mean': 0.684,
        'cv_std': 0.011,
        'n_training_samples': 115420,
        'feature_importance': [
            {'feature': 'RS_Composite', 'importance': 2845.2},
            {'feature': 'ADX14', 'importance': 2234.7},
            ...
        ]
    },

    'data_stats': {
        'positive_ratio': 0.504,  # 50.4% went positive
        'negative_ratio': 0.496,
        'total_samples': 115420
    }
}
```

---

## 🔄 Complete Data Flow

### From Raw Data to Picks

```
BSE BhavCopy (5600+ stocks, 2 years)
         ↓
[CACHE CHECK: BSE data cached?]
         ↓
Extract OHLCV per stock per day
         ↓
[CACHE CHECK: Features cached?]
         ↓
Compute 50+ Technical Indicators:
    • Trend: EMA20/50/200, slopes
    • Breakouts: 20d/63d/252d high distance & flags
    • Volume: VolMult, Up/Down volume ratio
    • Momentum: 21d/63d returns, RS Composite (percentile rank)
    • Strength: ADX, RSI, +DI/-DI
    • Volatility: Bollinger width, ATR
    • Weekly: Weekly BB width, weekly trend
         ↓
Create Labels (for training):
    For each day, look forward 5 sessions
    Label = 1 if close went up, 0 if down/flat
         ↓
Split Data (Time-Series):
    Train on: 2023-01-01 to 2025-09-30
    Validate on: 2025-10-01 to 2025-10-31
         ↓
Train LightGBM Model:
    • 5-fold time-series cross-validation
    • Binary classification (positive/negative)
    • Early stopping (prevent overfitting)
    • Feature importance tracking
         ↓
[SAVE: Model + Config + Metadata]
         ↓
Predict on Latest Day (e.g., Nov 4, 2025):
    • Get features for all 4706 stocks
    • Model outputs probability (0-1) for each stock
    • Sort by probability
         ↓
Apply Threshold (adaptive):
    • Start at 0.62
    • If no stocks, lower to 0.60, 0.58, ...
    • Stop at minimum 0.52
    • Show ALL stocks above final threshold
         ↓
Save Results:
    • CSV with all picks
    • Rank, symbol, price, probability, indicators
    • Location: stock_picker_data/results/picks_20251104.csv
```

---

## 🎓 Model Training Process

### Training Algorithm

```python
# 1. Prepare Data
X = features[['EMA20', 'RSI14', 'ADX14', ...]]  # 50+ columns
y = labels['positive_5session']  # 0 or 1

# 2. Time-Series Cross-Validation (5 folds)
for fold in 1 to 5:
    # Split chronologically (no shuffling!)
    train_data = data[start : split]
    val_data = data[split : end]

    # Train
    model = LightGBM(train_data)

    # Validate
    predictions = model.predict(val_data)
    auc_score = calculate_auc(val_data.labels, predictions)

    print(f"Fold {fold}: AUC = {auc_score}")

# 3. Train Final Model on ALL data
final_model = LightGBM(X, y)

# 4. Save Everything
save(final_model, config, metadata)
```

### Why Time-Series CV?

**Regular CV** (wrong):
```
Random shuffle → Train on future, test on past → LOOKAHEAD BIAS!
```

**Time-Series CV** (correct):
```
Always train on past → test on future → NO LOOKAHEAD
Fold 1: Train [2023-01 to 2024-01] → Test [2024-02 to 2024-04]
Fold 2: Train [2023-01 to 2024-04] → Test [2024-05 to 2024-07]
...
```

---

## ✅ Backtesting & Validation

### What Backtesting Does

```python
# For each historical signal date:
for date in [Oct 1, Oct 8, Oct 15, ...]:
    # 1. Use ONLY data up to this date (no future peeking!)
    historical_data = data[data.DATE <= date]

    # 2. Train model
    model = train_on_historical_data(historical_data)

    # 3. Get picks for this date
    picks = model.predict(date)

    # 4. Look forward 5 sessions (in the data we have now)
    actual_outcomes = check_5_sessions_later(picks, date)

    # 5. Record results
    results.append({
        'date': date,
        'picks': picks,
        'outcomes': actual_outcomes
    })

# 6. Calculate overall statistics
win_rate = (positive_picks / total_picks) * 100
avg_return = mean(all_returns)
```

### Backtest Output Example

```
Signal Date: 2024-10-01
Picks: 28 stocks
Outcomes 5 sessions later (2024-10-08):
    ✅ Positive: 19 (67.86%)
    ❌ Negative: 9 (32.14%)
    Avg Return: +2.13%

Signal Date: 2024-10-08
Picks: 25 stocks
Outcomes 5 sessions later (2024-10-15):
    ✅ Positive: 17 (68.00%)
    ❌ Negative: 8 (32.00%)
    Avg Return: +1.87%

...

Overall (10 dates, 247 total picks):
    Win Rate: 64.78%
    Avg Return: +1.95%
    Median Return: +1.56%
```

---

## 📅 Daily Usage Workflow

### Monday Morning Routine

```bash
# 1. Run the system
python run_5session_picker.py

# What happens internally:
# ├─ Check BSE cache (load if exists, ~5 sec)
# ├─ Check feature cache (load if exists, instant)
# ├─ Train model on latest data (or load if trained today)
# ├─ Predict on Monday's closing prices
# ├─ Apply threshold, get ALL qualifying stocks
# └─ Save CSV: stock_picker_data/results/picks_20251104.csv

# 2. Review the picks
# Open picks_20251104.csv
# See: Rank, Symbol, Price, Probability, Technical Indicators

# 3. Tuesday morning: Buy the stocks
# Based on your risk tolerance and capital:
#   - High confidence: Stocks with probability > 0.70
#   - Medium confidence: Stocks with probability 0.62-0.70
#   - Or: Top 10-15 stocks only

# 4. Hold for 5 trading sessions
# Don't sell early! The model is trained for 5-session outcomes

# 5. Next Monday: Check outcomes
# Did they close positive?
# System will learn from this on next training run
```

### Weekly Learning Cycle

```
Week 1:
    Monday: Run system → get picks → Prob[RELIANCE positive] = 0.78
    Tuesday: Buy RELIANCE at ₹2456
    Next Monday: RELIANCE closes at ₹2534 → ✅ Positive!

Week 2:
    Monday: Run system → model trained with Week 1 outcome
    Now model knows: "That pattern with RELIANCE → worked!"
    Gets picks → identifies similar patterns

Week 3:
    Monday: Run system → model trained with Week 1 + Week 2 outcomes
    Now model has more data to learn from
    Adapts: "These patterns → 68% win rate"

... and so on, continuous learning!
```

---

## 🎯 Key Takeaways

### What Makes This System Work

1. **Rich Features**: 50+ momentum/breakout indicators (your original expertise!)
2. **ML Learning**: Finds complex pattern combinations automatically
3. **Time-Series Validation**: No lookahead bias, realistic performance
4. **Daily Adaptation**: Retrains with latest data, stays current
5. **Comprehensive Caching**: Fast subsequent runs (3 min vs 20 min)
6. **Everything Saved**: Model, config, metadata for reproducibility

### What Gets Better Over Time

- **More training data**: Each day adds 4706 stock samples
- **Pattern recognition**: Model sees which combinations actually worked
- **Threshold tuning**: Learn optimal probability cutoffs
- **Feature importance**: Understand which indicators matter most

### Limitations to Remember

- **Not magic**: ~65% win rate is realistic, not 95%
- **Market dependent**: Works best in trending markets
- **Requires patience**: 5-session holding period is firm
- **Capital risk**: Always use proper position sizing
- **Needs validation**: Backtest before real money!

---

## 📊 Performance Expectations

### Realistic Targets

```
Win Rate: 60-70%
Avg Return per Pick: 1.5-2.5%
Median Return: 1.0-2.0%
Best Picks (Top 10%): 5-15% returns
Worst Picks (Bottom 10%): -5% to -10% losses
```

### How to Measure Success

1. **Win Rate > 60%** → System is working
2. **Average return > 1.5%** → Profitable after costs
3. **Consistency across dates** → Not just lucky
4. **High prob → high win rate** → Model is calibrated

---

## 💡 Usage Tips

1. **Always backtest first** (2-3 months historical data)
2. **Focus on high probability picks** (>0.65 for beginners)
3. **Diversify** (don't put all capital in one stock)
4. **Hold for 5 sessions** (don't exit early!)
5. **Track performance** (compare actual vs predicted)
6. **Retrain daily** (system learns from latest data)

---

**Remember**: This is a probability-based system, not a crystal ball. It identifies favorable setups based on historical patterns, but markets are unpredictable. Always use proper risk management!
