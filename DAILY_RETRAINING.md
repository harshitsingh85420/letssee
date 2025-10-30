# 📅 Daily Retraining System - How It Works

## 🧠 Understanding the Learning Process

### How the Model Learns

The 5-session stock picker uses **machine learning** to learn from historical patterns:

```
┌─────────────────────────────────────────────────────────────┐
│  HISTORICAL DATA (Past 2 Years)                             │
│                                                               │
│  For each day in history:                                    │
│  • Calculate 50+ technical indicators                        │
│  • Check: Did stock gain 1.5%+ in next 5 sessions? (Yes/No) │
│  • Store: [Indicators → Outcome]                            │
│                                                               │
│  Model learns: "When indicators look like X, Y, Z...        │
│                 stock usually gains 1.5%+ in 5 sessions"     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  TODAY'S PREDICTION                                          │
│                                                               │
│  For each stock today:                                       │
│  • Calculate same 50+ technical indicators                   │
│  • Model says: "These indicators match past winners!"        │
│  • Probability: 0.65 = 65% confidence based on history      │
│                                                               │
│  Result: List of stocks likely to gain in next 5 sessions   │
└─────────────────────────────────────────────────────────────┘
```

### Why Daily Retraining Matters

**Without Daily Retraining:**
- Model trained on Jan 1st data
- Market conditions change by Feb 1st
- Model still uses old patterns
- ❌ Predictions become less accurate over time

**With Daily Retraining:**
- Model retrains every day with latest data
- Learns most recent market patterns
- Adapts to changing conditions
- ✅ Predictions stay accurate and relevant

---

## 🔄 Daily Workflow

### Option 1: Full Daily Retraining (Recommended)

**Command:**
```bash
python run_stock_picker.py --mode both --stocks 100
```

or use the shorter alias:

```bash
python run_stock_picker.py --mode daily --stocks 100
```

**What Happens:**
1. 📥 Downloads latest data (up to TODAY)
2. 🎓 Trains fresh model on historical patterns
3. 🔮 Generates predictions for today
4. 💾 Saves results to CSV

**Time:** 5-10 minutes (first run), 2-3 minutes (with cache)

**Output:**
```
======================================================================
🎯 5-SESSION STOCK PICKER - DAILY RETRAINING SYSTEM
======================================================================

📅 Today's Date: 2025-10-30 09:00:00
🔧 Mode: both
📁 Data directory: ./stock_picker_data

======================================================================
🧠 DAILY RETRAINING MODE - How It Works:
======================================================================
1. 📊 Trains on historical data up to TODAY
2. 🎓 Learns: Which patterns preceded 5-session gains in the PAST
3. 🔮 Predicts: Which stocks TODAY show similar winning patterns
4. 🔄 Next run: Model updates with one more day of data

💡 This ensures your model adapts to current market conditions!

======================================================================
🎓 TRAINING NEW MODEL
======================================================================
[Training process...]

======================================================================
🔮 GENERATING DAILY PREDICTIONS - SCANNING ALL STOCKS
======================================================================
[Prediction process...]

🏆 ALL 23 QUALIFYING STOCK PICKS FOR 2025-10-30
```

---

### Option 2: Weekly Retraining (Faster Daily)

**For Daily Use:**
```bash
python run_stock_picker.py --mode predict
```

**For Weekly Update:**
```bash
python run_stock_picker.py --mode train --stocks 200
```

**Workflow:**
- Monday: Retrain model with latest week's data
- Tue-Sun: Use saved model for quick predictions

**Pros:** Faster daily runs (30 seconds)
**Cons:** Model may lag behind market by up to 7 days

---

## 📊 How the Model Improves Over Time

### Example: Learning Process

**Day 1 (Jan 1st):**
```
Training data: Jan 2023 - Jan 1, 2025
Model learns: "When RSI > 60 and MACD positive → 70% gain rate"
Predicts: 15 stocks
```

**Day 2 (Jan 2nd):**
```
Training data: Jan 2023 - Jan 2, 2025 (one more day!)
Model learns: "Yesterday's picks performed well, pattern confirmed"
           OR "Yesterday's picks failed, adjust weights"
Predicts: Updated list based on latest learning
```

**Day 30 (Jan 30th):**
```
Training data: Jan 2023 - Jan 30, 2025 (30 more days!)
Model learns: "Recent market favors momentum stocks over value"
Predicts: Adapts strategy to current market regime
```

### Self-Correcting Behavior

The model automatically adjusts because:

1. **Failed Predictions Get Learned:**
   - If Jan 1st picks didn't gain → Model learns "those patterns didn't work"
   - Next retraining: Model reduces weight on those patterns

2. **Successful Predictions Get Reinforced:**
   - If Jan 1st picks DID gain → Model learns "those patterns worked!"
   - Next retraining: Model increases weight on those patterns

3. **Recent Data Has More Impact:**
   - Last 3 months of data influences model more than 2-year-old data
   - Model adapts to current market conditions faster

---

## 🎯 Recommended Setup

### Daily Automation (Best Practice)

**Create a batch file:** `daily_stock_picker.bat`

```batch
@echo off
echo ========================================
echo Daily Stock Picker - Auto Retraining
echo ========================================
echo.

cd /d "path\to\letssee"

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run daily retraining + prediction
python run_stock_picker.py --mode daily --stocks 100

echo.
echo ========================================
echo Done! Check stock_picker_data/results/
echo ========================================
pause
```

**Schedule it:**
- Windows Task Scheduler: Run every day at 9:00 AM
- Linux cron: `0 9 * * * cd /path/to/letssee && ./run_daily.sh`

---

## 💡 Understanding the Results

### What the Probability Means

```
Rank  Symbol         Probability
1     RELIANCE.NS    0.7234
2     TCS.NS         0.6512
3     INFY.NS        0.6201
```

**Probability = Historical Success Rate**

- **0.7234 (72.34%)** = In the past, when RELIANCE had these indicators, it gained 1.5%+ in next 5 sessions **72 times out of 100**
- **0.6512 (65.12%)** = TCS gained in 65 out of 100 similar historical situations
- **0.6201 (62.01%)** = INFY gained in 62 out of 100 similar situations

### Model Learning Example

**Scenario:** Model predicted RELIANCE.NS on Jan 1st with 0.72 probability

**After 5 sessions (Jan 8th):**

If RELIANCE **gained 1.5%+:**
- ✅ Prediction was correct
- Next retraining: Model sees "this pattern worked"
- Similar patterns get higher confidence next time

If RELIANCE **did NOT gain 1.5%:**
- ❌ Prediction was wrong
- Next retraining: Model sees "this pattern failed this time"
- Pattern weight gets slightly reduced

**Over many days:**
- Patterns that consistently work → Higher probability scores
- Patterns that keep failing → Lower probability scores
- Model naturally evolves to current market conditions

---

## 🔧 Advanced: Tracking Model Performance

### Monitor Your Results

After each prediction day, track:

```csv
Date,       Total_Picks, Correct_5Day, Success_Rate
2025-01-01, 23,          17,           73.9%
2025-01-02, 18,          14,           77.8%
2025-01-03, 31,          22,           71.0%
```

### Signs Model Needs Retraining

- Success rate drops below 60% for 5+ consecutive days
- Market regime change (bull → bear or vice versa)
- Major economic event (policy change, global crisis)

→ Run `--mode daily` for a week to let model adapt

---

## ❓ FAQ

**Q: Should I retrain every single day?**
A: Recommended for best results, but weekly is acceptable. Daily retraining with `--mode daily` takes 5-10 min.

**Q: How does the model learn from failures?**
A: When retraining, the model sees historical outcomes. If a pattern consistently led to gains, it gets reinforced. If it failed, it gets de-emphasized.

**Q: What if I skip retraining for a month?**
A: Model will lag behind market conditions. Predictions will be based on 1-month-old patterns. Not recommended.

**Q: Does it learn from my specific picks?**
A: No - it learns from ALL stocks' historical patterns. Your picks are just the output.

**Q: Can I see what the model learned?**
A: Yes! Feature importance is stored in the model. Top features show which indicators matter most.

**Q: Why 5 sessions specifically?**
A: Configurable! Edit `HOLDING_PERIOD = 5` in config. Can be 3, 5, 10, or any number of sessions.

---

## 🎯 Summary

### Key Points

1. ✅ **Model trains on historical data** (what worked in the past)
2. ✅ **Predicts based on today's indicators** (which stocks look similar)
3. ✅ **Retraining updates the model** (learns latest patterns)
4. ✅ **Self-correcting over time** (bad patterns fade, good ones strengthen)

### Daily Workflow

```bash
# Morning: Run daily retraining
python run_stock_picker.py --mode daily --stocks 100

# Check results
cat stock_picker_data/results/picks_2025-10-30_09-00-00.csv

# After 5 sessions: Track which picks succeeded
# Model will learn from these outcomes in next retraining!
```

---

🚀 **You now have a self-improving stock picker that adapts to market conditions daily!**
