"""
Stock Picker Web App - Complete Feature Set

Access all features from anywhere:
- Get stock picks for specific dates
- Run backtests over date ranges
- Train and manage models
- View historical performance

Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
from datetime import date, timedelta, datetime
from pathlib import Path
import sys
import io

# Import our stock picker modules
from get_picks import get_picks_for_date
from stock_picker_5session import StockPicker5Session
from bse_loader import BSEDataFetcher

# Page config
st.set_page_config(
    page_title="Stock Picker 5-Session",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .stButton>button {
        width: 100%;
        font-weight: bold;
        padding: 0.5rem;
        font-size: 1.1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    h1 {
        color: #1f77b4;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("📈 Stock Picker - Complete Trading System")
st.markdown("*All features in one place - optimized for mobile & desktop*")

# Create tabs for different features
tab1, tab2, tab3, tab4 = st.tabs(["📅 Get Picks", "📊 Backtest", "🎓 Train Model", "📈 Performance"])

# ==================== TAB 1: GET PICKS ====================
with tab1:
    st.header("📅 Get Stock Picks for Specific Date")
    st.markdown("Get stock recommendations for any date and see actual outcomes")

    col1, col2 = st.columns([2, 1])

    with col1:
        pick_date = st.date_input(
            "Select Date",
            value=date.today() - timedelta(days=7),
            max_value=date.today(),
            key="pick_date",
            help="Pick a date to get stock recommendations"
        )

    with col2:
        pick_n_stocks = st.selectbox(
            "Training Stocks",
            options=[200, 500, 1000, "ALL"],
            index=0,
            key="pick_n_stocks",
            help="More stocks = better model but slower"
        )

    if pick_n_stocks == "ALL":
        pick_n_stocks = None

    pick_show_outcomes = st.checkbox(
        "Show Actual Outcomes",
        value=True,
        key="pick_outcomes",
        help="Show how the picks performed (only for past dates with 5+ sessions)"
    )

    if st.button("🚀 Get Stock Picks", type="primary", key="get_picks_btn"):
        with st.spinner(f"🔍 Analyzing stocks for {pick_date}..."):
            try:
                picks = get_picks_for_date(
                    signal_date=pick_date,
                    n_stocks=pick_n_stocks,
                    show_outcomes=pick_show_outcomes
                )

                if picks is not None and len(picks) > 0:
                    st.session_state['picks'] = picks
                    st.session_state['pick_date'] = pick_date
                    st.success(f"✅ Found {len(picks)} stock picks!")
                else:
                    st.warning("⚠️ No picks found for this date. Try a different date.")

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                with st.expander("Show Error Details"):
                    st.exception(e)

    # Display picks if available
    if 'picks' in st.session_state:
        picks = st.session_state['picks']
        pick_date = st.session_state['pick_date']

        st.markdown("---")
        st.subheader(f"📋 Results for {pick_date}")

        # Metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Picks", len(picks))

        with col2:
            avg_prob = picks['Probability'].mean() * 100
            st.metric("Avg Confidence", f"{avg_prob:.1f}%")

        with col3:
            if 'Return_fwd5' in picks.columns:
                valid = picks.dropna(subset=['Return_fwd5'])
                if len(valid) > 0:
                    win_rate = (valid['Return_fwd5'] > 0).sum() / len(valid) * 100
                    st.metric("Win Rate", f"{win_rate:.1f}%")
            else:
                st.metric("Win Rate", "N/A")

        # Performance summary
        if 'Return_fwd5' in picks.columns:
            valid = picks.dropna(subset=['Return_fwd5'])
            if len(valid) > 0:
                st.markdown("#### 📊 Performance Summary")

                perf_col1, perf_col2, perf_col3, perf_col4 = st.columns(4)

                with perf_col1:
                    st.metric("Avg Return", f"{valid['Return_fwd5'].mean():.2f}%")

                with perf_col2:
                    st.metric("Best Pick", f"{valid['Return_fwd5'].max():.2f}%")

                with perf_col3:
                    st.metric("Worst Pick", f"{valid['Return_fwd5'].min():.2f}%")

                with perf_col4:
                    positive = (valid['Return_fwd5'] > 0).sum()
                    st.metric("Winners", f"{positive}/{len(valid)}")

                # Chart
                outcome_counts = valid['Outcome'].value_counts()
                st.bar_chart(outcome_counts)

        # Table
        st.markdown("#### 📋 Stock Picks")

        display_cols = ['SC_CODE', 'SC_NAME', 'Close', 'Probability', 'Threshold']
        if 'Return_fwd5' in picks.columns:
            display_cols.extend(['Close_fwd5', 'Return_fwd5', 'Outcome'])

        display_df = picks[display_cols].copy()
        display_df['Probability'] = (display_df['Probability'] * 100).round(2).astype(str) + '%'

        if 'Return_fwd5' in display_df.columns:
            display_df['Return_fwd5'] = display_df['Return_fwd5'].round(2).astype(str) + '%'

        st.dataframe(display_df, width='stretch', height=400)

        # Export
        csv = picks.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"stock_picks_{pick_date}.csv",
            mime="text/csv"
        )

# ==================== TAB 2: BACKTEST ====================
with tab2:
    st.header("📊 Backtest Over Date Range")
    st.markdown("Run backtesting over multiple dates to evaluate strategy performance")

    col1, col2 = st.columns(2)

    with col1:
        backtest_start = st.date_input(
            "Start Date",
            value=date.today() - timedelta(days=90),
            max_value=date.today(),
            key="backtest_start"
        )

    with col2:
        backtest_end = st.date_input(
            "End Date",
            value=date.today() - timedelta(days=7),
            max_value=date.today(),
            key="backtest_end"
        )

    col3, col4 = st.columns(2)

    with col3:
        backtest_n_stocks = st.selectbox(
            "Training Stocks",
            options=[200, 500, 1000, "ALL"],
            index=0,
            key="backtest_n_stocks"
        )

    with col4:
        backtest_freq = st.selectbox(
            "Backtest Frequency",
            options=["Weekly", "Bi-weekly", "Monthly"],
            index=0,
            key="backtest_freq"
        )

    if backtest_n_stocks == "ALL":
        backtest_n_stocks = None

    # Map frequency to days
    freq_map = {"Weekly": 7, "Bi-weekly": 14, "Monthly": 30}

    if st.button("🚀 Run Backtest", type="primary", key="backtest_btn"):
        with st.spinner("🔍 Running backtest... This may take a while..."):
            try:
                # Import backtest function
                from backtest_5session import backtest_signal_dates

                # Generate signal dates
                signal_dates = []
                current = backtest_start
                while current <= backtest_end:
                    signal_dates.append(current)
                    current += timedelta(days=freq_map[backtest_freq])

                st.info(f"📅 Backtesting {len(signal_dates)} dates: {signal_dates[0]} to {signal_dates[-1]}")

                # Run backtest
                results = backtest_signal_dates(
                    signal_dates=signal_dates,
                    n_stocks=backtest_n_stocks,
                    lookback_days=730
                )

                if results is not None and len(results) > 0:
                    st.session_state['backtest_results'] = results
                    st.success(f"✅ Backtest complete! {len(results)} picks analyzed")
                else:
                    st.warning("⚠️ No results from backtest")

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                with st.expander("Show Error Details"):
                    st.exception(e)

    # Display backtest results
    if 'backtest_results' in st.session_state:
        results = st.session_state['backtest_results']

        st.markdown("---")
        st.subheader("📊 Backtest Results")

        # Overall metrics
        valid = results.dropna(subset=['Return_fwd5'])

        if len(valid) > 0:
            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                st.metric("Total Picks", len(results))

            with col2:
                win_rate = (valid['Return_fwd5'] > 0).sum() / len(valid) * 100
                st.metric("Win Rate", f"{win_rate:.1f}%")

            with col3:
                avg_return = valid['Return_fwd5'].mean()
                st.metric("Avg Return", f"{avg_return:.2f}%")

            with col4:
                st.metric("Best Pick", f"{valid['Return_fwd5'].max():.2f}%")

            with col5:
                st.metric("Worst Pick", f"{valid['Return_fwd5'].min():.2f}%")

            # Performance by date
            st.markdown("#### 📅 Performance by Signal Date")
            date_performance = valid.groupby('Signal_Date').agg({
                'Return_fwd5': ['count', 'mean', lambda x: (x > 0).sum() / len(x) * 100]
            }).round(2)
            date_performance.columns = ['Picks', 'Avg Return (%)', 'Win Rate (%)']
            st.dataframe(date_performance, width='stretch')

            # Chart: Returns distribution
            st.markdown("#### 📈 Returns Distribution")
            st.bar_chart(valid['Return_fwd5'])

            # Full results table
            st.markdown("#### 📋 All Picks")
            st.dataframe(results, width='stretch', height=400)

            # Export
            csv = results.to_csv(index=False)
            st.download_button(
                label="📥 Download Backtest Results CSV",
                data=csv,
                file_name=f"backtest_{backtest_start}_{backtest_end}.csv",
                mime="text/csv"
            )

# ==================== TAB 3: TRAIN MODEL ====================
with tab3:
    st.header("🎓 Train & Manage Model")
    st.markdown("Train a new model or view existing model details")

    picker = StockPicker5Session()

    # Check if model exists
    model_exists = picker.model_exists()

    if model_exists:
        st.success("✅ Trained model found!")

        if st.button("📦 Load Model Details", key="load_model_btn"):
            with st.spinner("Loading model..."):
                if picker.load_model():
                    st.session_state['model_loaded'] = True
    else:
        st.info("ℹ️ No trained model found. Train a new one below.")

    # Model training section
    st.markdown("---")
    st.subheader("🎓 Train New Model")

    col1, col2 = st.columns(2)

    with col1:
        train_n_stocks = st.selectbox(
            "Training Stocks",
            options=[200, 500, 1000, "ALL"],
            index=2,
            key="train_n_stocks",
            help="More stocks = better model but slower (ALL = 4000+ stocks, 15-20 min)"
        )

    with col2:
        train_lookback = st.number_input(
            "Lookback Days",
            min_value=365,
            max_value=1095,
            value=730,
            step=30,
            key="train_lookback",
            help="Number of days of historical data to use for training"
        )

    if st.button("🚀 Train New Model", type="primary", key="train_btn"):
        with st.spinner("🎓 Training model... This will take 10-20 minutes..."):
            try:
                # Capture output
                from io import StringIO
                import sys

                # Create progress container
                progress_container = st.empty()

                progress_container.info("📥 Fetching data...")

                # Set parameters
                if train_n_stocks == "ALL":
                    train_n_stocks = None

                picker_train = StockPicker5Session()
                picker_train.LOOKBACK_DAYS = train_lookback

                # Fetch data
                raw_bhav, features_with_labels = picker_train.fetch_data()

                progress_container.info("🎯 Preparing training data...")

                # Prepare training data
                X, y = picker_train.prepare_training_data(features_with_labels)

                progress_container.info("🤖 Training model... (this takes time)")

                # Train
                picker_train.train_model(X, y)

                progress_container.success("✅ Model training complete!")
                st.session_state['model_trained'] = True
                st.balloons()

            except Exception as e:
                st.error(f"❌ Training failed: {str(e)}")
                with st.expander("Show Error Details"):
                    st.exception(e)

    # Display loaded model info
    if 'model_loaded' in st.session_state and st.session_state['model_loaded']:
        st.markdown("---")
        st.subheader("📊 Model Information")

        if picker.model is not None:
            st.success(f"✅ Model loaded with {len(picker.feature_cols)} features")

            # Show feature importance if available
            if hasattr(picker.model, 'feature_importance'):
                importance_df = pd.DataFrame({
                    'Feature': picker.feature_cols,
                    'Importance': picker.model.feature_importance(importance_type='gain')
                }).sort_values('Importance', ascending=False).head(20)

                st.markdown("#### Top 20 Features by Importance")
                st.bar_chart(importance_df.set_index('Feature'))

# ==================== TAB 4: PERFORMANCE DASHBOARD ====================
with tab4:
    st.header("📈 Historical Performance Dashboard")
    st.markdown("View historical backtest results and performance metrics")

    # Look for CSV files in results directory
    results_dir = Path("stock_picker_data/results")

    if results_dir.exists():
        csv_files = list(results_dir.glob("*.csv"))

        if csv_files:
            st.markdown(f"📁 Found {len(csv_files)} result files")

            # File selector
            selected_file = st.selectbox(
                "Select Results File",
                options=[f.name for f in csv_files],
                key="perf_file"
            )

            if selected_file:
                file_path = results_dir / selected_file

                try:
                    df = pd.read_csv(file_path)

                    st.success(f"✅ Loaded {len(df)} picks from {selected_file}")

                    # Calculate metrics
                    if 'Return_fwd5' in df.columns:
                        valid = df.dropna(subset=['Return_fwd5'])

                        if len(valid) > 0:
                            # Overall metrics
                            col1, col2, col3, col4, col5 = st.columns(5)

                            with col1:
                                st.metric("Total Picks", len(valid))

                            with col2:
                                win_rate = (valid['Return_fwd5'] > 0).sum() / len(valid) * 100
                                st.metric("Win Rate", f"{win_rate:.1f}%")

                            with col3:
                                avg_return = valid['Return_fwd5'].mean()
                                st.metric("Avg Return", f"{avg_return:.2f}%")

                            with col4:
                                st.metric("Best", f"{valid['Return_fwd5'].max():.2f}%")

                            with col5:
                                st.metric("Worst", f"{valid['Return_fwd5'].min():.2f}%")

                            # Performance over time
                            if 'Signal_Date' in df.columns:
                                st.markdown("#### 📅 Performance Over Time")

                                date_perf = valid.groupby('Signal_Date')['Return_fwd5'].agg(['mean', 'count'])
                                date_perf.columns = ['Avg Return', 'Count']

                                st.line_chart(date_perf['Avg Return'])

                            # Returns distribution
                            st.markdown("#### 📊 Returns Distribution")

                            import matplotlib.pyplot as plt

                            fig, ax = plt.subplots(figsize=(10, 4))
                            ax.hist(valid['Return_fwd5'], bins=50, edgecolor='black')
                            ax.axvline(0, color='red', linestyle='--', linewidth=2)
                            ax.set_xlabel('5-Session Return (%)')
                            ax.set_ylabel('Frequency')
                            ax.set_title('Distribution of Returns')
                            st.pyplot(fig)

                            # Top/Bottom performers
                            col_left, col_right = st.columns(2)

                            with col_left:
                                st.markdown("#### 🏆 Top 10 Performers")
                                top_10 = valid.nlargest(10, 'Return_fwd5')[['SC_NAME', 'Return_fwd5']]
                                st.dataframe(top_10, width='stretch')

                            with col_right:
                                st.markdown("#### 📉 Bottom 10 Performers")
                                bottom_10 = valid.nsmallest(10, 'Return_fwd5')[['SC_NAME', 'Return_fwd5']]
                                st.dataframe(bottom_10, width='stretch')

                            # Full data
                            st.markdown("#### 📋 Full Results")
                            st.dataframe(df, width='stretch', height=400)

                    else:
                        st.warning("⚠️ No return data in this file")
                        st.dataframe(df, width='stretch', height=400)

                except Exception as e:
                    st.error(f"❌ Error loading file: {str(e)}")

        else:
            st.info("ℹ️ No results files found. Run a backtest first!")

    else:
        st.info("ℹ️ No results directory found. Run a backtest first!")

    # Upload custom CSV
    st.markdown("---")
    st.subheader("📤 Upload Custom Results")

    uploaded_file = st.file_uploader(
        "Upload CSV file",
        type=['csv'],
        key="upload_csv"
    )

    if uploaded_file:
        try:
            df_upload = pd.read_csv(uploaded_file)
            st.success(f"✅ Loaded {len(df_upload)} rows")
            st.dataframe(df_upload, width='stretch', height=400)

            # Export processed
            csv_out = df_upload.to_csv(index=False)
            st.download_button(
                label="📥 Download Processed CSV",
                data=csv_out,
                file_name="processed_results.csv",
                mime="text/csv"
            )

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <small>Stock Picker 5-Session Complete System | Built with Streamlit | Mobile Optimized</small>
</div>
""", unsafe_allow_html=True)
