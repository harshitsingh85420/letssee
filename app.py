"""
Stock Picker Web App - Access from anywhere!

Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
from datetime import date, timedelta
from pathlib import Path
import sys

# Import our stock picker
from get_picks import get_picks_for_date

# Page config
st.set_page_config(
    page_title="Stock Picker 5-Session",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for mobile-friendly design
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #00cc00;
        color: white;
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
st.title("📈 Stock Picker - 5 Session Predictor")
st.markdown("*Get stock picks for any date - optimized for mobile & desktop*")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")

    # Date selection
    signal_date = st.date_input(
        "📅 Select Date",
        value=date.today() - timedelta(days=7),
        max_value=date.today(),
        help="Pick a date to get stock recommendations"
    )

    # Number of stocks to train on
    n_stocks = st.selectbox(
        "📊 Training Stocks",
        options=[200, 500, 1000, "ALL"],
        index=0,
        help="More stocks = better model but slower"
    )

    if n_stocks == "ALL":
        n_stocks = None

    # Show outcomes toggle
    show_outcomes = st.checkbox(
        "Show Actual Outcomes",
        value=True,
        help="Show how the picks performed (only available for past dates with 5+ sessions of data)"
    )

    # Export options
    export_csv = st.checkbox(
        "Export to CSV",
        value=False,
        help="Download results as CSV file"
    )

    st.markdown("---")
    st.markdown("### 📱 Mobile Tips")
    st.markdown("- Swipe left/right on tables")
    st.markdown("- Pinch to zoom charts")
    st.markdown("- Bookmark this page!")

# Main content
st.markdown("---")

# Generate picks button
if st.button("🚀 Get Stock Picks", type="primary"):
    with st.spinner(f"🔍 Analyzing stocks for {signal_date}..."):
        try:
            # Get picks
            picks = get_picks_for_date(
                signal_date=signal_date,
                n_stocks=n_stocks,
                show_outcomes=show_outcomes
            )

            if picks is not None and len(picks) > 0:
                # Store in session state
                st.session_state['picks'] = picks
                st.session_state['signal_date'] = signal_date

                st.success(f"✅ Found {len(picks)} stock picks!")
            else:
                st.warning("⚠️ No picks found for this date. Try a different date.")

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.exception(e)

# Display results if available
if 'picks' in st.session_state:
    picks = st.session_state['picks']
    signal_date = st.session_state['signal_date']

    st.markdown("---")
    st.header(f"📋 Results for {signal_date}")

    # Summary metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Picks",
            len(picks),
            help="Number of stocks selected"
        )

    with col2:
        avg_prob = picks['Probability'].mean() * 100
        st.metric(
            "Avg Confidence",
            f"{avg_prob:.1f}%",
            help="Average model probability"
        )

    with col3:
        if 'Return_fwd5' in picks.columns:
            valid = picks.dropna(subset=['Return_fwd5'])
            if len(valid) > 0:
                win_rate = (valid['Return_fwd5'] > 0).sum() / len(valid) * 100
                st.metric(
                    "Win Rate",
                    f"{win_rate:.1f}%",
                    help="Percentage of profitable picks"
                )
        else:
            st.metric(
                "Win Rate",
                "N/A",
                help="Outcomes not available yet"
            )

    # Performance summary if available
    if 'Return_fwd5' in picks.columns:
        valid = picks.dropna(subset=['Return_fwd5'])
        if len(valid) > 0:
            st.markdown("### 📊 Performance Summary")

            perf_col1, perf_col2, perf_col3, perf_col4 = st.columns(4)

            with perf_col1:
                avg_return = valid['Return_fwd5'].mean()
                st.metric("Avg Return", f"{avg_return:.2f}%")

            with perf_col2:
                max_return = valid['Return_fwd5'].max()
                st.metric("Best Pick", f"{max_return:.2f}%")

            with perf_col3:
                min_return = valid['Return_fwd5'].min()
                st.metric("Worst Pick", f"{min_return:.2f}%")

            with perf_col4:
                positive = (valid['Return_fwd5'] > 0).sum()
                st.metric("Winners", f"{positive}/{len(valid)}")

            # Outcome distribution
            st.markdown("### 📈 Outcome Distribution")
            outcome_counts = valid['Outcome'].value_counts()
            st.bar_chart(outcome_counts)

    # Display picks table
    st.markdown("### 📋 Stock Picks")

    # Prepare display columns
    display_cols = ['SC_CODE', 'SC_NAME', 'Close', 'Probability', 'Threshold']

    if 'Return_fwd5' in picks.columns:
        display_cols.extend(['Close_fwd5', 'Return_fwd5', 'Outcome'])

    # Format the dataframe
    display_df = picks[display_cols].copy()
    display_df['Probability'] = (display_df['Probability'] * 100).round(2).astype(str) + '%'

    if 'Return_fwd5' in display_df.columns:
        display_df['Return_fwd5'] = display_df['Return_fwd5'].round(2).astype(str) + '%'

    # Show table
    st.dataframe(
        display_df,
        use_container_width=True,
        height=400
    )

    # Export to CSV
    if export_csv:
        csv = picks.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"stock_picks_{signal_date}.csv",
            mime="text/csv",
            use_container_width=True
        )

    # Top picks highlight
    st.markdown("### 🏆 Top 5 Picks")
    top_5 = picks.head(5)

    for idx, row in top_5.iterrows():
        with st.container():
            col_a, col_b, col_c = st.columns([2, 2, 2])

            with col_a:
                st.markdown(f"**{row['SC_NAME']}**")
                st.caption(f"Code: {row['SC_CODE']}")

            with col_b:
                st.markdown(f"**₹{row['Close']:.2f}**")
                st.caption(f"Confidence: {row['Probability']*100:.1f}%")

            with col_c:
                if 'Return_fwd5' in row and pd.notna(row['Return_fwd5']):
                    color = "🟢" if row['Return_fwd5'] > 0 else "🔴"
                    st.markdown(f"{color} **{row['Return_fwd5']:.2f}%**")
                    st.caption(row['Outcome'])
                else:
                    st.markdown("⏳ Pending")
                    st.caption("Waiting for outcome")

            st.markdown("---")

else:
    # Instructions when no picks loaded
    st.info("👆 Select a date and click 'Get Stock Picks' to start!")

    st.markdown("### 📖 How to Use")
    st.markdown("""
    1. **Select a date** from the sidebar (past dates show actual outcomes)
    2. **Choose training stocks** (200 is fast, more is better but slower)
    3. **Click 'Get Stock Picks'** to run the algorithm
    4. **Review the picks** and their confidence scores
    5. **Export to CSV** if you want to save the results

    #### 💡 Tips:
    - Past dates (7+ days ago) will show actual outcomes
    - Recent dates may not have full 5-session data yet
    - Higher probability = higher confidence in the prediction
    - Win rate shows historical accuracy
    """)

    st.markdown("### ⚠️ Disclaimer")
    st.warning("""
    This tool is for educational purposes only.
    Past performance does not guarantee future results.
    Always do your own research before investing.
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <small>Stock Picker 5-Session | Built with Streamlit | Mobile Optimized</small>
</div>
""", unsafe_allow_html=True)
