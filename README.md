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

A comprehensive ML-powered stock picking system that predicts 5-session positive closes using momentum and breakout strategies for Indian markets (BSE).

## 🎯 Features

- **📅 Get Stock Picks**: AI recommendations with confidence scores for any date
- **📊 Backtest**: Test strategy performance with 3 modes:
  - **Continuous Learning**: ONE model that learns from each date (⭐ Recommended)
  - **Full Year**: Test entire year with walk-forward validation
  - **Date Range**: Custom period testing
- **🎓 Train Model**: Build and update ML models
  - Train new models from scratch
  - Incremental updates (add new data to existing model)
  - Automatic learning (model learns from predictions automatically)
- **📈 Performance**: Analyze historical results with charts and metrics

## 🧠 Automatic Continuous Learning

The model learns automatically from your predictions - **no manual intervention needed!**

```
Day 1: Get picks → System logs predictions
Day 7: System checks outcomes → Adds to training → Retrains model
Result: Model gets smarter automatically! ✨
```

**Setup once**: Enable auto-learning
**Use normally**: Just get picks daily
**Model learns**: Automatically from every prediction

## 🚀 Quick Start

### Using the Web App (Deployed on Hugging Face)

Just open the app and interact with the 4 tabs:

1. **📅 Get Picks**: Select date → Get recommendations
2. **📊 Backtest**: Choose mode → Run analysis
3. **🎓 Train Model**: Train or update models
4. **📈 Performance**: View historical results

### Usage Tips

- **Past dates** (7+ days ago): Shows actual outcomes
- **Recent dates** (2-7 days): May show partial outcomes
- **Today/Future**: Predictions only (outcomes not available yet)

### Model Training Options

- **200 stocks**: Fast (5-10 min) - good for testing
- **500 stocks**: Medium (10-15 min) - balanced
- **1000 stocks**: Better (15-20 min) - more comprehensive
- **ALL stocks**: Best (20-30 min) - full 4000+ BSE stocks

## 📊 How It Works

The system:
- Fetches BSE data (5600+ stocks)
- Computes 29 technical features (EMA, RSI, ADX, Breakouts, Volume, Momentum)
- Trains LightGBM ML model
- Predicts 5-session positive closes
- Learns automatically from prediction outcomes

## 🔧 Technology Stack

- **Streamlit**: Web interface
- **LightGBM**: Machine learning
- **Pandas/NumPy**: Data processing
- **BSE Data**: Indian stock market (5600+ stocks)
- **Python 3.10+**: Modern Python features

## 📱 Mobile Optimized

Works great on phones and tablets!

**Add to home screen:**
- **iOS**: Safari → Share → "Add to Home Screen"
- **Android**: Chrome → Menu → "Add to Home screen"

## 🎓 Key Concepts

### Continuous Learning (⭐ Recommended)
- ONE model that learns from each date
- Gets progressively smarter over time
- Shows learning curve and improvement
- Simulates real-world deployment

### Walk-Forward Backtest
- Separate model for each date
- No lookahead bias
- Academic validation
- Proves strategy works

### Automatic Learning
- Integrated into daily workflow
- Logs predictions automatically
- Model updates itself
- Zero manual work needed

## 📚 Documentation

- `WEBAPP_FEATURES.md`: Complete feature guide
- `CONTINUOUS_LEARNING_EXPLAINED.md`: Walk-forward vs continuous learning
- `AUTO_LEARNING_GUIDE.md`: Automatic learning setup
- `DEPLOY_HUGGINGFACE.md`: Deployment instructions

## ⚠️ Disclaimer

**FOR EDUCATIONAL PURPOSES ONLY**

This tool is for education and research. Past performance does not guarantee future results. Always do your own research before investing.

## 🔑 Local Commands (Optional)

If running locally:

```bash
# Web app
streamlit run app.py

# Enable auto-learning
python auto_learning.py enable

# View learning stats
python auto_learning.py stats

# Continuous learning backtest
python continuous_learning_backtest.py 2024

# Year-wise backtest
python yearwise_backtest.py 2024 weekly
```

---

Built with ❤️ using Streamlit, LightGBM, and continuous learning

**Access from anywhere - Desktop, Mobile, Tablet!**
