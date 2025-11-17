"""
Incremental Model Training Module

Allows the model to learn from new data continuously:
- Tracks last training date
- Fetches only NEW data since last training
- Adds to existing training set
- Retrains model with expanded knowledge
- Model gets smarter over time!
"""

import pandas as pd
import pickle
from datetime import date, timedelta
from pathlib import Path
from typing import Optional, Tuple

from bse_loader import BSEDataFetcher
from momentum_features import prepare_features_all, add_forward_returns
from stock_picker_5session import StockPicker5Session
import lightgbm as lgb


class IncrementalModelTrainer:
    """
    Train model incrementally as new data becomes available
    """

    def __init__(self, base_dir: str = "./stock_picker_data"):
        self.base_dir = Path(base_dir)
        self.models_dir = self.base_dir / "models"
        self.models_dir.mkdir(parents=True, exist_ok=True)

        self.fetcher = BSEDataFetcher()
        self.picker = StockPicker5Session()

    def get_last_training_info(self) -> Optional[dict]:
        """Get information about the last training session"""
        model_path = self.models_dir / "model_5session.pkl"

        if not model_path.exists():
            return None

        try:
            with open(model_path, 'rb') as f:
                save_package = pickle.load(f)

            metadata = save_package.get('metadata', {})
            data_stats = save_package.get('data_stats', {})

            return {
                'train_date': metadata.get('train_date'),
                'last_data_date': metadata.get('last_data_date'),
                'n_training_samples': metadata.get('n_training_samples', 0),
                'cv_mean': metadata.get('cv_mean', 0),
                'data_start': metadata.get('data_start'),
                'data_end': metadata.get('data_end')
            }
        except Exception as e:
            print(f"⚠️ Error reading model metadata: {e}")
            return None

    def update_model_with_new_data(self, n_stocks: Optional[int] = None,
                                   lookback_days: int = 730) -> dict:
        """
        Update existing model with new data since last training

        Args:
            n_stocks: Number of stocks to use (None = ALL)
            lookback_days: Total lookback period in days

        Returns:
            dict with training results
        """
        print("\n" + "=" * 80)
        print("🔄 INCREMENTAL MODEL UPDATE")
        print("=" * 80)

        # Check if we have existing model
        last_info = self.get_last_training_info()

        if last_info and last_info.get('last_data_date'):
            print(f"📅 Last training date: {last_info['train_date']}")
            print(f"📊 Last data included: {last_info['last_data_date']}")
            print(f"🎯 Training samples: {last_info['n_training_samples']:,}")
            print(f"📈 Previous CV AUC: {last_info['cv_mean']:.4f}")

            # Calculate how much new data is available
            last_date = last_info['last_data_date']
            if isinstance(last_date, str):
                last_date = pd.to_datetime(last_date).date()
            elif isinstance(last_date, pd.Timestamp):
                last_date = last_date.date()

            today = date.today()
            new_days = (today - last_date).days

            print(f"\n✨ New data available: {new_days} days since last training")

            if new_days < 5:
                print(f"⚠️ Only {new_days} new days available. Consider waiting for more data.")
                response = input("Continue anyway? (y/n): ")
                if response.lower() != 'y':
                    return {'status': 'cancelled', 'reason': 'insufficient_new_data'}
        else:
            print("ℹ️ No existing model found - will train from scratch")

        # Fetch extended data range
        end_date = self.fetcher.prev_bday(date.today())
        start_date = end_date - timedelta(days=lookback_days)

        print(f"\n📥 Fetching data: {start_date} → {end_date}")
        bhav = self.fetcher.fetch_bhav_range(start_date, end_date)

        print(f"✅ Fetched {len(bhav):,} rows | {bhav['SC_CODE'].nunique()} unique stocks")

        # Get stock universe
        qualified_stocks = self.fetcher.get_stock_universe(bhav, self.picker.MIN_DATA_POINTS)
        bhav_qualified = bhav[bhav['SC_CODE'].isin(qualified_stocks)].copy()

        # Select training stocks
        if n_stocks and len(qualified_stocks) > n_stocks:
            liquidity = bhav_qualified.groupby('SC_CODE')['ValueTraded'].mean().sort_values(ascending=False)
            top_stocks = liquidity.head(n_stocks).index.tolist()
            bhav_train = bhav_qualified[bhav_qualified['SC_CODE'].isin(top_stocks)].copy()
            print(f"📊 Training on top {n_stocks} most liquid stocks")
        else:
            bhav_train = bhav_qualified.copy()
            print(f"📊 Training on ALL {len(qualified_stocks)} qualified stocks")

        # Compute features
        print(f"\n🔧 Computing features...")
        features = prepare_features_all(bhav_train)
        features_with_labels = add_forward_returns(features, periods=[self.picker.FORWARD_PERIOD])

        # Prepare training data
        print(f"\n🎯 Preparing training data...")
        X, y = self.picker.prepare_training_data(features_with_labels)

        if last_info:
            new_samples = len(X) - last_info['n_training_samples']
            print(f"📈 Training samples: {len(X):,} (+{new_samples:,} new samples)")
        else:
            print(f"📈 Training samples: {len(X):,}")

        # Train model
        print(f"\n🤖 Training model with expanded dataset...")
        self.picker.train_model(X, y)

        # Update metadata to track data range
        model_path = self.models_dir / "model_5session.pkl"
        with open(model_path, 'rb') as f:
            save_package = pickle.load(f)

        # Add data range tracking
        save_package['metadata']['data_start'] = start_date
        save_package['metadata']['data_end'] = end_date
        save_package['metadata']['last_data_date'] = end_date
        save_package['metadata']['incremental_update'] = True

        if last_info:
            save_package['metadata']['previous_samples'] = last_info['n_training_samples']
            save_package['metadata']['new_samples'] = len(X) - last_info['n_training_samples']

        # Save updated package
        with open(model_path, 'wb') as f:
            pickle.dump(save_package, f, protocol=pickle.HIGHEST_PROTOCOL)

        print(f"\n✅ Model updated and saved!")
        print(f"💾 Location: {model_path}")

        return {
            'status': 'success',
            'total_samples': len(X),
            'new_samples': len(X) - last_info['n_training_samples'] if last_info else len(X),
            'cv_mean': save_package['metadata']['cv_mean'],
            'data_range': f"{start_date} to {end_date}"
        }

    def auto_update_if_needed(self, min_new_days: int = 7, n_stocks: Optional[int] = None) -> bool:
        """
        Automatically update model if enough new data is available

        Args:
            min_new_days: Minimum new days required before updating
            n_stocks: Number of stocks to use

        Returns:
            True if model was updated, False otherwise
        """
        last_info = self.get_last_training_info()

        if not last_info or not last_info.get('last_data_date'):
            print("ℹ️ No existing model - use full training instead")
            return False

        last_date = last_info['last_data_date']
        if isinstance(last_date, str):
            last_date = pd.to_datetime(last_date).date()
        elif isinstance(last_date, pd.Timestamp):
            last_date = last_date.date()

        today = date.today()
        new_days = (today - last_date).days

        if new_days >= min_new_days:
            print(f"✨ {new_days} new days available - updating model!")
            result = self.update_model_with_new_data(n_stocks=n_stocks)
            return result['status'] == 'success'
        else:
            print(f"ℹ️ Only {new_days} new days - waiting for {min_new_days} days before update")
            return False


def run_incremental_update(n_stocks: Optional[int] = None, auto: bool = False):
    """
    Run incremental model update

    Args:
        n_stocks: Number of stocks (None = ALL)
        auto: If True, only update if enough new data available
    """
    trainer = IncrementalModelTrainer()

    if auto:
        # Auto mode - only update if 7+ new days available
        success = trainer.auto_update_if_needed(min_new_days=7, n_stocks=n_stocks)
        if success:
            print("\n🎉 Model successfully updated with new data!")
        else:
            print("\n⏸️ Model update skipped - not enough new data yet")
    else:
        # Manual mode - update regardless
        result = trainer.update_model_with_new_data(n_stocks=n_stocks)
        if result['status'] == 'success':
            print("\n🎉 Model successfully updated!")
            print(f"   New samples added: {result['new_samples']:,}")
            print(f"   Total samples: {result['total_samples']:,}")
            print(f"   CV AUC: {result['cv_mean']:.4f}")
        else:
            print(f"\n⚠️ Update not performed: {result.get('reason', 'unknown')}")


if __name__ == "__main__":
    import sys

    # Usage:
    # python incremental_training.py          # Update with 200 stocks
    # python incremental_training.py 500      # Update with 500 stocks
    # python incremental_training.py ALL      # Update with ALL stocks
    # python incremental_training.py auto     # Auto-update only if 7+ new days

    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg.lower() == 'auto':
            run_incremental_update(n_stocks=200, auto=True)
        elif arg.upper() == 'ALL':
            run_incremental_update(n_stocks=None, auto=False)
        else:
            try:
                n = int(arg)
                run_incremental_update(n_stocks=n, auto=False)
            except ValueError:
                print(f"Usage: python incremental_training.py [200|500|1000|ALL|auto]")
    else:
        # Default: update with 200 stocks
        run_incremental_update(n_stocks=200, auto=False)
