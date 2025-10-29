# 5-Session Stock Picker Notebook - Error Analysis

## Executive Summary

I've analyzed the entire notebook systematically. Below are all identified errors, categorized by severity, along with fixes.

---

## 🔴 CRITICAL ERRORS (Will cause notebook to fail)

### 1. **Cell 19: Missing Feature Columns in Prediction Pipeline**

**Location**: `generate_daily_picks()` function, line ~35

**Error**:
```python
# Extract feature columns (same as training)
exclude_cols = ['date', 'symbol', 'open', 'high', 'low', 'close', 'volume']
feature_cols = [col for col in latest.columns if col not in exclude_cols]
```

**Problem**:
- The feature columns are determined dynamically from whatever columns exist after feature engineering
- During training, features are created by `prepare_ml_dataset()` which includes target generation
- During prediction, features are created by `compute_all_features()` which ALSO includes target generation
- The feature columns, their order, and presence might not match between training and prediction
- The model expects specific features in a specific order

**Impact**: Model prediction will fail with dimension mismatch or incorrect predictions

**Fix**: The predictor needs to store and use the exact feature columns from training

### 2. **Cell 13: log() function called before definition**

**Location**: Cell 13, lines after import attempts

**Error**:
```python
try:
    from indian_trading_system.indicators.technical import TechnicalIndicators
    # ...
    log("✅ Successfully imported indian_trading_system modules!")  # ❌ log() not yet defined
    MODULES_AVAILABLE = True
except ImportError as e:
    log(f"⚠️ Could not import modules: {e}", 'WARNING')  # ❌ log() not yet defined
```

**Problem**: `log()` function is defined in Cell 6, but Cell 13 uses it. However, in Colab, if cells are run out of order or if there's an issue with the execution order, this will fail.

**Impact**: NameError when imports fail or succeed

**Fix**: Either use print() instead or ensure log() is available globally

---

## 🟡 HIGH PRIORITY ISSUES (Will likely cause failures)

### 3. **Cell 8: NSE API Will Fail**

**Location**: `fetch_nse_stock_universe()` function

**Error**:
```python
url = f"https://www.nseindia.com/api/equity-stockIndices?index={index.replace(' ', '%20')}"
headers = {
    'User-Agent': 'Mozilla/5.0',
    'Accept': 'application/json'
}
response = requests.get(url, headers=headers, timeout=10)
```

**Problem**:
- NSE India API requires session management, cookies, and specific headers
- Simple GET request will return 401/403
- Only fetches 50 fallback symbols instead of 3000+

**Impact**: Will only get ~50 stocks instead of 3000+, severely limiting the system

**Fix**: Need proper NSE API scraping with session management OR use alternative data source

### 4. **Cell 11: F&O Ban List URL May Fail**

**Location**: `fetch_fno_ban_list()` function

**Error**:
```python
url = "https://nsearchives.nseindia.com/content/fo/fo_secban.csv"
```

**Problem**:
- URL might have changed
- No retry logic
- Silently returns empty list on failure

**Impact**: F&O banned stocks won't be filtered out

**Fix**: Add retry logic, verify current URL, add proper error handling

### 5. **Cell 14: Module Method Call Signature Mismatch Risk**

**Location**: `compute_all_features()` function

**Potential Issue**:
```python
df = technical_indicators.calculate_all(df)
df = volatility_estimators.calculate_all(df)
```

**Problem**:
- These methods return the DataFrame with added columns
- But some might expect different column names (e.g., 'Close' vs 'close')
- yfinance returns 'Date', 'Open', 'High', 'Low', 'Close', 'Volume'
- Cell 9 converts to lowercase
- Need to ensure consistency

**Impact**: Could cause KeyError if column names don't match

**Status**: Checked modules - they use lowercase column names ✅

---

## 🟠 MEDIUM PRIORITY ISSUES (May cause issues in specific scenarios)

### 6. **Cell 17: LightGBM Model Doesn't Store Feature Names**

**Location**: `LightGBMStockPredictor` class

**Issue**:
```python
def train(self, X: pd.DataFrame, y: pd.Series, feature_names: List[str]):
    train_data = lgb.Dataset(X, label=y, feature_name=feature_names)
    self.model = lgb.train(...)
```

**Problem**:
- Feature names are passed but not stored in the class
- When loading model later, feature names are lost
- Prediction pipeline doesn't know which features to use

**Impact**: Cannot reproduce predictions reliably

**Fix**: Store feature_names as instance variable

### 7. **Cell 21: run_complete_workflow() - Model Loading Without Features**

**Location**: `run_complete_workflow()` function

**Issue**:
```python
if os.path.exists(model_path):
    predictor.load(model_path)
    log(f"✅ Model loaded from {model_path}")
```

**Problem**:
- Loads model but doesn't load the feature columns used during training
- Can't make predictions without knowing which features to use

**Impact**: Predictions will fail after loading saved model

**Fix**: Save and load feature columns alongside model

### 8. **Cell 14: compute_features_pandas_ta() Defined After Being Referenced**

**Location**: `compute_all_features()` function

**Issue**: Function calls `compute_features_pandas_ta()` but it's defined later in the same cell

**Status**: ✅ Actually fine - Python allows this within the same cell

---

## 🟢 LOW PRIORITY ISSUES (Cosmetic or minor)

### 9. **Cell 4: Duplicate TALIB_AVAILABLE Definition**

**Location**: Cells 2 and 4

**Issue**: `TALIB_AVAILABLE` is defined in both Cell 2 and Cell 4

**Impact**: Minor - just redundant, not harmful

**Fix**: Remove from one cell

### 10. **Cell 16: Verbose Loop for Dataset Preparation**

**Location**: `prepare_ml_dataset()` function

**Issue**: Uses tqdm loop but doesn't parallelize

**Impact**: Slow for 3000+ stocks (could take hours)

**Fix**: Consider using joblib.Parallel for feature computation

---

## 📋 REQUIRED FIXES

### Fix #1: Update Cell 17 - Store Feature Names

```python
class LightGBMStockPredictor:
    def __init__(self, params: Optional[Dict] = None):
        # ... existing code ...
        self.feature_names = None  # ADD THIS

    def train(self, X: pd.DataFrame, y: pd.Series, feature_names: List[str]):
        # ... existing code ...
        self.feature_names = feature_names  # ADD THIS

    def save(self, path: str):
        if self.model is None:
            raise ValueError("Model not trained yet!")

        self.model.save_model(path)

        # Save feature names
        import json
        feature_path = path.replace('.txt', '_features.json')
        with open(feature_path, 'w') as f:
            json.dump(self.feature_names, f)

        log(f"Model and features saved to {path}")

    def load(self, path: str):
        self.model = lgb.Booster(model_file=path)

        # Load feature names
        import json
        feature_path = path.replace('.txt', '_features.json')
        if os.path.exists(feature_path):
            with open(feature_path, 'r') as f:
                self.feature_names = json.load(f)

        log(f"Model and features loaded from {path}")
```

### Fix #2: Update Cell 19 - Use Stored Feature Names

```python
def generate_daily_picks(
    predictor: LightGBMStockPredictor,
    stock_universe: pd.DataFrame,
    target_picks: int = 15,
    initial_threshold: float = 0.62,
    min_threshold: float = 0.52,
    threshold_step: float = 0.02
) -> pd.DataFrame:
    # ... existing code up to feature computation ...

    for symbol, df in tqdm(stock_data.items(), desc="Computing features"):
        try:
            df_features = compute_all_features(df)
            latest = df_features.iloc[-1:].copy()

            # Use predictor's stored feature names
            if predictor.feature_names is None:
                raise ValueError("Model has no feature names - was it trained properly?")

            # Ensure all required features exist
            missing_features = set(predictor.feature_names) - set(latest.columns)
            if missing_features:
                log(f"Missing features for {symbol}: {missing_features}", 'WARNING')
                # Add missing features with 0
                for feat in missing_features:
                    latest[feat] = 0

            # Extract features in correct order
            X = latest[predictor.feature_names]

            # ... rest of code ...
```

### Fix #3: Update Cell 13 - Fix log() calls

```python
# Step 4: Import our proven modules
try:
    from indian_trading_system.indicators.technical import TechnicalIndicators
    from indian_trading_system.indicators.volatility import VolatilityEstimators
    from indian_trading_system.indicators.patterns import CandlestickPatterns
    from indian_trading_system.models.features import FeatureEngineer
    from indian_trading_system.backtesting.engine import BacktestEngine
    from indian_trading_system.utils.indian_market import IndianMarketUtils

    print("✅ Successfully imported indian_trading_system modules!")  # Changed to print
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Could not import modules: {e}")  # Changed to print
    print("Will use inline implementations")
    MODULES_AVAILABLE = False
```

### Fix #4: Update Cell 16 - Save Feature Columns in prepare_ml_dataset

```python
def prepare_ml_dataset(stock_data_dict: Dict[str, pd.DataFrame]) -> Tuple[pd.DataFrame, List[str]]:
    # ... existing code ...

    # Combine all stocks
    combined_df = pd.concat(all_data, ignore_index=True)

    # Identify feature columns
    exclude_cols = ['date', 'symbol', 'open', 'high', 'low', 'close', 'volume',
                    'forward_return', 'target']
    feature_cols = [col for col in combined_df.columns if col not in exclude_cols]

    # Remove features with too many NaNs (>50%)
    features_to_remove = []
    for col in feature_cols:
        if combined_df[col].isna().sum() / len(combined_df) > 0.5:
            features_to_remove.append(col)

    for col in features_to_remove:
        feature_cols.remove(col)

    # Fill remaining NaNs with median
    for col in feature_cols:
        if combined_df[col].isna().any():
            median_val = combined_df[col].median()
            combined_df[col] = combined_df[col].fillna(median_val)

    # SAVE FEATURE COLUMNS TO CONFIG
    feature_list_path = os.path.join(CONFIG['MODELS_DIR'], 'feature_columns.json')
    import json
    with open(feature_list_path, 'w') as f:
        json.dump(feature_cols, f)
    log(f"Saved {len(feature_cols)} feature columns to {feature_list_path}")

    log(f"Prepared dataset: {len(combined_df)} samples, {len(feature_cols)} features")
    log(f"Positive samples: {combined_df['target'].sum()} ({combined_df['target'].mean()*100:.1f}%)")

    return combined_df, feature_cols
```

---

## ✅ TESTING RECOMMENDATIONS

1. **Test with Small Dataset First**: Run with `n_stocks_for_training=10` to catch errors quickly

2. **Test Each Section Independently**:
   - Test data download (Cell 9)
   - Test feature engineering (Cell 14)
   - Test model training (Cell 17)
   - Test prediction pipeline (Cell 19)

3. **Verify Feature Consistency**:
   ```python
   # After training
   print(f"Training features: {predictor.feature_names[:10]}")

   # After prediction
   print(f"Prediction features: {X.columns[:10]}")
   ```

4. **Check Data Shapes**:
   ```python
   print(f"Training X shape: {X.shape}")
   print(f"Prediction X shape: {X.shape}")
   ```

---

## 🎯 SUMMARY

**Total Issues Found**: 10
- Critical: 2
- High Priority: 3
- Medium Priority: 3
- Low Priority: 2

**Must-Fix Before Running**:
1. Fix feature name storage and retrieval (Critical #1)
2. Fix log() calls in Cell 13 (Critical #2)
3. Consider alternative for NSE API (High #3)

**Recommended Fixes**:
- All Critical and High Priority issues
- Medium Priority #6 and #7 (feature storage)

**Optional Improvements**:
- Parallelize dataset preparation
- Add retry logic for API calls
- Improve error messages
