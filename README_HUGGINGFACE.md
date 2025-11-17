---
title: Stock Picker 5-Session
emoji: 📈
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: "1.28.0"
app_file: app.py
pinned: false
license: mit
---

# 📈 Stock Picker - 5 Session Prediction System

A comprehensive ML-powered stock picking system that predicts 5-session positive closes using momentum and breakout strategies.

## 🎯 Features

- **Get Stock Picks**: Select any date and get AI recommendations
- **Backtest**: Test strategy performance over date ranges
- **Train Model**: Build and update ML models with latest data
- **Performance Dashboard**: Analyze historical results

## 🚀 Quick Start

This app runs automatically on Hugging Face Spaces. Just interact with the tabs!

### Tabs:

1. **📅 Get Picks**: Get stock recommendations for specific dates
2. **📊 Backtest**: Run backtests over date ranges
3. **🎓 Train Model**: Train or update ML models
4. **📈 Performance**: View historical performance metrics

## 📊 How It Works

The system uses:
- **LightGBM ML model** for predictions
- **29 technical features** (EMA, RSI, ADX, Breakouts, etc.)
- **Momentum & breakout signals** from Indian stock market (BSE)
- **5-session forward prediction** for positive closes

## 💡 Tips

- Past dates show actual outcomes
- First run on new date computes features (may take time)
- Subsequent runs are cached and fast
- Update model weekly/monthly for best results

## 🔧 Technology Stack

- **Streamlit**: Web interface
- **LightGBM**: Machine learning
- **Pandas**: Data processing
- **BSE Data**: Indian stock market data

## 📱 Mobile Optimized

Works great on phones and tablets! Add to home screen for app-like experience.

## ⚠️ Disclaimer

This tool is for educational purposes only. Past performance does not guarantee future results. Always do your own research before investing.

## 📚 Learn More

Check the documentation files:
- `WEBAPP_FEATURES.md`: Complete feature guide
- `INCREMENTAL_LEARNING.md`: How the model learns continuously
- `DEPLOYMENT_GUIDE.md`: Deployment instructions

---

Built with ❤️ using Streamlit and LightGBM
