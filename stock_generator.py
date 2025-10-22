#!/usr/bin/env python3
"""
Stock Data Generator
Generates random stock market data for testing and demonstration purposes.
"""

import random
import datetime
from typing import List, Dict
from dataclasses import dataclass, asdict


@dataclass
class Stock:
    """Represents a stock with its market data."""
    symbol: str
    name: str
    price: float
    change: float
    change_percent: float
    volume: int
    market_cap: str
    sector: str
    timestamp: str

    def __str__(self):
        change_sign = '+' if self.change >= 0 else ''
        return (f"{self.symbol:6} | {self.name:25} | "
                f"${self.price:8.2f} | {change_sign}{self.change:+6.2f} "
                f"({change_sign}{self.change_percent:+5.2f}%) | "
                f"Vol: {self.volume:,}")


class StockGenerator:
    """Generates random stock market data."""

    # Common stock symbols and company names
    STOCKS_DATA = [
        ("AAPL", "Apple Inc.", "Technology"),
        ("MSFT", "Microsoft Corporation", "Technology"),
        ("GOOGL", "Alphabet Inc.", "Technology"),
        ("AMZN", "Amazon.com Inc.", "Consumer Cyclical"),
        ("TSLA", "Tesla Inc.", "Automotive"),
        ("META", "Meta Platforms Inc.", "Technology"),
        ("NVDA", "NVIDIA Corporation", "Technology"),
        ("JPM", "JPMorgan Chase & Co.", "Financial Services"),
        ("V", "Visa Inc.", "Financial Services"),
        ("WMT", "Walmart Inc.", "Consumer Defensive"),
        ("DIS", "The Walt Disney Company", "Entertainment"),
        ("NFLX", "Netflix Inc.", "Entertainment"),
        ("BA", "Boeing Company", "Industrials"),
        ("GS", "Goldman Sachs Group", "Financial Services"),
        ("NKE", "Nike Inc.", "Consumer Cyclical"),
        ("SBUX", "Starbucks Corporation", "Consumer Cyclical"),
        ("AMD", "Advanced Micro Devices", "Technology"),
        ("INTC", "Intel Corporation", "Technology"),
        ("PYPL", "PayPal Holdings Inc.", "Financial Services"),
        ("CRM", "Salesforce Inc.", "Technology"),
    ]

    def __init__(self):
        """Initialize the stock generator."""
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _generate_price(self) -> float:
        """Generate a random stock price between $10 and $500."""
        return round(random.uniform(10.0, 500.0), 2)

    def _generate_change(self, price: float) -> tuple[float, float]:
        """Generate price change and change percentage."""
        change_percent = random.uniform(-5.0, 5.0)
        change = round(price * (change_percent / 100), 2)
        return round(change, 2), round(change_percent, 2)

    def _generate_volume(self) -> int:
        """Generate trading volume."""
        return random.randint(1_000_000, 100_000_000)

    def _format_market_cap(self, price: float, volume: int) -> str:
        """Generate a market cap string."""
        # Rough estimation based on price and volume
        cap = price * volume * random.uniform(10, 100)
        if cap >= 1_000_000_000_000:
            return f"${cap/1_000_000_000_000:.2f}T"
        elif cap >= 1_000_000_000:
            return f"${cap/1_000_000_000:.2f}B"
        else:
            return f"${cap/1_000_000:.2f}M"

    def generate_stock(self, symbol: str, name: str, sector: str) -> Stock:
        """Generate a single stock with random data."""
        price = self._generate_price()
        change, change_percent = self._generate_change(price)
        volume = self._generate_volume()
        market_cap = self._format_market_cap(price, volume)

        return Stock(
            symbol=symbol,
            name=name,
            price=price,
            change=change,
            change_percent=change_percent,
            volume=volume,
            market_cap=market_cap,
            sector=sector,
            timestamp=self.timestamp
        )

    def generate_stocks(self, count: int = None) -> List[Stock]:
        """
        Generate multiple stocks.

        Args:
            count: Number of stocks to generate. If None, generates all available stocks.

        Returns:
            List of Stock objects.
        """
        if count is None:
            stocks_to_generate = self.STOCKS_DATA
        else:
            stocks_to_generate = random.sample(self.STOCKS_DATA, min(count, len(self.STOCKS_DATA)))

        return [self.generate_stock(symbol, name, sector)
                for symbol, name, sector in stocks_to_generate]

    def generate_custom_stock(self, symbol: str, name: str, sector: str = "Unknown") -> Stock:
        """Generate a stock with custom symbol and name."""
        return self.generate_stock(symbol, name, sector)


def print_header():
    """Print table header."""
    print("\n" + "=" * 100)
    print(f"{'SYMBOL':<6} | {'COMPANY NAME':<25} | {'PRICE':>8} | {'CHANGE':>6} | {'VOLUME':>15}")
    print("=" * 100)


def print_stocks(stocks: List[Stock]):
    """Print stocks in a formatted table."""
    print_header()
    for stock in stocks:
        print(stock)
    print("=" * 100)
    print(f"\nGenerated {len(stocks)} stocks at {stocks[0].timestamp if stocks else 'N/A'}\n")


def main():
    """Main function to demonstrate stock generation."""
    print("\n🚀 Stock Data Generator")
    print("=" * 50)

    # Create generator
    generator = StockGenerator()

    # Generate all stocks
    print("\n📊 Generating stock market data...\n")
    stocks = generator.generate_stocks()

    # Sort by symbol
    stocks.sort(key=lambda s: s.symbol)

    # Display stocks
    print_stocks(stocks)

    # Show some statistics
    total_volume = sum(s.volume for s in stocks)
    avg_price = sum(s.price for s in stocks) / len(stocks)
    gainers = [s for s in stocks if s.change > 0]
    losers = [s for s in stocks if s.change < 0]

    print("\n📈 Market Summary:")
    print(f"  • Total Stocks: {len(stocks)}")
    print(f"  • Average Price: ${avg_price:.2f}")
    print(f"  • Total Volume: {total_volume:,}")
    print(f"  • Gainers: {len(gainers)} ({len(gainers)/len(stocks)*100:.1f}%)")
    print(f"  • Losers: {len(losers)} ({len(losers)/len(stocks)*100:.1f}%)")

    if gainers:
        top_gainer = max(gainers, key=lambda s: s.change_percent)
        print(f"  • Top Gainer: {top_gainer.symbol} ({top_gainer.change_percent:+.2f}%)")

    if losers:
        top_loser = min(losers, key=lambda s: s.change_percent)
        print(f"  • Top Loser: {top_loser.symbol} ({top_loser.change_percent:+.2f}%)")

    print("\n✅ Stock generation complete!\n")


if __name__ == "__main__":
    main()
