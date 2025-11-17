"""
Continuous Learning Backtest

The model LEARNS as it goes through time:
1. Start with initial trained model
2. For each date:
   - Make predictions with CURRENT model
   - Get actual outcomes
   - ADD outcomes to training data
   - RETRAIN model on expanded dataset
   - Model now KNOWS MORE
3. Next date uses the IMPROVED model

This simulates real-world learning where model gets smarter over time!
"""

import pandas as pd
import numpy as np
from datetime import date, timedelta
from typing import List, Optional, Tuple
from pathlib import Path
import lightgbm as lgb

from bse_loader import BSEDataFetcher
from momentum_features import prepare_features_all, add_forward_returns
from stock_picker_5session import StockPicker5Session


class ContinuousLearningBacktest:
    """
    Backtest where the model learns continuously from each date's outcomes
    """

    def __init__(self, picker: StockPicker5Session):
        self.picker = picker
        self.fetcher = BSEDataFetcher()

    def run_continuous_learning_backtest(
        self,
        signal_dates: List[date],
        n_stocks: Optional[int] = 200,
        lookback_days: int = 730
    ) -> Tuple[pd.DataFrame, dict]:
        """
        Run backtest where model learns from each date's outcomes

        Args:
            signal_dates: Dates to generate picks
            n_stocks: Training stock count
            lookback_days: Initial training lookback

        Returns:
            (results_df, learning_metrics)
        """
        print("\n" + "=" * 80)
        print("🧠 CONTINUOUS LEARNING BACKTEST")
        print("=" * 80)
        print("Model will LEARN from each date's outcomes and get progressively smarter!")
        print(f"Signal dates: {min(signal_dates)} → {max(signal_dates)}")
        print(f"Total dates: {len(signal_dates)}")
        print("=" * 80)

        # Fetch data covering all dates + forward period
        lookback_start = min(signal_dates) - timedelta(days=lookback_days)
        lookback_end = max(signal_dates) + timedelta(days=30)

        print(f"\n📥 Fetching data: {lookback_start} → {lookback_end}")
        bhav = self.fetcher.fetch_bhav_range(lookback_start, lookback_end)

        # Get stock universe
        qualified_stocks = self.fetcher.get_stock_universe(bhav, self.picker.MIN_DATA_POINTS)

        # Limit training stocks
        if n_stocks and n_stocks < len(qualified_stocks):
            liquidity = bhav.groupby('SC_CODE')['ValueTraded'].mean().sort_values(ascending=False)
            top_stocks = liquidity.head(n_stocks).index.tolist()
            bhav_train = bhav[bhav['SC_CODE'].isin(top_stocks)].copy()
        else:
            bhav_train = bhav.copy()

        print(f"📊 Training on {len(qualified_stocks) if not n_stocks else n_stocks} stocks")

        # Compute features once
        print(f"\n🔧 Computing features...")
        features = prepare_features_all(bhav_train)
        features_with_labels = add_forward_returns(features, periods=[self.picker.FORWARD_PERIOD])

        print(f"✅ Features computed: {len(features):,} rows")

        # STEP 1: Initial model training
        print(f"\n" + "=" * 80)
        print("🎓 STEP 1: Train Initial Model")
        print("=" * 80)

        initial_date = min(signal_dates)
        initial_cutoff = pd.Timestamp(initial_date)

        # Train on data BEFORE first signal date
        initial_data = features_with_labels[features_with_labels['DATE'] < initial_cutoff].copy()

        label_col = f"Label_fwd{self.picker.FORWARD_PERIOD}_positive"
        initial_train = initial_data.dropna(subset=[label_col] + self.picker.feature_cols).copy()

        X_initial = initial_train[self.picker.feature_cols]
        y_initial = initial_train[label_col]

        print(f"📊 Initial training samples: {len(X_initial):,}")
        print(f"   Positive ratio: {y_initial.mean():.2%}")

        # Train initial model
        params = {
            'objective': 'binary',
            'metric': 'auc',
            'boosting_type': 'gbdt',
            'num_leaves': 31,
            'learning_rate': 0.05,
            'feature_fraction': 0.8,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'verbose': -1,
            'seed': 42
        }

        train_data = lgb.Dataset(X_initial, label=y_initial)
        current_model = lgb.train(params, train_data, num_boost_round=200, callbacks=[lgb.log_evaluation(0)])

        print("✅ Initial model trained!")

        # STEP 2: Continuous learning through dates
        print(f"\n" + "=" * 80)
        print("🔄 STEP 2: Continuous Learning Phase")
        print("=" * 80)

        all_results = []
        learning_metrics = {
            'dates': [],
            'training_samples': [],
            'win_rates': [],
            'avg_returns': []
        }

        # Keep accumulating training data
        accumulated_X = X_initial.copy()
        accumulated_y = y_initial.copy()

        for idx, signal_date in enumerate(signal_dates, 1):
            print(f"\n{'=' * 80}")
            print(f"📅 Date {idx}/{len(signal_dates)}: {signal_date}")
            print(f"{'=' * 80}")

            signal_date_ts = pd.Timestamp(signal_date)

            # Get data for this date
            df_signal = features_with_labels[features_with_labels['DATE'] == signal_date_ts].copy()

            if df_signal.empty:
                print(f"⚠️ No data for {signal_date}")
                continue

            # Make predictions with CURRENT model
            df_predict = df_signal.dropna(subset=self.picker.feature_cols).copy()

            if df_predict.empty:
                print(f"⚠️ No valid features for {signal_date}")
                continue

            X_pred = df_predict[self.picker.feature_cols]
            probabilities = current_model.predict(X_pred)

            # Apply threshold
            threshold = self.picker.INITIAL_THRESHOLD
            picks_mask = probabilities >= threshold

            while picks_mask.sum() == 0 and threshold >= self.picker.MIN_THRESHOLD:
                threshold -= self.picker.THRESHOLD_STEP
                picks_mask = probabilities >= threshold

            # Create picks
            picks = pd.DataFrame({
                'Signal_Date': signal_date,
                'SC_CODE': df_predict.loc[picks_mask, 'SC_CODE'].values,
                'SC_NAME': df_predict.loc[picks_mask, 'SC_NAME'].values,
                'Close': df_predict.loc[picks_mask, 'Close'].values,
                'Probability': probabilities[picks_mask],
                'Threshold': threshold
            })

            # Get actual outcomes (if available)
            if label_col in df_predict.columns:
                actual_labels = df_predict.loc[picks_mask, label_col].values
                fwd_return_col = f"Return_fwd{self.picker.FORWARD_PERIOD}"

                if fwd_return_col in df_predict.columns:
                    picks['Return_fwd5'] = df_predict.loc[picks_mask, fwd_return_col].values
                    picks['Outcome'] = picks['Return_fwd5'].apply(
                        lambda x: 'Positive' if x > 0 else ('Negative' if x < 0 else 'Flat')
                    )

            print(f"   📊 Picks generated: {len(picks)}")

            if 'Return_fwd5' in picks.columns:
                valid = picks.dropna(subset=['Return_fwd5'])
                if len(valid) > 0:
                    wr = (valid['Return_fwd5'] > 0).sum() / len(valid) * 100
                    avg_ret = valid['Return_fwd5'].mean()
                    print(f"   📈 Win rate: {wr:.1f}% | Avg return: {avg_ret:.2f}%")

                    learning_metrics['dates'].append(signal_date)
                    learning_metrics['training_samples'].append(len(accumulated_X))
                    learning_metrics['win_rates'].append(wr)
                    learning_metrics['avg_returns'].append(avg_ret)

            all_results.append(picks)

            # LEARNING STEP: Add this date's outcomes to training data
            print(f"   🧠 Learning from outcomes...")

            # Get all data up to and including this date
            df_up_to_date = features_with_labels[features_with_labels['DATE'] <= signal_date_ts].copy()
            df_new_learning = df_up_to_date.dropna(subset=[label_col] + self.picker.feature_cols).copy()

            # Only add truly NEW data (not already in accumulated)
            new_samples = df_new_learning[~df_new_learning.index.isin(accumulated_X.index)]

            if len(new_samples) > 0:
                X_new = new_samples[self.picker.feature_cols]
                y_new = new_samples[label_col]

                # Add to accumulated data
                accumulated_X = pd.concat([accumulated_X, X_new], ignore_index=False)
                accumulated_y = pd.concat([accumulated_y, y_new], ignore_index=False)

                print(f"   ➕ Added {len(new_samples)} new training samples")
                print(f"   📚 Total training samples now: {len(accumulated_X):,}")

                # RETRAIN model on expanded dataset
                print(f"   🔄 Retraining model with updated knowledge...")

                train_data = lgb.Dataset(accumulated_X, label=accumulated_y)
                current_model = lgb.train(params, train_data, num_boost_round=200, callbacks=[lgb.log_evaluation(0)])

                print(f"   ✅ Model updated! (knows {len(accumulated_X):,} examples now)")
            else:
                print(f"   ℹ️ No new data to learn from")

        # Combine results
        if not all_results:
            print("\n❌ No results!")
            return pd.DataFrame(), learning_metrics

        results_df = pd.concat(all_results, ignore_index=True)

        print(f"\n" + "=" * 80)
        print("🎉 CONTINUOUS LEARNING BACKTEST COMPLETE")
        print("=" * 80)
        print(f"Total picks: {len(results_df)}")
        print(f"Model learned from: {len(accumulated_X):,} examples (started with {len(X_initial):,})")
        print(f"New knowledge gained: {len(accumulated_X) - len(X_initial):,} examples")

        return results_df, learning_metrics


def run_continuous_learning_year(
    year: int,
    frequency: str = 'weekly',
    n_stocks: Optional[int] = 200
) -> Tuple[pd.DataFrame, dict]:
    """
    Run continuous learning backtest for entire year

    Args:
        year: Year to test
        frequency: Signal frequency
        n_stocks: Training stock count

    Returns:
        (results_df, learning_metrics)
    """
    print("\n" + "=" * 80)
    print(f"🧠 CONTINUOUS LEARNING BACKTEST: {year}")
    print("=" * 80)
    print("Model will learn from each date and get progressively smarter!")
    print("=" * 80)

    # Get trading days
    from yearwise_backtest import get_trading_days_in_year

    signal_dates = get_trading_days_in_year(year, frequency)

    if not signal_dates:
        print("❌ No trading days found!")
        return pd.DataFrame(), {}

    print(f"✅ Will test {len(signal_dates)} dates with continuous learning")

    # Run backtest
    picker = StockPicker5Session()
    backtester = ContinuousLearningBacktest(picker)

    results, metrics = backtester.run_continuous_learning_backtest(
        signal_dates=signal_dates,
        n_stocks=n_stocks,
        lookback_days=730
    )

    # Save results
    output_dir = Path("stock_picker_data/results")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"continuous_learning_{year}_{frequency}.csv"
    results.to_csv(output_file, index=False)

    print(f"\n💾 Results saved: {output_file}")

    # Show learning curve
    if metrics['win_rates']:
        print(f"\n📈 LEARNING CURVE:")
        print(f"   First 10 dates avg win rate: {np.mean(metrics['win_rates'][:10]):.1f}%")
        print(f"   Last 10 dates avg win rate: {np.mean(metrics['win_rates'][-10:]):.1f}%")
        improvement = np.mean(metrics['win_rates'][-10:]) - np.mean(metrics['win_rates'][:10])
        print(f"   Improvement: {improvement:+.1f}%")

    return results, metrics


if __name__ == "__main__":
    import sys

    # Usage:
    # python continuous_learning_backtest.py 2024
    # python continuous_learning_backtest.py 2024 weekly
    # python continuous_learning_backtest.py 2024 weekly 500

    if len(sys.argv) < 2:
        print("Usage: python continuous_learning_backtest.py YEAR [frequency] [n_stocks]")
        print("")
        print("Examples:")
        print("  python continuous_learning_backtest.py 2024")
        print("  python continuous_learning_backtest.py 2024 weekly")
        print("  python continuous_learning_backtest.py 2024 weekly 500")
        sys.exit(1)

    year = int(sys.argv[1])
    frequency = sys.argv[2] if len(sys.argv) > 2 else 'weekly'
    n_stocks = None if len(sys.argv) > 3 and sys.argv[3].upper() == 'ALL' else int(sys.argv[3]) if len(sys.argv) > 3 else 200

    run_continuous_learning_year(year, frequency, n_stocks)
