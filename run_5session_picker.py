#!/usr/bin/env python
"""
5-Session Stock Picker - Main Runner

Usage:
    # Daily mode (recommended - retrains every day)
    python run_5session_picker.py

    # With custom number of stocks for training
    python run_5session_picker.py --stocks 500
"""

import argparse
from stock_picker_5session import run_daily


def main():
    parser = argparse.ArgumentParser(
        description="5-Session Stock Picker - ML-Enhanced Momentum/Breakout System\n\n"
                    "Intention:\n"
                    "• Run today → tells which stocks to buy tomorrow\n"
                    "• Expects positive close in 5 sessions\n"
                    "• NSE data (priority) → BSE fallback\n"
                    "• ML model learns which patterns lead to 5-session gains\n"
                    "• Shows ALL qualifying stocks (no limit!)\n"
                    "• Daily retraining - model learns continuously\n",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--stocks',
        type=int,
        default=200,
        help='Number of most liquid stocks to use for training (default: 200, use 500+ for best results)'
    )

    args = parser.parse_args()

    # Run daily mode
    run_daily(n_stocks=args.stocks)


if __name__ == "__main__":
    main()
