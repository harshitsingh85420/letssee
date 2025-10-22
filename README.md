# Stock Generator

A Python application that generates random stock market data for testing and demonstration purposes.

## Features

- Generates realistic stock market data including:
  - Stock symbols and company names
  - Current prices
  - Price changes (both absolute and percentage)
  - Trading volumes
  - Market capitalization
  - Sector classification
- Displays formatted stock tables
- Provides market summary statistics
- Includes top gainers and losers

## Requirements

- Python 3.9 or higher
- No external dependencies (uses only Python standard library)

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd letssee
```

2. Make the script executable (optional):
```bash
chmod +x stock_generator.py
```

## Usage

### Basic Usage

Run the stock generator:

```bash
python stock_generator.py
```

or

```bash
python3 stock_generator.py
```

### Using as a Module

You can also import and use the stock generator in your own Python code:

```python
from stock_generator import StockGenerator

# Create a generator instance
generator = StockGenerator()

# Generate all available stocks
stocks = generator.generate_stocks()

# Generate a specific number of random stocks
stocks = generator.generate_stocks(count=5)

# Generate a custom stock
custom_stock = generator.generate_custom_stock("ACME", "Acme Corporation", "Technology")

# Access stock data
for stock in stocks:
    print(f"{stock.symbol}: ${stock.price} ({stock.change_percent:+.2f}%)")
```

## Output Example

```
🚀 Stock Data Generator
==================================================

📊 Generating stock market data...

====================================================================================================
SYMBOL | COMPANY NAME              |    PRICE | CHANGE |          VOLUME
====================================================================================================
AAPL   | Apple Inc.                |   $234.56 |  +3.45 (+1.50%) | Vol: 45,234,567
AMZN   | Amazon.com Inc.           |   $178.90 |  -2.10 (-1.16%) | Vol: 38,901,234
...
====================================================================================================

Generated 20 stocks at 2025-10-22 09:38:00

📈 Market Summary:
  • Total Stocks: 20
  • Average Price: $156.78
  • Total Volume: 890,456,789
  • Gainers: 12 (60.0%)
  • Losers: 8 (40.0%)
  • Top Gainer: NVDA (+4.85%)
  • Top Loser: BA (-4.23%)

✅ Stock generation complete!
```

## Stock Data Structure

Each stock contains the following information:

- `symbol`: Stock ticker symbol (e.g., "AAPL")
- `name`: Company name (e.g., "Apple Inc.")
- `price`: Current stock price
- `change`: Price change in dollars
- `change_percent`: Price change as a percentage
- `volume`: Trading volume
- `market_cap`: Market capitalization (formatted)
- `sector`: Industry sector
- `timestamp`: Generation timestamp

## Included Stock Symbols

The generator includes 20 major stocks across various sectors:

- Technology: AAPL, MSFT, GOOGL, META, NVDA, AMD, INTC, CRM
- Financial Services: JPM, V, GS, PYPL
- Consumer: AMZN, WMT, NKE, SBUX
- Entertainment: DIS, NFLX
- Automotive: TSLA
- Industrials: BA

## Customization

You can easily customize the stock generator by:

1. Adding more stocks to the `STOCKS_DATA` list in the `StockGenerator` class
2. Adjusting price ranges in the `_generate_price()` method
3. Modifying volatility in the `_generate_change()` method
4. Changing volume ranges in the `_generate_volume()` method

## License

This project is open source and available for educational and testing purposes.

## Contributing

Feel free to submit issues and enhancement requests!
