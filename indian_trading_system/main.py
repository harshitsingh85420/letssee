"""
Main execution script for Indian Equity Trading System.

This script demonstrates the complete workflow:
1. Data loading and cleaning
2. Technical indicator calculation
3. ML model training and prediction
4. Signal generation
5. Backtesting
6. Portfolio management
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path

# Data modules
from data.loader import DataLoader
from data.cleaner import DataCleaner

# Indicator modules
from indicators.technical import TechnicalIndicators
from indicators.volatility import VolatilityEstimators
from indicators.patterns import CandlestickPatterns

# ML modules
from models.features import FeatureEngineer
from models.ml_models import MLModels

# Portfolio modules
from portfolio.manager import PortfolioManager
from portfolio.signals import SignalGenerator, StockRanker

# Backtesting
from backtesting.engine import BacktestEngine

# Utils
from utils.constants import TOP_10_NIFTY, NIFTY_50_SYMBOLS
from utils.indian_market import IndianMarketUtils

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TradingSystem:
    """
    Complete trading system integrating all components.
    """

    def __init__(self, symbols: list = None, initial_capital: float = 1000000):
        """
        Initialize trading system.

        Args:
            symbols: List of symbols to trade (default: TOP_10_NIFTY)
            initial_capital: Initial capital in INR
        """
        self.symbols = symbols if symbols else TOP_10_NIFTY
        self.initial_capital = initial_capital

        # Initialize components
        self.data_loader = DataLoader()
        self.data_cleaner = DataCleaner()
        self.technical = TechnicalIndicators()
        self.volatility = VolatilityEstimators()
        self.patterns = CandlestickPatterns()
        self.feature_engineer = FeatureEngineer()
        self.ml_models = MLModels()
        self.signal_generator = SignalGenerator()
        self.backtest_engine = BacktestEngine(initial_capital=initial_capital)
        self.portfolio_manager = PortfolioManager(capital=initial_capital)

        # Data storage
        self.data_dict = {}
        self.signals_dict = {}

        logger.info(f"Initialized Trading System with {len(self.symbols)} symbols")

    def load_and_prepare_data(self, force_download: bool = False):
        """
        Load and prepare data for all symbols.

        Args:
            force_download: Force fresh download
        """
        logger.info("Loading data...")

        # Load data
        self.data_dict = self.data_loader.load_multiple_stocks(
            self.symbols,
            force_download=force_download
        )

        # Clean data
        logger.info("Cleaning data...")
        self.data_dict = self.data_cleaner.clean_multiple_stocks(
            self.data_dict,
            validate=True,
            filter_liquidity=False
        )

        logger.info(f"Data loaded for {len(self.data_dict)} stocks")

    def calculate_indicators(self):
        """Calculate technical indicators for all stocks."""
        logger.info("Calculating indicators...")

        for symbol, df in self.data_dict.items():
            logger.info(f"Processing {symbol}")

            # Technical indicators
            df = self.technical.calculate_all(df)

            # Volatility indicators
            df = self.volatility.calculate_all(df)

            # Candlestick patterns
            df = self.patterns.detect_all_patterns(df)
            df = self.patterns.calculate_pattern_strength(df)

            self.data_dict[symbol] = df

        logger.info("Indicator calculation complete")

    def train_ml_models(self, symbol: str = None):
        """
        Train ML models.

        Args:
            symbol: Symbol to train on (default: first symbol)
        """
        if symbol is None:
            symbol = self.symbols[0]

        logger.info(f"Training ML models on {symbol}...")

        df = self.data_dict[symbol]

        # Create features
        df_with_features = self.feature_engineer.create_all_features(df)
        X, y, feature_names = self.feature_engineer.prepare_ml_data(df_with_features)

        if len(X) < 100:
            logger.warning(f"Insufficient data for training: {len(X)} samples")
            return

        # Cross-validate
        logger.info("Running cross-validation...")
        rf_cv_results = self.ml_models.cross_validate(X, y, model_type='rf')
        xgb_cv_results = self.ml_models.cross_validate(X, y, model_type='xgb')

        # Train final models
        logger.info("Training final models...")
        self.ml_models.train_final_models(X, y, feature_names)

        logger.info("ML training complete")

        return {
            'rf_cv': rf_cv_results,
            'xgb_cv': xgb_cv_results
        }

    def generate_signals(self, use_ml: bool = False):
        """
        Generate trading signals for all stocks.

        Args:
            use_ml: Whether to use ML predictions
        """
        logger.info("Generating signals...")

        for symbol, df in self.data_dict.items():
            logger.info(f"Generating signals for {symbol}")

            ml_predictions = None

            if use_ml and self.ml_models.rf_model is not None:
                # Get ML predictions
                df_with_features = self.feature_engineer.create_all_features(df)
                feature_cols = self.feature_engineer.get_feature_columns(df_with_features)

                # Prepare data
                X = df_with_features[feature_cols].values
                ml_predictions = self.ml_models.predict(X, model_type='ensemble')
                ml_predictions = pd.Series(ml_predictions, index=df.index)

            # Generate signals
            df_with_signals = self.signal_generator.generate_all_signals(df, ml_predictions)
            self.signals_dict[symbol] = df_with_signals

        logger.info("Signal generation complete")

    def rank_stocks(self, top_n: int = 10):
        """
        Rank stocks by signal strength.

        Args:
            top_n: Number of top stocks to return

        Returns:
            DataFrame with ranked stocks
        """
        ranker = StockRanker()
        rankings = ranker.rank_by_signal_strength(self.signals_dict, top_n=top_n)

        logger.info(f"\nTop {len(rankings)} stocks by signal strength:")
        print(rankings)

        return rankings

    def backtest_strategy(self, symbol: str = None):
        """
        Backtest trading strategy.

        Args:
            symbol: Symbol to backtest (None for all)

        Returns:
            Backtest results
        """
        if symbol:
            # Single stock backtest
            df = self.signals_dict[symbol]
            signals = df['trading_signal']

            logger.info(f"Backtesting {symbol}...")
            results = self.backtest_engine.run_backtest(df, signals, position_size=0.3)
            self.backtest_engine.print_results(results)

            return results

        else:
            # Multi-stock backtest
            logger.info("Running portfolio backtest...")

            # Extract signals
            signals_for_backtest = {}
            data_for_backtest = {}

            for symbol in self.signals_dict.keys():
                df = self.signals_dict[symbol]
                signals_for_backtest[symbol] = df['trading_signal']
                data_for_backtest[symbol] = df

            results = self.backtest_engine.run_multi_stock_backtest(
                data_for_backtest,
                signals_for_backtest,
                position_size_per_stock=0.1
            )

            self.backtest_engine.print_results(results)

            return results

    def run_complete_workflow(self, train_ml: bool = True, backtest: bool = True):
        """
        Run complete trading system workflow.

        Args:
            train_ml: Whether to train ML models
            backtest: Whether to run backtest

        Returns:
            Dictionary with results
        """
        logger.info("="*80)
        logger.info("STARTING COMPLETE TRADING SYSTEM WORKFLOW")
        logger.info("="*80)

        # 1. Load and prepare data
        self.load_and_prepare_data()

        # 2. Calculate indicators
        self.calculate_indicators()

        # 3. Train ML models (optional)
        ml_results = None
        if train_ml:
            ml_results = self.train_ml_models()

        # 4. Generate signals
        self.generate_signals(use_ml=train_ml)

        # 5. Rank stocks
        rankings = self.rank_stocks(top_n=10)

        # 6. Backtest (optional)
        backtest_results = None
        if backtest:
            backtest_results = self.backtest_strategy()

        logger.info("="*80)
        logger.info("WORKFLOW COMPLETE")
        logger.info("="*80)

        return {
            'data': self.data_dict,
            'signals': self.signals_dict,
            'rankings': rankings,
            'ml_results': ml_results,
            'backtest_results': backtest_results
        }


def main():
    """
    Main function demonstrating system usage.
    """
    print("\n" + "="*80)
    print("INDIAN EQUITY TRADING SYSTEM")
    print("5-Day Trading Horizon with Advanced Technical Analysis and ML")
    print("="*80 + "\n")

    # Create trading system (using top 10 NIFTY stocks for demonstration)
    system = TradingSystem(symbols=TOP_10_NIFTY, initial_capital=1000000)

    # Run complete workflow
    results = system.run_complete_workflow(train_ml=True, backtest=True)

    # Display top stocks
    print("\n" + "="*80)
    print("TOP TRADING OPPORTUNITIES")
    print("="*80)
    print(results['rankings'])

    # Show signal summary for top stock
    if not results['rankings'].empty:
        top_stock = results['rankings'].iloc[0]['symbol']
        df = results['signals'][top_stock]

        print(f"\n" + "="*80)
        print(f"RECENT SIGNALS FOR {top_stock}")
        print("="*80)
        print(system.signal_generator.get_signal_summary(df, recent_days=10))

    print("\n" + "="*80)
    print("SYSTEM READY FOR TRADING")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
