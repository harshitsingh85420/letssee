# Deploy to Hugging Face Spaces - Step by Step Guide

Deploy your Stock Picker web app to Hugging Face Spaces for **FREE** and access it from anywhere!

## 🎯 Why Hugging Face Spaces?

✅ **100% Free** - No credit card required
✅ **Always online** - App runs 24/7
✅ **Easy deployment** - Git-based workflow
✅ **Global CDN** - Fast access worldwide
✅ **Custom domain** - Professional URL (optional)
✅ **No sleep mode** - Unlike some free services
✅ **Community friendly** - Great for sharing

---

## 🚀 Quick Deployment (5 Minutes)

### Step 1: Create Hugging Face Account

1. Go to **https://huggingface.co/**
2. Click **"Sign Up"** (top right)
3. Create free account (use GitHub login for faster setup)
4. Verify your email

### Step 2: Create a New Space

1. Go to **https://huggingface.co/spaces**
2. Click **"Create new Space"**
3. Fill in details:
   - **Space name**: `stock-picker-5session` (or your choice)
   - **License**: MIT
   - **Select SDK**: **Streamlit** (IMPORTANT!)
   - **Space hardware**: CPU basic (free tier)
   - **Visibility**: Public or Private (your choice)
4. Click **"Create Space"**

### Step 3: Upload Files via Web Interface

**Option A: Upload Files Directly (Easiest)**

1. In your new Space, click **"Files"** tab
2. Click **"Add file"** → **"Upload files"**
3. Upload these files:
   ```
   app.py
   bse_loader.py
   momentum_features.py
   momentum_features_enhanced.py
   stock_picker_5session.py
   backtest_5session.py
   get_picks.py
   incremental_training.py
   market_regime.py
   stock_picker_enhanced.py
   advanced_features.py
   ```

4. Click **"Add file"** → **"Create new file"**
   - Name: `requirements.txt`
   - Paste contents from `requirements-streamlit.txt`
   - Click **"Commit new file"**

5. Click **"Add file"** → **"Create new file"**
   - Name: `README.md`
   - Paste contents from `README_HUGGINGFACE.md`
   - Click **"Commit new file"**

**Option B: Git Push (For Advanced Users)**

```bash
# Clone your space
git clone https://huggingface.co/spaces/YOUR_USERNAME/stock-picker-5session
cd stock-picker-5session

# Copy necessary files
cp ~/letssee/app.py .
cp ~/letssee/bse_loader.py .
cp ~/letssee/momentum_features.py .
cp ~/letssee/momentum_features_enhanced.py .
cp ~/letssee/stock_picker_5session.py .
cp ~/letssee/backtest_5session.py .
cp ~/letssee/get_picks.py .
cp ~/letssee/incremental_training.py .
cp ~/letssee/market_regime.py .
cp ~/letssee/stock_picker_enhanced.py .
cp ~/letssee/advanced_features.py .
cp ~/letssee/requirements-streamlit.txt requirements.txt
cp ~/letssee/README_HUGGINGFACE.md README.md

# Create .gitignore
cat > .gitignore << EOF
*.pkl
*.pyc
__pycache__/
.DS_Store
*.csv
stock_picker_data/
.streamlit/
EOF

# Commit and push
git add .
git commit -m "Initial deployment"
git push
```

### Step 4: Wait for Build

1. Hugging Face will automatically build your app
2. Watch the **"Logs"** tab for progress
3. Build takes 2-5 minutes
4. Once done, you'll see your app running!

### Step 5: Access Your App

Your app is now live at:
```
https://huggingface.co/spaces/YOUR_USERNAME/stock-picker-5session
```

**Share this URL** with anyone - no login required for public spaces!

---

## 📋 Required Files Checklist

Make sure you have uploaded these files:

### Core Python Files (Required)
- ✅ `app.py` - Main Streamlit app
- ✅ `bse_loader.py` - BSE data fetcher
- ✅ `momentum_features.py` - Feature engineering
- ✅ `stock_picker_5session.py` - Main stock picker
- ✅ `backtest_5session.py` - Backtesting module
- ✅ `get_picks.py` - Get picks for specific dates
- ✅ `incremental_training.py` - Incremental learning

### Optional Python Files (Recommended)
- ⚠️ `momentum_features_enhanced.py` - Enhanced features (optional)
- ⚠️ `market_regime.py` - Market regime detection (optional)
- ⚠️ `stock_picker_enhanced.py` - Enhanced picker (optional)
- ⚠️ `advanced_features.py` - Advanced features (optional)

### Configuration Files (Required)
- ✅ `requirements.txt` - Python dependencies
- ✅ `README.md` - Space description

### Optional Files
- 📄 `WEBAPP_FEATURES.md` - Feature documentation
- 📄 `INCREMENTAL_LEARNING.md` - Learning guide
- 📄 `.gitignore` - Git ignore rules

---

## 🔧 Configuration Files

### `requirements.txt`
Use the contents of `requirements-streamlit.txt`:

```txt
# Core dependencies
pandas>=1.4.0
numpy>=1.21.0
requests>=2.27.0

# Machine Learning
lightgbm>=3.3.0
scikit-learn>=1.0.0

# Web Framework
streamlit>=1.28.0

# Plotting
matplotlib>=3.5.0
plotly>=5.0.0

# Optional
openpyxl>=3.0.0
```

### `README.md` (Optional but Recommended)
Use `README_HUGGINGFACE.md` content with the YAML header at top:

```yaml
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
```

### `.gitignore` (Recommended)
```
*.pkl
*.pyc
__pycache__/
.DS_Store
*.csv
stock_picker_data/
.streamlit/
venv/
*.log
```

---

## 🎨 Customization

### Change Space Name
In README.md YAML header:
```yaml
title: Your Custom Name
```

### Change Emoji
```yaml
emoji: 🚀  # Any emoji you like
```

### Change Colors
```yaml
colorFrom: red
colorTo: yellow
```

### Make Space Private
In Space settings:
- Click **"Settings"** tab
- Change **"Visibility"** to Private
- Click **"Save"**

---

## 🐛 Troubleshooting

### Build Fails

**Check Logs:**
1. Go to **"Logs"** tab in your Space
2. Look for error messages
3. Common issues:

**Missing dependencies:**
```
ERROR: No module named 'lightgbm'
```
**Fix:** Add to `requirements.txt`

**Import errors:**
```
ImportError: cannot import name 'X' from 'Y'
```
**Fix:** Make sure all Python files are uploaded

**Syntax errors:**
```
SyntaxError: invalid syntax
```
**Fix:** Check Python version compatibility

### App Runs But Errors When Using

**Data fetching fails:**
- BSE website might be blocking requests
- Try using cached data or different dates

**Model not found:**
- Train a model first using Tab 3
- Models are stored in Space persistent storage

**Slow performance:**
- First run computes features (10-15 min)
- Subsequent runs use cache (faster)
- Consider upgrading to better hardware tier

### Out of Memory

**Free tier has 16GB RAM limit**

If you hit memory limits:
1. Reduce training stocks (use 200 instead of ALL)
2. Clear cache files (delete `*.pkl` files)
3. Upgrade to better hardware tier (paid)

---

## ⚡ Performance Optimization

### Enable Persistent Storage

Hugging Face Spaces have persistent storage that survives rebuilds:

1. Create `stock_picker_data` directory
2. Cache files will persist between sessions
3. Trained models stay saved

### Speed Up First Load

Add this to your Space Settings → Environment variables:

```
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_PORT=7860
```

### Enable Caching

The app already uses `@st.cache_data` for caching - this works automatically on Hugging Face!

---

## 🔒 Security & Privacy

### For Public Spaces

- ✅ Anyone can view and use your app
- ❌ Don't include API keys or secrets
- ❌ Don't commit sensitive data
- ✅ Use environment variables for secrets

### For Private Spaces

- ✅ Only you can access
- ✅ Share with specific users via Settings
- ✅ Good for personal/team use
- ⚠️ Still visible to Hugging Face staff

### Secrets Management

For sensitive data (API keys, etc.):

1. Go to **Settings** tab
2. Click **"Variables and secrets"**
3. Add secrets
4. Access in code via `os.environ['SECRET_NAME']`

---

## 📊 Usage Limits (Free Tier)

| Resource | Limit |
|----------|-------|
| RAM | 16 GB |
| Storage | 50 GB |
| CPU | 2 cores |
| Timeout | No timeout for Spaces |
| Concurrent Users | Unlimited |
| Always-on | Yes |

**Upgrading:**
- Need more? Upgrade to paid hardware tier
- As low as $0.60/hour for better specs
- Only pay when running

---

## 🌐 Custom Domain (Optional)

Want `stockpicker.yourdomain.com` instead of the Hugging Face URL?

1. Upgrade to paid hardware tier
2. Go to Settings → Custom domain
3. Add your domain
4. Update DNS records
5. Done!

---

## 🔄 Updating Your App

### Via Web Interface

1. Go to **Files** tab
2. Click on file to edit
3. Click **"Edit"** button
4. Make changes
5. Click **"Commit changes"**
6. App auto-rebuilds!

### Via Git

```bash
# Make local changes
git add .
git commit -m "Update XYZ"
git push

# Space rebuilds automatically
```

---

## 📱 Mobile Access

Your app is mobile-optimized! Users can:

1. Open the Hugging Face URL on phone
2. Use all features (tabs, buttons, tables)
3. Add to home screen for app-like experience

### iOS:
Safari → Share → Add to Home Screen

### Android:
Chrome → Menu → Add to Home screen

---

## 🎓 Next Steps After Deployment

### 1. Train Initial Model
```
Tab 3 → Train New Model → ALL stocks → Train
Wait 15-20 min
```

### 2. Test with Recent Date
```
Tab 1 → Select date 1 week ago → Get Picks
```

### 3. Run Backtest
```
Tab 2 → Select date range → Weekly → Run Backtest
```

### 4. Share Your Space
```
Share URL: https://huggingface.co/spaces/YOUR_USERNAME/stock-picker-5session
```

---

## 💡 Tips & Best Practices

### For Better Performance

1. **Use 200 stocks initially** - faster training/picks
2. **Clear cache periodically** - delete old `*.pkl` files
3. **Update model weekly** - keep it fresh
4. **Monitor logs** - watch for errors

### For Production Use

1. **Test thoroughly first** - try all features
2. **Document your workflow** - add instructions
3. **Monitor usage** - check logs regularly
4. **Backup models** - download trained models
5. **Update dependencies** - keep packages current

### For Sharing

1. **Make README clear** - explain what it does
2. **Add screenshots** - show features
3. **Provide examples** - show how to use
4. **Respond to issues** - help users
5. **Keep it updated** - fix bugs

---

## 🆘 Getting Help

### Hugging Face Community

- **Forum**: https://discuss.huggingface.co/
- **Discord**: https://discord.gg/huggingface
- **Docs**: https://huggingface.co/docs/hub/spaces

### Your Space Issues

1. Check **Logs** tab for errors
2. Review **Settings** for configuration
3. Try **Rebuild Space** button
4. Ask in Hugging Face forum

---

## 🎉 You're Done!

Your Stock Picker is now deployed and accessible worldwide!

**Your app URL:**
```
https://huggingface.co/spaces/YOUR_USERNAME/stock-picker-5session
```

**Features available:**
- ✅ Get stock picks from any device
- ✅ Run backtests online
- ✅ Train models in the cloud
- ✅ Analyze performance
- ✅ Share with others
- ✅ Access from mobile

**Enjoy your cloud-based stock picking system!** 📈🌍🚀

---

## 📚 Additional Resources

- Hugging Face Spaces Guide: https://huggingface.co/docs/hub/spaces
- Streamlit Documentation: https://docs.streamlit.io/
- Your app features: See `WEBAPP_FEATURES.md`
- Incremental learning: See `INCREMENTAL_LEARNING.md`

---

**Need help?** Check the Hugging Face documentation or ask in their community forum!
