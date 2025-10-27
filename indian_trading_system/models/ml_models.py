"""
Machine learning models for stock return prediction.
Includes Random Forest, XGBoost with purged cross-validation.
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple
import logging
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.model_selection import TimeSeriesSplit
from imblearn.over_sampling import SMOTE
import xgboost as xgb
import joblib

from ..utils.constants import (
    RF_N_ESTIMATORS, RF_MAX_DEPTH, RF_MIN_SAMPLES_SPLIT, RF_MIN_SAMPLES_LEAF,
    XGB_N_ESTIMATORS, XGB_MAX_DEPTH, XGB_LEARNING_RATE, XGB_SUBSAMPLE, XGB_COLSAMPLE_BYTREE,
    CV_N_SPLITS, CV_PURGE_DAYS, CV_EMBARGO_DAYS
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PurgedTimeSeriesSplit:
    """
    Time series cross-validator with purge and embargo.

    Purge: Remove samples around the test set to avoid leakage
    Embargo: Leave gap after test set to prevent look-ahead bias
    """

    def __init__(self, n_splits: int = CV_N_SPLITS,
                 purge_days: int = CV_PURGE_DAYS,
                 embargo_days: int = CV_EMBARGO_DAYS):
        """
        Initialize purged time series split.

        Args:
            n_splits: Number of splits
            purge_days: Days to purge around test set
            embargo_days: Days to embargo after test set
        """
        self.n_splits = n_splits
        self.purge_days = purge_days
        self.embargo_days = embargo_days

    def split(self, X: np.ndarray, y: np.ndarray = None, groups: np.ndarray = None):
        """
        Generate indices to split data into training and test set.

        Args:
            X: Features array
            y: Target array (unused)
            groups: Group labels (unused)

        Yields:
            Train and test indices
        """
        n_samples = len(X)
        test_size = n_samples // (self.n_splits + 1)

        for i in range(self.n_splits):
            # Test set indices
            test_start = (i + 1) * test_size
            test_end = test_start + test_size

            if test_end > n_samples:
                break

            # Training set: all data before test set (with purge)
            train_end = test_start - self.purge_days

            if train_end <= 0:
                continue

            train_indices = np.arange(0, train_end)
            test_indices = np.arange(test_start, min(test_end, n_samples))

            # Apply embargo: don't use samples right after test set for training in next fold
            if i < self.n_splits - 1:
                embargo_end = test_end + self.embargo_days
                if embargo_end < n_samples:
                    # Remove embargoed samples from future training sets
                    train_indices = train_indices[train_indices < test_start - self.purge_days]

            yield train_indices, test_indices


class MLModels:
    """
    Machine learning models for stock return prediction.
    """

    def __init__(self):
        """Initialize ML models."""
        self.rf_model = None
        self.xgb_model = None
        self.feature_names = None

    def train_random_forest(self, X_train: np.ndarray, y_train: np.ndarray,
                           use_smote: bool = True) -> RandomForestClassifier:
        """
        Train Random Forest model.

        Args:
            X_train: Training features
            y_train: Training target
            use_smote: Whether to use SMOTE for class imbalance

        Returns:
            Trained Random Forest model
        """
        logger.info("Training Random Forest...")

        # Handle class imbalance with SMOTE
        if use_smote:
            try:
                smote = SMOTE(random_state=42)
                X_train, y_train = smote.fit_resample(X_train, y_train)
                logger.info(f"Applied SMOTE: new shape {X_train.shape}")
            except Exception as e:
                logger.warning(f"SMOTE failed: {e}. Training without SMOTE.")

        # Train model
        model = RandomForestClassifier(
            n_estimators=RF_N_ESTIMATORS,
            max_depth=RF_MAX_DEPTH,
            min_samples_split=RF_MIN_SAMPLES_SPLIT,
            min_samples_leaf=RF_MIN_SAMPLES_LEAF,
            random_state=42,
            n_jobs=-1,
            class_weight='balanced'
        )

        model.fit(X_train, y_train)
        logger.info("Random Forest training complete")

        return model

    def train_xgboost(self, X_train: np.ndarray, y_train: np.ndarray,
                     use_smote: bool = True) -> xgb.XGBClassifier:
        """
        Train XGBoost model.

        Args:
            X_train: Training features
            y_train: Training target
            use_smote: Whether to use SMOTE for class imbalance

        Returns:
            Trained XGBoost model
        """
        logger.info("Training XGBoost...")

        # Handle class imbalance with SMOTE
        if use_smote:
            try:
                smote = SMOTE(random_state=42)
                X_train, y_train = smote.fit_resample(X_train, y_train)
                logger.info(f"Applied SMOTE: new shape {X_train.shape}")
            except Exception as e:
                logger.warning(f"SMOTE failed: {e}. Training without SMOTE.")

        # Calculate scale_pos_weight for imbalanced classes
        n_pos = np.sum(y_train == 1)
        n_neg = np.sum(y_train == 0)
        scale_pos_weight = n_neg / n_pos if n_pos > 0 else 1

        # Train model
        model = xgb.XGBClassifier(
            n_estimators=XGB_N_ESTIMATORS,
            max_depth=XGB_MAX_DEPTH,
            learning_rate=XGB_LEARNING_RATE,
            subsample=XGB_SUBSAMPLE,
            colsample_bytree=XGB_COLSAMPLE_BYTREE,
            scale_pos_weight=scale_pos_weight,
            random_state=42,
            n_jobs=-1,
            eval_metric='logloss'
        )

        model.fit(X_train, y_train)
        logger.info("XGBoost training complete")

        return model

    def evaluate_model(self, model, X_test: np.ndarray, y_test: np.ndarray) -> Dict:
        """
        Evaluate model performance.

        Args:
            model: Trained model
            X_test: Test features
            y_test: Test target

        Returns:
            Dictionary of metrics
        """
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1]

        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, zero_division=0),
            'recall': recall_score(y_test, y_pred, zero_division=0),
            'f1': f1_score(y_test, y_pred, zero_division=0),
            'roc_auc': roc_auc_score(y_test, y_pred_proba) if len(np.unique(y_test)) > 1 else 0
        }

        return metrics

    def cross_validate(self, X: np.ndarray, y: np.ndarray,
                      model_type: str = 'rf') -> Dict:
        """
        Perform purged cross-validation.

        Args:
            X: Features
            y: Target
            model_type: 'rf' for Random Forest or 'xgb' for XGBoost

        Returns:
            Dictionary with cross-validation results
        """
        logger.info(f"Starting purged cross-validation for {model_type}...")

        cv = PurgedTimeSeriesSplit(
            n_splits=CV_N_SPLITS,
            purge_days=CV_PURGE_DAYS,
            embargo_days=CV_EMBARGO_DAYS
        )

        cv_results = {
            'train_metrics': [],
            'test_metrics': [],
            'feature_importance': []
        }

        for fold, (train_idx, test_idx) in enumerate(cv.split(X, y)):
            logger.info(f"\nFold {fold + 1}/{CV_N_SPLITS}")
            logger.info(f"Train size: {len(train_idx)}, Test size: {len(test_idx)}")

            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]

            # Train model
            if model_type == 'rf':
                model = self.train_random_forest(X_train, y_train)
            elif model_type == 'xgb':
                model = self.train_xgboost(X_train, y_train)
            else:
                raise ValueError(f"Unknown model type: {model_type}")

            # Evaluate on train and test
            train_metrics = self.evaluate_model(model, X_train, y_train)
            test_metrics = self.evaluate_model(model, X_test, y_test)

            logger.info(f"Train metrics: {train_metrics}")
            logger.info(f"Test metrics: {test_metrics}")

            cv_results['train_metrics'].append(train_metrics)
            cv_results['test_metrics'].append(test_metrics)

            # Feature importance
            if hasattr(model, 'feature_importances_'):
                cv_results['feature_importance'].append(model.feature_importances_)

        # Calculate average metrics
        avg_train_metrics = {
            metric: np.mean([fold[metric] for fold in cv_results['train_metrics']])
            for metric in cv_results['train_metrics'][0].keys()
        }

        avg_test_metrics = {
            metric: np.mean([fold[metric] for fold in cv_results['test_metrics']])
            for metric in cv_results['test_metrics'][0].keys()
        }

        logger.info("\nAverage Train Metrics:")
        for metric, value in avg_train_metrics.items():
            logger.info(f"  {metric}: {value:.4f}")

        logger.info("\nAverage Test Metrics:")
        for metric, value in avg_test_metrics.items():
            logger.info(f"  {metric}: {value:.4f}")

        cv_results['avg_train_metrics'] = avg_train_metrics
        cv_results['avg_test_metrics'] = avg_test_metrics

        # Average feature importance
        if cv_results['feature_importance']:
            cv_results['avg_feature_importance'] = np.mean(cv_results['feature_importance'], axis=0)

        return cv_results

    def train_final_models(self, X: np.ndarray, y: np.ndarray,
                          feature_names: list = None):
        """
        Train final models on all data.

        Args:
            X: Features
            y: Target
            feature_names: List of feature names
        """
        logger.info("Training final models on all data...")

        self.feature_names = feature_names

        # Train Random Forest
        self.rf_model = self.train_random_forest(X, y)

        # Train XGBoost
        self.xgb_model = self.train_xgboost(X, y)

        logger.info("Final models trained successfully")

    def predict(self, X: np.ndarray, model_type: str = 'ensemble') -> np.ndarray:
        """
        Make predictions.

        Args:
            X: Features
            model_type: 'rf', 'xgb', or 'ensemble'

        Returns:
            Predictions (probabilities)
        """
        if model_type == 'rf':
            if self.rf_model is None:
                raise ValueError("Random Forest model not trained")
            return self.rf_model.predict_proba(X)[:, 1]

        elif model_type == 'xgb':
            if self.xgb_model is None:
                raise ValueError("XGBoost model not trained")
            return self.xgb_model.predict_proba(X)[:, 1]

        elif model_type == 'ensemble':
            if self.rf_model is None or self.xgb_model is None:
                raise ValueError("Models not trained")

            # Average predictions from both models
            rf_pred = self.rf_model.predict_proba(X)[:, 1]
            xgb_pred = self.xgb_model.predict_proba(X)[:, 1]
            return (rf_pred + xgb_pred) / 2

        else:
            raise ValueError(f"Unknown model type: {model_type}")

    def get_feature_importance(self, top_n: int = 20) -> pd.DataFrame:
        """
        Get feature importance from trained models.

        Args:
            top_n: Number of top features to return

        Returns:
            DataFrame with feature importance
        """
        if self.rf_model is None or self.xgb_model is None:
            raise ValueError("Models not trained")

        if self.feature_names is None:
            raise ValueError("Feature names not provided")

        # Get importance from both models
        rf_importance = self.rf_model.feature_importances_
        xgb_importance = self.xgb_model.feature_importances_

        # Average importance
        avg_importance = (rf_importance + xgb_importance) / 2

        # Create DataFrame
        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'rf_importance': rf_importance,
            'xgb_importance': xgb_importance,
            'avg_importance': avg_importance
        })

        # Sort by average importance
        importance_df = importance_df.sort_values('avg_importance', ascending=False)

        return importance_df.head(top_n)

    def save_models(self, filepath_prefix: str):
        """
        Save trained models to disk.

        Args:
            filepath_prefix: Prefix for model files
        """
        if self.rf_model:
            joblib.dump(self.rf_model, f"{filepath_prefix}_rf.pkl")
            logger.info(f"Saved Random Forest to {filepath_prefix}_rf.pkl")

        if self.xgb_model:
            joblib.dump(self.xgb_model, f"{filepath_prefix}_xgb.pkl")
            logger.info(f"Saved XGBoost to {filepath_prefix}_xgb.pkl")

    def load_models(self, filepath_prefix: str):
        """
        Load trained models from disk.

        Args:
            filepath_prefix: Prefix for model files
        """
        try:
            self.rf_model = joblib.load(f"{filepath_prefix}_rf.pkl")
            logger.info(f"Loaded Random Forest from {filepath_prefix}_rf.pkl")
        except Exception as e:
            logger.warning(f"Failed to load Random Forest: {e}")

        try:
            self.xgb_model = joblib.load(f"{filepath_prefix}_xgb.pkl")
            logger.info(f"Loaded XGBoost from {filepath_prefix}_xgb.pkl")
        except Exception as e:
            logger.warning(f"Failed to load XGBoost: {e}")


if __name__ == "__main__":
    # Example usage
    from ..data.loader import DataLoader
    from .features import FeatureEngineer

    loader = DataLoader()
    df = loader.load_stock_data('RELIANCE.NS')

    if df is not None:
        # Create features
        engineer = FeatureEngineer()
        df_with_features = engineer.create_all_features(df)
        X, y, feature_names = engineer.prepare_ml_data(df_with_features)

        print(f"Data shape: X={X.shape}, y={y.shape}")
        print(f"Positive samples: {y.sum()} ({y.mean():.1%})")

        # Train models
        ml_models = MLModels()

        # Cross-validate
        print("\n=== Random Forest Cross-Validation ===")
        rf_cv_results = ml_models.cross_validate(X, y, model_type='rf')

        print("\n=== XGBoost Cross-Validation ===")
        xgb_cv_results = ml_models.cross_validate(X, y, model_type='xgb')

        # Train final models
        ml_models.train_final_models(X, y, feature_names)

        # Feature importance
        print("\n=== Top 20 Important Features ===")
        print(ml_models.get_feature_importance(top_n=20))
