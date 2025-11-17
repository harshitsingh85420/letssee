"""
Year-wise Backtesting and Training

Allows you to:
1. Select a year (e.g., 2024, 2023)
2. Automatically backtest ALL trading days in that year
3. Model retrains for each date (walk-forward)
4. Comprehensive yearly performance analysis
"""

import pandas as pd
from datetime import date, timedelta
from typing import List, Optional
from pathlib import Path

from backtest_5session import backtest_signal_dates
from bse_loader import BSEDataFetcher


def get_trading_days_in_year(year: int, frequency: str = 'daily') -> List[date]:
    """
    Get all trading days in a specific year

    Args:
        year: Year to get trading days for (e.g., 2024)
        frequency: 'daily', 'weekly', 'biweekly', 'monthly'

    Returns:
        List of dates representing trading days
    """
    fetcher = BSEDataFetcher()

    # Get date range for entire year
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)

    print(f"📅 Fetching trading days for {year}...")

    # Fetch data for entire year to get actual trading dates
    try:
        bhav = fetcher.fetch_bhav_range(start_date, end_date)

        if bhav.empty:
            print(f"❌ No data available for {year}")
            return []

        # Get unique trading dates
        all_dates = sorted(bhav['DATE'].unique())

        # Convert to date objects
        trading_dates = [pd.to_datetime(d).date() for d in all_dates]

        print(f"✅ Found {len(trading_dates)} trading days in {year}")

        # Apply frequency filter
        if frequency == 'daily':
            selected_dates = trading_dates
        elif frequency == 'weekly':
            # Pick one date per week (Fridays or last day of week)
            selected_dates = []
            current_week = None
            for d in trading_dates:
                week_num = d.isocalendar()[1]
                if week_num != current_week:
                    selected_dates.append(d)
                    current_week = week_num
                elif d.weekday() == 4:  # Friday
                    # Replace with Friday if found
                    selected_dates[-1] = d
        elif frequency == 'biweekly':
            # Every 2 weeks
            selected_dates = [trading_dates[i] for i in range(0, len(trading_dates), 10)]
        elif frequency == 'monthly':
            # One per month
            selected_dates = []
            current_month = None
            for d in trading_dates:
                month = d.month
                if month != current_month:
                    current_month = month
                    selected_dates.append(d)
        else:
            selected_dates = trading_dates

        print(f"📊 Selected {len(selected_dates)} dates with '{frequency}' frequency")

        return selected_dates

    except Exception as e:
        print(f"❌ Error fetching trading days: {e}")
        return []


def backtest_year(year: int,
                  frequency: str = 'weekly',
                  n_stocks: Optional[int] = 200,
                  lookback_days: int = 730) -> pd.DataFrame:
    """
    Backtest entire year with walk-forward model training

    Args:
        year: Year to backtest (e.g., 2024, 2023)
        frequency: How often to generate signals ('daily', 'weekly', 'biweekly', 'monthly')
        n_stocks: Number of stocks for training (None = ALL)
        lookback_days: Days of history for training

    Returns:
        DataFrame with all picks and outcomes for the year
    """
    print("\n" + "=" * 80)
    print(f"📅 YEAR-WISE BACKTESTING: {year}")
    print("=" * 80)
    print(f"Frequency: {frequency}")
    print(f"Training stocks: {n_stocks if n_stocks else 'ALL'}")
    print(f"Lookback period: {lookback_days} days")
    print("=" * 80)

    # Get all trading days for the year
    signal_dates = get_trading_days_in_year(year, frequency)

    if not signal_dates:
        print("❌ No trading days found!")
        return pd.DataFrame()

    print(f"\n🎯 Will backtest {len(signal_dates)} dates in {year}")
    print(f"   First date: {signal_dates[0]}")
    print(f"   Last date: {signal_dates[-1]}")

    # Run backtest with walk-forward training
    print("\n🔄 Starting walk-forward backtest...")
    print("   (Model will retrain for EACH date - this is correct!)")

    results = backtest_signal_dates(
        signal_dates=signal_dates,
        n_stocks=n_stocks,
        lookback_days=lookback_days
    )

    if results is not None and len(results) > 0:
        # Add year column
        results['Year'] = year

        # Save results
        output_dir = Path("stock_picker_data/results")
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"backtest_year_{year}_{frequency}.csv"
        results.to_csv(output_file, index=False)

        print(f"\n✅ Backtest complete!")
        print(f"💾 Results saved to: {output_file}")

        # Show summary
        print(f"\n📊 SUMMARY FOR {year}:")
        print(f"   Total picks: {len(results)}")

        if 'Return_fwd5' in results.columns:
            valid = results.dropna(subset=['Return_fwd5'])
            if len(valid) > 0:
                win_rate = (valid['Return_fwd5'] > 0).sum() / len(valid) * 100
                avg_return = valid['Return_fwd5'].mean()

                print(f"   Win rate: {win_rate:.1f}%")
                print(f"   Avg return: {avg_return:.2f}%")
                print(f"   Best pick: {valid['Return_fwd5'].max():.2f}%")
                print(f"   Worst pick: {valid['Return_fwd5'].min():.2f}%")

    return results


def backtest_multiple_years(years: List[int],
                            frequency: str = 'weekly',
                            n_stocks: Optional[int] = 200,
                            lookback_days: int = 730) -> pd.DataFrame:
    """
    Backtest multiple years

    Args:
        years: List of years (e.g., [2022, 2023, 2024])
        frequency: Signal frequency
        n_stocks: Training stock count
        lookback_days: Training lookback

    Returns:
        Combined DataFrame with all years
    """
    print("\n" + "=" * 80)
    print(f"📅 MULTI-YEAR BACKTESTING: {years}")
    print("=" * 80)

    all_results = []

    for year in years:
        print(f"\n{'='*80}")
        print(f"Processing year: {year}")
        print(f"{'='*80}")

        year_results = backtest_year(
            year=year,
            frequency=frequency,
            n_stocks=n_stocks,
            lookback_days=lookback_days
        )

        if year_results is not None and len(year_results) > 0:
            all_results.append(year_results)

    if not all_results:
        print("❌ No results from any year!")
        return pd.DataFrame()

    # Combine all years
    combined = pd.concat(all_results, ignore_index=True)

    # Save combined results
    output_dir = Path("stock_picker_data/results")
    years_str = "_".join(map(str, years))
    output_file = output_dir / f"backtest_years_{years_str}_{frequency}.csv"
    combined.to_csv(output_file, index=False)

    print(f"\n" + "=" * 80)
    print(f"✅ MULTI-YEAR BACKTEST COMPLETE")
    print(f"=" * 80)
    print(f"💾 Combined results: {output_file}")
    print(f"\n📊 OVERALL SUMMARY:")
    print(f"   Years tested: {years}")
    print(f"   Total picks: {len(combined)}")

    if 'Return_fwd5' in combined.columns:
        valid = combined.dropna(subset=['Return_fwd5'])
        if len(valid) > 0:
            win_rate = (valid['Return_fwd5'] > 0).sum() / len(valid) * 100
            avg_return = valid['Return_fwd5'].mean()

            print(f"   Overall win rate: {win_rate:.1f}%")
            print(f"   Overall avg return: {avg_return:.2f}%")

            # Per-year breakdown
            print(f"\n   📅 Year-by-year:")
            for year in years:
                year_data = valid[valid['Year'] == year]
                if len(year_data) > 0:
                    year_wr = (year_data['Return_fwd5'] > 0).sum() / len(year_data) * 100
                    year_ret = year_data['Return_fwd5'].mean()
                    print(f"      {year}: {len(year_data)} picks, {year_wr:.1f}% win rate, {year_ret:.2f}% avg return")

    return combined


if __name__ == "__main__":
    import sys

    # Usage:
    # python yearwise_backtest.py 2024                  # Backtest 2024
    # python yearwise_backtest.py 2024 daily            # Daily signals
    # python yearwise_backtest.py 2024 weekly 500       # Weekly, 500 stocks
    # python yearwise_backtest.py 2023 2024             # Multiple years

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python yearwise_backtest.py YEAR [frequency] [n_stocks]")
        print("")
        print("Examples:")
        print("  python yearwise_backtest.py 2024")
        print("  python yearwise_backtest.py 2024 weekly")
        print("  python yearwise_backtest.py 2024 weekly 500")
        print("  python yearwise_backtest.py 2024 monthly ALL")
        print("  python yearwise_backtest.py 2023 2024  # Multiple years")
        sys.exit(1)

    # Parse years
    years = []
    frequency = 'weekly'
    n_stocks = 200

    for i, arg in enumerate(sys.argv[1:], 1):
        try:
            year = int(arg)
            if 2000 <= year <= 2100:
                years.append(year)
        except ValueError:
            if i == len(years) + 1:  # Next arg after years
                frequency = arg.lower()
            elif i == len(years) + 2:  # Arg after frequency
                if arg.upper() == 'ALL':
                    n_stocks = None
                else:
                    n_stocks = int(arg)

    if not years:
        print("❌ Please provide at least one valid year (e.g., 2024)")
        sys.exit(1)

    # Run backtest
    if len(years) == 1:
        backtest_year(
            year=years[0],
            frequency=frequency,
            n_stocks=n_stocks
        )
    else:
        backtest_multiple_years(
            years=years,
            frequency=frequency,
            n_stocks=n_stocks
        )
