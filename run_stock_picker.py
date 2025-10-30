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
    universe = build_stock_universe(max_stocks=n_stocks)  # Limit for training
    log(f"Training on up to {len(universe)} stocks")

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
    """Generate daily predictions - scans ALL stocks"""
    log("="*70)
    log("🔮 GENERATING DAILY PREDICTIONS - SCANNING ALL STOCKS")
    log("="*70)

    # Load model if not provided
    if predictor is None:
        model_path = os.path.join(config.MODELS_DIR, '5session_model.txt')
        if not os.path.exists(model_path):
            log("❌ No trained model found! Run with --mode train first", 'ERROR')
            return None

        log("📂 Loading trained model...")
        predictor = LightGBMPredictor(config)
        predictor.load(model_path)
        log(f"✅ Model loaded with {len(predictor.feature_names)} features")

    # Step 1: Build FULL universe (ALL stocks)
    log("\n" + "-"*70)
    log("STEP 1: Building Stock Universe")
    log("-"*70)
    universe = build_stock_universe(max_stocks=None)  # No limit - scan ALL
    log(f"🎯 Target universe: {len(universe)} stocks")
    log(f"📊 Sources: Nifty 50, Next 50, Midcap 100, Smallcap 250")

    # Step 2: Download latest data
    log("\n" + "-"*70)
    log("STEP 2: Downloading Historical Data")
    log("-"*70)
    loader = DataLoader(config)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=config.LOOKBACK_DAYS)).strftime('%Y-%m-%d')
    log(f"📅 Date range: {start_date} to {end_date} ({config.LOOKBACK_DAYS} days)")

    stock_data = loader.download_multiple(universe, start_date, end_date)
    log(f"✅ Downloaded: {len(stock_data)}/{len(universe)} stocks")
    log(f"❌ Failed/Insufficient data: {len(universe) - len(stock_data)} stocks")

    # Step 3: Apply filters
    log("\n" + "-"*70)
    log("STEP 3: Applying Risk Filters")
    log("-"*70)
    initial_count = len(stock_data)

    stock_data = RiskFilters.apply_all(stock_data, config)

    filtered_count = initial_count - len(stock_data)
    log(f"📊 Filter summary:")
    log(f"   • Started with: {initial_count} stocks")
    log(f"   • Filtered out: {filtered_count} stocks")
    log(f"   • ✅ Passed all filters: {len(stock_data)} stocks")

    if len(stock_data) == 0:
        log("❌ No stocks passed filters!", 'ERROR')
        return None

    # Step 4: Compute features and predict
    log("\n" + "-"*70)
    log("STEP 4: Computing Features & Making Predictions")
    log("-"*70)
    log(f"🔬 Processing {len(stock_data)} stocks with {len(predictor.feature_names)} features each...")

    computer = FeatureComputer()
    predictions = []

    from tqdm import tqdm
    for symbol, df in tqdm(stock_data.items(), desc="Analyzing stocks", unit="stock"):
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
            log(f"⚠️  Error predicting {symbol}: {e}", 'WARNING')
            continue

    if not predictions:
        log("❌ No predictions generated!", 'ERROR')
        return None

    log(f"✅ Generated predictions for {len(predictions)} stocks")

    # Step 5: Apply threshold to get ALL qualifying stocks
    log("\n" + "-"*70)
    log("STEP 5: Filtering by Threshold (Finding ALL Qualifying Stocks)")
    log("-"*70)

    predictions_df = pd.DataFrame(predictions)

    # Show probability distribution
    log(f"📊 Probability distribution:")
    log(f"   • Max probability: {predictions_df['probability'].max():.4f}")
    log(f"   • Mean probability: {predictions_df['probability'].mean():.4f}")
    log(f"   • Min probability: {predictions_df['probability'].min():.4f}")

    log(f"\n🎯 Applying thresholds to find ALL qualifying stocks:")

    # Try different thresholds and show how many pass at each level
    threshold = config.INITIAL_THRESHOLD
    best_picks = pd.DataFrame()

    while threshold >= config.MIN_THRESHOLD:
        picks_at_threshold = predictions_df[predictions_df['probability'] >= threshold].copy()
        log(f"   🔍 Threshold {threshold:.2f}: {len(picks_at_threshold)} stocks qualify")

        # Save picks from the highest threshold that gives us results
        if len(picks_at_threshold) > 0 and best_picks.empty:
            best_picks = picks_at_threshold
            final_threshold = threshold

        threshold -= config.THRESHOLD_STEP

    # If we found qualifying stocks, use them, otherwise use min threshold
    if best_picks.empty:
        final_threshold = config.MIN_THRESHOLD
        best_picks = predictions_df[predictions_df['probability'] >= final_threshold].copy()

    picks = best_picks
    log(f"\n✅ Final threshold: {final_threshold:.2f}")
    log(f"✅ Total qualifying stocks: {len(picks)}")
    log(f"📊 Note: Showing ALL stocks that pass the criteria (from penny stocks to expensive)")

    # Sort by probability (no limit on number of picks)
    picks = picks.sort_values('probability', ascending=False)
    picks['rank'] = range(1, len(picks) + 1)

    # Step 6: Display and save
    log("\n" + "="*80)
    log("🏆 ALL {0} QUALIFYING STOCK PICKS FOR {1}".format(len(picks), datetime.now().strftime('%Y-%m-%d')))
    log("="*80)

    # Summary statistics
    log(f"\n📊 Qualifying Stocks Statistics:")
    log(f"   • Total qualifying stocks: {len(picks)}")
    log(f"   • Average probability: {picks['probability'].mean():.4f}")
    log(f"   • Highest probability: {picks['probability'].iloc[0]:.4f}")
    log(f"   • Lowest probability: {picks['probability'].iloc[-1]:.4f}")
    log(f"   • Price range: ₹{picks['last_close'].min():.2f} to ₹{picks['last_close'].max():.2f}")
    log(f"   • Average price: ₹{picks['last_close'].mean():.2f}")
    log(f"   • Average 5D return: {picks['return_5d'].mean():.2f}%")

    # Detailed table
    log("\n" + "-"*80)
    print(f"\n{'Rank':<6}{'Symbol':<15}{'Probability':<15}{'Price':<12}{'Volume(20D)':<15}{'5D Return%':<12}")
    print("="*80)
    for _, row in picks.iterrows():
        vol_str = f"{row['volume_20d_avg']/1e6:.2f}M" if row['volume_20d_avg'] > 1e6 else f"{row['volume_20d_avg']/1e3:.0f}K"
        print(f"{int(row['rank']):<6}{row['symbol']:<15}{row['probability']:<15.4f}"
              f"₹{row['last_close']:<11.2f}{vol_str:<15}{row['return_5d']:<12.2f}")
    print("="*80)

    # Save to CSV
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"picks_{timestamp}.csv"
    filepath = os.path.join(config.RESULTS_DIR, filename)
    picks.to_csv(filepath, index=False)

    log(f"\n💾 Results saved to: {filepath}")
    log(f"📁 Full results directory: {config.RESULTS_DIR}")

    # Final summary
    log("\n" + "="*80)
    log("✅ PREDICTION COMPLETE!")
    log("="*80)
    log(f"📊 Scanned: {len(universe)} stocks")
    log(f"✅ Generated predictions: {len(predictions)} stocks")
    log(f"🎯 Qualifying stocks (passed all criteria): {len(picks)} stocks")
    log(f"📊 Price range included: Penny stocks to expensive (no limits)")
    log(f"⚠️  Note: This is for educational purposes only. Always do your own research!")
    log("="*80)

    return picks


def main():
    parser = argparse.ArgumentParser(
        description='5-Session Stock Picker - Daily Retraining System\n\n'
                    'HOW IT WORKS:\n'
                    '1. Model trains on historical data up to TODAY\n'
                    '2. Learns which patterns preceded 5-session gains in the PAST\n'
                    '3. Predicts which stocks TODAY show similar patterns\n'
                    '4. Retrains daily/weekly with latest data for continuous learning\n',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--mode', choices=['train', 'predict', 'both', 'daily'], default='predict',
                       help='Mode: train=train only, predict=use saved model, both/daily=retrain+predict (recommended for daily use)')
    parser.add_argument('--stocks', type=int, default=100,
                       help='Number of stocks for training (default: 100, use 500+ for best model)')
    parser.add_argument('--data-dir', type=str, default='./stock_picker_data',
                       help='Directory for data and models')
    parser.add_argument('--scan-limit', type=int, default=None,
                       help='Limit number of stocks to scan during prediction (default: ALL stocks)')
    args = parser.parse_args()

    # 'daily' is an alias for 'both'
    if args.mode == 'daily':
        args.mode = 'both'

    print("="*70)
    print("🎯 5-SESSION STOCK PICKER - DAILY RETRAINING SYSTEM")
    print("="*70)
    print(f"\n📅 Today's Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔧 Mode: {args.mode}")
    print(f"📁 Data directory: {args.data_dir}")

    if args.mode == 'both':
        print("\n" + "="*70)
        print("🧠 DAILY RETRAINING MODE - How It Works:")
        print("="*70)
        print("1. 📊 Trains on historical data up to TODAY")
        print("2. 🎓 Learns: Which patterns preceded 5-session gains in the PAST")
        print("3. 🔮 Predicts: Which stocks TODAY show similar winning patterns")
        print("4. 🔄 Next run: Model updates with one more day of data")
        print("\n💡 This ensures your model adapts to current market conditions!")

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
