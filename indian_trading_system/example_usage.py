"""
Simple example demonstrating how to use the trading system components.
"""

import pandas as pd
import numpy as np
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def example_1_data_loading():
    """Example 1: Load and clean data."""
    print("\n" + "="*80)
    print("EXAMPLE 1: DATA LOADING")
    print("="*80)

    from data.loader import DataLoader
    from data.cleaner import DataCleaner

    # Load data
    loader = DataLoader()
    symbol = 'RELIANCE.NS'
    print(f"\nLoading data for {symbol}...")

    df = loader.load_stock_data(symbol)

    if df is not None:
        print(f"\nLoaded {len(df)} days of data")
        print(f"Date range: {df['date'].min()} to {df['date'].max()}")
        print(f"\nFirst few rows:")
        print(df.head())

        # Clean data
        cleaner = DataCleaner()
        df_clean = cleaner.clean_stock_data(df)

        print(f"\nAfter cleaning: {len(df_clean)} rows")

        # Data quality report
        report = cleaner.get_data_quality_report(df_clean)
        print(f"\nData Quality Report:")
        print(f"  Total rows: {report['total_rows']}")
        print(f"  Mean close: ₹{report['price_stats']['mean_close']:.2f}")
        print(f"  Mean volume: {report['volume_stats']['mean_volume']:,.0f}")


def example_2_technical_indicators():
    """Example 2: Calculate technical indicators."""
    print("\n" + "="*80)
    print("EXAMPLE 2: TECHNICAL INDICATORS")
    print("="*80)

    from data.loader import DataLoader
    from indicators.technical import TechnicalIndicators
    from indicators.volatility import VolatilityEstimators

    # Load data
    loader = DataLoader()
    df = loader.load_stock_data('TCS.NS')

    if df is not None:
        # Calculate indicators
        technical = TechnicalIndicators()
        volatility = VolatilityEstimators()

        df = technical.calculate_all(df)
        df = volatility.calculate_all(df)

        print("\nTechnical Indicators (last 5 days):")
        cols = ['date', 'close', 'supertrend_direction', 'adx', 'kst', 'cmf', 'yang_zhang_vol']
        print(df[cols].tail())


def example_3_candlestick_patterns():
    """Example 3: Detect candlestick patterns."""
    print("\n" + "="*80)
    print("EXAMPLE 3: CANDLESTICK PATTERNS")
    print("="*80)

    from data.loader import DataLoader
    from indicators.patterns import CandlestickPatterns

    # Load data
    loader = DataLoader()
    df = loader.load_stock_data('INFY.NS')

    if df is not None:
        # Detect patterns
        patterns = CandlestickPatterns()
        df = patterns.detect_all_patterns(df)
        df = patterns.calculate_pattern_strength(df)

        # Get summary
        summary = patterns.get_pattern_summary(df)
        print("\nPattern Detection Summary:")
        print(summary)

        # Show recent patterns
        pattern_cols = [col for col in df.columns if col.startswith('pattern_')]
        recent = df[df[pattern_cols].sum(axis=1) > 0].tail(5)

        if not recent.empty:
            print("\nRecent patterns detected:")
            print(recent[['date', 'close'] + pattern_cols[:5]])


def example_4_ml_training():
    """Example 4: Train ML models."""
    print("\n" + "="*80)
    print("EXAMPLE 4: ML MODEL TRAINING")
    print("="*80)

    from data.loader import DataLoader
    from models.features import FeatureEngineer
    from models.ml_models import MLModels

    # Load data
    loader = DataLoader()
    df = loader.load_stock_data('HDFCBANK.NS')

    if df is not None:
        # Create features
        engineer = FeatureEngineer()
        df_with_features = engineer.create_all_features(df)
        X, y, feature_names = engineer.prepare_ml_data(df_with_features)

        print(f"\nData shape: X={X.shape}, y={y.shape}")
        print(f"Positive samples: {y.sum()} ({y.mean():.1%})")

        if len(X) > 100:
            # Train models (simplified - just one CV fold for speed)
            ml_models = MLModels()

            print("\nTraining Random Forest...")
            model = ml_models.train_random_forest(X, y)

            print("\nTraining XGBoost...")
            model = ml_models.train_xgboost(X, y)

            # Train final models
            ml_models.train_final_models(X, y, feature_names)

            # Feature importance
            print("\nTop 10 Important Features:")
            importance = ml_models.get_feature_importance(top_n=10)
            print(importance)


def example_5_signal_generation():
    """Example 5: Generate trading signals."""
    print("\n" + "="*80)
    print("EXAMPLE 5: SIGNAL GENERATION")
    print("="*80)

    from data.loader import DataLoader
    from portfolio.signals import SignalGenerator

    # Load data
    loader = DataLoader()
    df = loader.load_stock_data('ICICIBANK.NS')

    if df is not None:
        # Generate signals
        signal_gen = SignalGenerator()
        df_with_signals = signal_gen.generate_all_signals(df)

        # Show recent signals
        print("\nRecent signals (last 10 days):")
        summary = signal_gen.get_signal_summary(df_with_signals, recent_days=10)
        print(summary)

        # Show buy signals
        buy_signals = df_with_signals[df_with_signals['trading_signal'] == 1].tail(5)
        if not buy_signals.empty:
            print("\nRecent BUY signals:")
            print(buy_signals[['date', 'close', 'composite_signal']])


def example_6_backtesting():
    """Example 6: Run backtest."""
    print("\n" + "="*80)
    print("EXAMPLE 6: BACKTESTING")
    print("="*80)

    from data.loader import DataLoader
    from portfolio.signals import SignalGenerator
    from backtesting.engine import BacktestEngine

    # Load data
    loader = DataLoader()
    df = loader.load_stock_data('RELIANCE.NS')

    if df is not None:
        # Generate signals
        signal_gen = SignalGenerator()
        df_with_signals = signal_gen.generate_all_signals(df)

        # Run backtest
        engine = BacktestEngine(initial_capital=1000000)
        results = engine.run_backtest(
            df_with_signals,
            df_with_signals['trading_signal'],
            position_size=0.3
        )

        # Print results
        engine.print_results(results)


def example_7_portfolio_management():
    """Example 7: Portfolio management."""
    print("\n" + "="*80)
    print("EXAMPLE 7: PORTFOLIO MANAGEMENT")
    print("="*80)

    from portfolio.manager import PortfolioManager

    # Create portfolio
    portfolio = PortfolioManager(capital=1000000, max_positions=10)

    # Add positions
    print("\nAdding positions...")
    portfolio.add_position('RELIANCE.NS', 100, 2500, stop_loss=2400, sector='Energy')
    portfolio.add_position('TCS.NS', 50, 3500, stop_loss=3400, sector='IT')
    portfolio.add_position('HDFCBANK.NS', 75, 1600, stop_loss=1550, sector='Banking')

    # Update prices
    print("\nUpdating prices...")
    portfolio.update_position('RELIANCE.NS', 2550)
    portfolio.update_position('TCS.NS', 3450)
    portfolio.update_position('HDFCBANK.NS', 1620)

    # Show portfolio
    portfolio.print_portfolio()


def example_8_transaction_costs():
    """Example 8: Calculate Indian market transaction costs."""
    print("\n" + "="*80)
    print("EXAMPLE 8: TRANSACTION COSTS")
    print("="*80)

    from utils.indian_market import IndianMarketUtils

    market_utils = IndianMarketUtils()

    # Calculate costs for different trade sizes
    trade_values = [50000, 100000, 500000, 1000000]

    print("\nTransaction Costs:")
    print("-" * 80)

    for trade_value in trade_values:
        costs = market_utils.calculate_transaction_costs(trade_value)

        print(f"\nTrade Value: ₹{trade_value:,}")
        print(f"  Brokerage: ₹{costs['brokerage']:.2f}")
        print(f"  STT: ₹{costs['stt']:.2f}")
        print(f"  Exchange Charges: ₹{costs['exchange_charges']:.2f}")
        print(f"  GST: ₹{costs['gst']:.2f}")
        print(f"  Stamp Duty: ₹{costs['stamp_duty']:.2f}")
        print(f"  Total Round-Trip: ₹{costs['total_round_trip']:.2f} ({costs['total_round_trip_pct']:.4f}%)")


def run_all_examples():
    """Run all examples."""
    examples = [
        example_1_data_loading,
        example_2_technical_indicators,
        example_3_candlestick_patterns,
        # example_4_ml_training,  # Uncomment if you want to run ML training (takes time)
        example_5_signal_generation,
        example_6_backtesting,
        example_7_portfolio_management,
        example_8_transaction_costs,
    ]

    for i, example_func in enumerate(examples, 1):
        try:
            example_func()
        except Exception as e:
            logger.error(f"Error in example {i}: {e}")
            import traceback
            traceback.print_exc()

        print("\n")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("INDIAN EQUITY TRADING SYSTEM - EXAMPLES")
    print("="*80)

    run_all_examples()

    print("\n" + "="*80)
    print("ALL EXAMPLES COMPLETE")
    print("="*80)
