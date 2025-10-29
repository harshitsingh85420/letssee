#!/usr/bin/env python3
"""
5-Session Stock Picker - Standalone Runner
Run this script daily to generate stock picks

Usage:
    python run_stock_picker.py --mode train --stocks 50     # Train new model
    python run_stock_picker.py --mode predict               # Generate daily picks
    python run_stock_picker.py --mode both --stocks 100     # Train and predict
"""

import os
import sys
import argparse
import warnings
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

warnings.filterwarnings('ignore')

# Import pipeline modules
from stock_picker_pipeline import (
    StockPickerConfig,
    DataLoader,
    RiskFilters,
    FeatureComputer,
    LightGBMPredictor,
    build_stock_universe,
    generate_labels,
    log
)


def train_model(config: StockPickerConfig, n_stocks: int = 100):
    """Train a new model"""
    log("="*70)
    log("🎓 TRAINING NEW MODEL")
    log("="*70)

    # Step 1: Build stock universe
    universe = build_stock_universe()[:n_stocks]  # Limit for training
    log(f"Training on {len(universe)} stocks")

    # Step 2: Download data
    loader = DataLoader(config)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=config.LOOKBACK_DAYS)).strftime('%Y-%m-%d')

    stock_data = loader.download_multiple(universe, start_date, end_date)

    # Step 3: Apply risk filters
    stock_data = RiskFilters.apply_all(stock_data, config)

    if len(stock_data) == 0:
        log("❌ No stocks passed filters!", 'ERROR')
        return None

    # Step 4: Compute features and prepare dataset
    log("Computing features and preparing ML dataset...")
    computer = FeatureComputer()

    all_data = []
    for symbol, df in stock_data.items():
        df_copy = df.copy()
        df_copy['symbol'] = symbol

        # Compute features
        df_features = computer.compute_features(df_copy)

        # Generate labels
        df_labeled = generate_labels(df_features, config.HOLDING_PERIOD, config.TARGET_GAIN)

        all_data.append(df_labeled)

    # Combine all stocks
    combined_df = pd.concat(all_data, ignore_index=True)

    # Get feature columns
    exclude_cols = ['date', 'symbol', 'open', 'high', 'low', 'close', 'volume',
                    'forward_return', 'target']
    feature_cols = [col for col in combined_df.columns if col not in exclude_cols]

    # Remove features with too many NaNs
    for col in feature_cols[:]:
        if combined_df[col].isna().sum() / len(combined_df) > 0.5:
            feature_cols.remove(col)

    # Fill remaining NaNs
    for col in feature_cols:
        if combined_df[col].isna().any():
            combined_df[col] = combined_df[col].fillna(combined_df[col].median())

    log(f"Dataset: {len(combined_df)} samples, {len(feature_cols)} features")
    log(f"Positive samples: {combined_df['target'].sum()} ({combined_df['target'].mean()*100:.1f}%)")

    # Step 5: Train model
    X = combined_df[feature_cols]
    y = combined_df['target']

    predictor = LightGBMPredictor(config)
    predictor.train(X, y, feature_cols)

    # Step 6: Save model
    model_path = os.path.join(config.MODELS_DIR, '5session_model.txt')
    predictor.save(model_path)

    log("✅ Model training complete!")
    return predictor


def generate_predictions(config: StockPickerConfig, predictor: LightGBMPredictor = None):
    """Generate daily predictions"""
    log("="*70)
    log("🔮 GENERATING DAILY PREDICTIONS")
    log("="*70)

    # Load model if not provided
    if predictor is None:
        model_path = os.path.join(config.MODELS_DIR, '5session_model.txt')
        if not os.path.exists(model_path):
            log("❌ No trained model found! Run with --mode train first", 'ERROR')
            return None

        predictor = LightGBMPredictor(config)
        predictor.load(model_path)

    # Step 1: Build universe
    universe = build_stock_universe()
    log(f"Analyzing {len(universe)} stocks")

    # Step 2: Download latest data
    loader = DataLoader(config)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=config.LOOKBACK_DAYS)).strftime('%Y-%m-%d')

    stock_data = loader.download_multiple(universe, start_date, end_date)

    # Step 3: Apply filters
    stock_data = RiskFilters.apply_all(stock_data, config)

    if len(stock_data) == 0:
        log("❌ No stocks passed filters!", 'ERROR')
        return None

    # Step 4: Compute features and predict
    log("Computing features and making predictions...")
    computer = FeatureComputer()

    predictions = []
    for symbol, df in stock_data.items():
        try:
            df_features = computer.compute_features(df)
            latest = df_features.iloc[-1:].copy()

            # Predict
            prob = predictor.predict(latest)[0]

            predictions.append({
                'symbol': symbol,
                'probability': prob,
                'last_close': df['close'].iloc[-1],
                'volume_20d_avg': df['volume'].tail(20).mean(),
                'return_5d': df['close'].pct_change(5).iloc[-1] * 100 if len(df) >= 5 else 0
            })
        except Exception as e:
            log(f"Error predicting {symbol}: {e}", 'WARNING')
            continue

    if not predictions:
        log("❌ No predictions generated!", 'ERROR')
        return None

    # Step 5: Auto-threshold to get target picks
    predictions_df = pd.DataFrame(predictions)
    threshold = config.INITIAL_THRESHOLD

    while threshold >= config.MIN_THRESHOLD:
        picks = predictions_df[predictions_df['probability'] >= threshold].copy()
        log(f"Threshold {threshold:.2f}: {len(picks)} picks")

        if len(picks) >= config.TARGET_PICKS:
            break
        threshold -= config.THRESHOLD_STEP

    # Get top picks
    picks = picks.sort_values('probability', ascending=False).head(config.TARGET_PICKS)
    picks['rank'] = range(1, len(picks) + 1)

    # Step 6: Display and save
    log("\n" + "="*80)
    log("🏆 TOP STOCK PICKS")
    log("="*80)
    print(f"\n{'Rank':<6}{'Symbol':<15}{'Probability':<15}{'Price':<12}{'5D Return %':<15}")
    print("="*80)
    for _, row in picks.iterrows():
        print(f"{int(row['rank']):<6}{row['symbol']:<15}{row['probability']:<15.4f}"
              f"₹{row['last_close']:<11.2f}{row['return_5d']:<15.2f}")
    print("="*80)

    # Save to CSV
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"picks_{timestamp}.csv"
    filepath = os.path.join(config.RESULTS_DIR, filename)
    picks.to_csv(filepath, index=False)
    log(f"\n💾 Saved to: {filepath}")

    return picks


def main():
    parser = argparse.ArgumentParser(description='5-Session Stock Picker')
    parser.add_argument('--mode', choices=['train', 'predict', 'both'], default='predict',
                       help='Mode: train new model, predict with existing, or both')
    parser.add_argument('--stocks', type=int, default=100,
                       help='Number of stocks for training (default: 100)')
    parser.add_argument('--data-dir', type=str, default='./stock_picker_data',
                       help='Directory for data and models')
    args = parser.parse_args()

    print("="*70)
    print("🎯 5-SESSION STOCK PICKER - PRODUCTION SYSTEM")
    print("="*70)
    print(f"\nMode: {args.mode}")
    print(f"Data directory: {args.data_dir}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Initialize config
    config = StockPickerConfig(args.data_dir)

    # Check imports
    try:
        from indian_trading_system.indicators.technical import TechnicalIndicators
        print("✅ indian_trading_system modules available\n")
    except ImportError:
        print("⚠️ indian_trading_system modules not available, using fallbacks\n")

    # Run based on mode
    predictor = None

    if args.mode in ['train', 'both']:
        predictor = train_model(config, args.stocks)
        if predictor is None:
            print("\n❌ Training failed!")
            sys.exit(1)

    if args.mode in ['predict', 'both']:
        picks = generate_predictions(config, predictor)
        if picks is None:
            print("\n❌ Prediction failed!")
            sys.exit(1)

    print("\n" + "="*70)
    print("✅ DONE!")
    print("="*70)


if __name__ == '__main__':
    main()
