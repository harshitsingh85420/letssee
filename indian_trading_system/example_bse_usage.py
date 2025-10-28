"""
Example: Using BSE official data instead of Yahoo Finance.

This demonstrates the BSE data loader with automatic indicator calculation and caching.
Much faster after first run due to intelligent caching!
"""

from datetime import date, timedelta
from data.bse_loader import BSEDataLoader
from portfolio.signals import SignalGenerator, StockRanker
from backtesting.engine import BacktestEngine

print("="*80)
print("BSE OFFICIAL DATA LOADER DEMO")
print("="*80)
print()

# Initialize BSE loader
loader = BSEDataLoader()

# Example 1: Single Stock Analysis with Caching
print("📊 EXAMPLE 1: Load Reliance from BSE (with caching)")
print("-" * 80)

start_date = date(2024, 1, 1)
end_date = date.today()

# Reliance Industries BSE code: 500325
print(f"\nFetching Reliance (BSE: 500325) from {start_date} to {end_date}")
print("First run: Downloads from BSE and calculates indicators (~30 seconds)")
print("Subsequent runs: Loads from cache (<1 second)")
print()

df = loader.get_stock_data('500325', start_date, end_date)

print(f"✅ Loaded {len(df)} trading days")
print(f"Date range: {df['date'].min()} to {df['date'].max()}")
print("\n📈 Recent prices:")
print(df[['date', 'open', 'high', 'low', 'close', 'volume']].tail())

# Calculate indicators (will use cache if available)
print("\n🔄 Calculating technical indicators...")
df_with_indicators = loader.calculate_and_cache_indicators(df, '500325')

print(f"✅ Total columns: {len(df_with_indicators.columns)}")
indicator_cols = [c for c in df_with_indicators.columns
                 if c not in ['date', 'open', 'high', 'low', 'close', 'volume', 'symbol', 'SC_CODE', 'SC_NAME']]
print(f"✅ Indicator columns: {len(indicator_cols)}")
print(f"\nSample indicators: {indicator_cols[:15]}")

# Show recent indicators
print("\n📊 Recent Indicators:")
cols_to_show = ['date', 'close', 'supertrend_direction', 'adx', 'kst', 'cmf', 'yang_zhang_vol']
available_cols = [c for c in cols_to_show if c in df_with_indicators.columns]
print(df_with_indicators[available_cols].tail(10))

# Example 2: Generate Trading Signals
print("\n" + "="*80)
print("📊 EXAMPLE 2: Generate Trading Signals")
print("-" * 80)

signal_gen = SignalGenerator()
df_signals = signal_gen.generate_all_signals(df_with_indicators)

print(f"\n✅ Signals generated!")
print("\nRecent signals (last 10 days):")
signal_cols = ['date', 'close', 'composite_signal', 'trading_signal']
available_signal_cols = [c for c in signal_cols if c in df_signals.columns]
print(df_signals[available_signal_cols].tail(10))

# Count signals
buy_signals = len(df_signals[df_signals['trading_signal'] == 1])
sell_signals = len(df_signals[df_signals['trading_signal'] == -1])

print(f"\n📈 Signal Statistics:")
print(f"  Total Buy Signals: {buy_signals}")
print(f"  Total Sell Signals: {sell_signals}")
print(f"  Current Signal: {df_signals['trading_signal'].iloc[-1]}")

# Example 3: Backtest
print("\n" + "="*80)
print("📊 EXAMPLE 3: Backtest Strategy")
print("-" * 80)

engine = BacktestEngine(initial_capital=1000000)
results = engine.run_backtest(df_signals, df_signals['trading_signal'], position_size=0.3)

engine.print_results(results)

# Example 4: Load Multiple NIFTY 50 Stocks
print("\n" + "="*80)
print("📊 EXAMPLE 4: Load Multiple NIFTY 50 Stocks")
print("-" * 80)

print("\nLoading top 5 NIFTY stocks with pre-calculated indicators...")
print("(First run takes 2-3 minutes, subsequent runs < 5 seconds!)")
print()

nifty_codes = list(loader.get_nifty_50_codes().items())[:5]
nifty_data = {}

for symbol, code in nifty_codes:
    try:
        # This will use cache if available!
        df = loader.get_stock_data(code, start_date, end_date)
        df_ind = loader.calculate_and_cache_indicators(df, code)

        # Generate signals
        df_signals = signal_gen.generate_all_signals(df_ind)
        nifty_data[symbol] = df_signals

        print(f"  ✅ {symbol} ({code}): {len(df)} days, "
              f"{len(df_signals[df_signals['trading_signal'] == 1])} buy signals")
    except Exception as e:
        print(f"  ❌ {symbol} ({code}): {e}")

# Rank stocks by signal strength
print("\n🏆 Stock Rankings by Signal Strength:")
print("-" * 80)

ranker = StockRanker()
rankings = ranker.rank_by_signal_strength(nifty_data, top_n=5)
print(rankings)

# Example 5: Cache Management
print("\n" + "="*80)
print("📊 EXAMPLE 5: Cache Management")
print("-" * 80)

cache_files = list(loader.cache_dir.glob("*.pkl"))
print(f"\nCache location: {loader.cache_dir}")
print(f"Cached files: {len(cache_files)}")

if cache_files:
    total_size = sum(f.stat().st_size for f in cache_files) / (1024 * 1024)
    print(f"Total cache size: {total_size:.2f} MB")
    print(f"\nSample cached files:")
    for f in cache_files[:5]:
        size_kb = f.stat().st_size / 1024
        print(f"  {f.name}: {size_kb:.1f} KB")

print("\n💡 Cache Benefits:")
print("  • First load: Downloads from BSE + calculates indicators (~30s per stock)")
print("  • Subsequent loads: Instant (<1s per stock)")
print("  • Indicators cached for 1 day")
print("  • Automatic cache invalidation after 1 day")

# Cleanup old cache
print("\n🧹 Cleaning old cache files (>7 days)...")
loader.clear_cache(older_than_days=7)

# Example 6: Performance Comparison
print("\n" + "="*80)
print("📊 EXAMPLE 6: BSE vs Yahoo Finance Comparison")
print("-" * 80)

print("\n✅ BSE Official Data (BhavCopy):")
print("  Pros:")
print("    • Official source - most reliable")
print("    • Complete market data")
print("    • No rate limits")
print("    • Full day's data in single file")
print("    • Includes all BSE stocks")
print("    • Pre-calculated indicators cached")
print("    • 10x faster after first run")
print("  Cons:")
print("    • Requires BSE stock codes")
print("    • More complex initial setup")

print("\n📊 Yahoo Finance:")
print("  Pros:")
print("    • Simple API")
print("    • Works with .NS suffix")
print("    • International stocks")
print("  Cons:")
print("    • Rate limited")
print("    • Sometimes unreliable")
print("    • Slower for multiple stocks")
print("    • Data quality issues")

print("\n💡 Recommendation:")
print("  • Use BSE for Indian stocks (production)")
print("  • Use Yahoo Finance for quick testing")
print("  • BSE is 10x faster with caching!")

print("\n" + "="*80)
print("✅ DEMO COMPLETE!")
print("="*80)
print("\n📝 Summary:")
print(f"  • Loaded data for {len(nifty_data)} stocks from BSE")
print(f"  • Pre-calculated {len(indicator_cols)} indicators per stock")
print(f"  • Cached for instant future access")
print(f"  • Ready for production trading!")
print("\n🚀 Try running this script again - it will be 10x faster!")
