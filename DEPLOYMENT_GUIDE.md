# Stock Picker Web App - Deployment Guide

Your stock picker is now a web application! Access it from any device - mobile, tablet, or desktop.

## 🚀 Quick Start (Run Locally)

### 1. Install Streamlit Dependencies

```bash
pip install -r requirements-streamlit.txt
```

### 2. Run the App

```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`

### 3. Access from Mobile (Same WiFi Network)

When you run the app, Streamlit shows a "Network URL" like:
```
Network URL: http://192.168.1.100:8501
```

**On your phone/tablet (connected to same WiFi):**
- Open browser
- Type in the Network URL
- Bookmark it for easy access!

---

## ☁️ Deploy Online (FREE) - Access from Anywhere!

Deploy to **Streamlit Cloud** so you can access your app from anywhere in the world, even when your computer is off!

### Option 1: Streamlit Cloud (Recommended - FREE)

#### Step 1: Push Code to GitHub

```bash
# Commit the new files
git add app.py requirements-streamlit.txt DEPLOYMENT_GUIDE.md
git commit -m "Add Streamlit web app for stock picker"
git push origin main
```

#### Step 2: Deploy to Streamlit Cloud

1. Go to **https://share.streamlit.io**
2. Sign in with GitHub
3. Click **"New app"**
4. Select:
   - **Repository**: `harshitsingh85420/letssee`
   - **Branch**: `main` (or your branch)
   - **Main file**: `app.py`
5. Click **"Advanced settings"**
   - **Python version**: 3.10
   - **Requirements file**: `requirements-streamlit.txt`
6. Click **"Deploy"**

**Your app will be live at:**
```
https://your-app-name.streamlit.app
```

Access from anywhere - phone, laptop, tablet!

---

### Option 2: Heroku (Alternative)

If you prefer Heroku, follow these steps:

#### 1. Create Required Files

**Procfile:**
```bash
echo "web: streamlit run app.py --server.port=\$PORT" > Procfile
```

**runtime.txt:**
```bash
echo "python-3.10.13" > runtime.txt
```

#### 2. Deploy to Heroku

```bash
# Install Heroku CLI first: https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Create app
heroku create your-stock-picker

# Push code
git push heroku main

# Open app
heroku open
```

---

### Option 3: Run on Your Own Server

If you have a VPS or cloud server:

```bash
# Install dependencies
pip install -r requirements-streamlit.txt

# Run with nohup (keeps running after logout)
nohup streamlit run app.py --server.port 8501 &

# Or use screen/tmux
screen -S stockpicker
streamlit run app.py
# Press Ctrl+A then D to detach
```

Configure your firewall to allow port 8501, and access via:
```
http://your-server-ip:8501
```

---

## 📱 Mobile App Experience

While this is a web app, you can make it feel like a native mobile app:

### iOS (iPhone/iPad)

1. Open the app URL in Safari
2. Tap the **Share** button (square with arrow)
3. Tap **"Add to Home Screen"**
4. Name it "Stock Picker"
5. Tap **"Add"**

Now you have an app icon on your home screen!

### Android

1. Open the app URL in Chrome
2. Tap the **menu** (three dots)
3. Tap **"Add to Home screen"**
4. Name it "Stock Picker"
5. Tap **"Add"**

---

## 🎯 Features of Your Web App

✅ **Mobile-Friendly Design** - Works perfectly on phones
✅ **Date Picker** - Select any date to get picks
✅ **Live Results** - See picks with confidence scores
✅ **Actual Outcomes** - View how past picks performed
✅ **Performance Metrics** - Win rate, avg return, best/worst picks
✅ **CSV Export** - Download results for analysis
✅ **Visual Charts** - Outcome distribution charts
✅ **Responsive Tables** - Swipe to see all columns

---

## 💡 Usage Tips

### For Best Results:

1. **Past Dates (7+ days ago)**: Shows actual outcomes - great for backtesting
2. **Recent Dates (2-7 days ago)**: May show partial outcomes
3. **Today/Future**: Shows predictions only (no outcomes yet)

### Training Stocks Setting:

- **200 stocks**: Fast, good for quick checks (1-2 minutes)
- **500 stocks**: Better model, slower (5-10 minutes)
- **1000 stocks**: Even better, slower (10-15 minutes)
- **ALL stocks**: Best model, slowest (15-20 minutes)

### Mobile Performance:

- First run on a date will be slower (computing features)
- Subsequent runs for same date range are MUCH faster (cached)
- Consider using 200 stocks on mobile for speed

---

## 🔧 Troubleshooting

### App is Slow

- First run computes features (10-15 min), then caches
- Use fewer training stocks (200 instead of ALL)
- Check your internet connection
- Clear cache: Delete `features_*.pkl` files

### "No picks found"

- Try a different date
- Ensure date has at least 200 days of prior data
- Check if market was open on that date

### Can't Access from Phone (Local)

- Ensure phone and computer are on same WiFi
- Check firewall isn't blocking port 8501
- Try the external URL shown by Streamlit

### Deployment Errors

**Streamlit Cloud:**
- Check `requirements-streamlit.txt` is committed
- Verify Python version is 3.10 in settings
- Check logs for specific error messages

**Heroku:**
- Ensure `Procfile` and `runtime.txt` exist
- Check logs: `heroku logs --tail`

---

## 🔐 Security Notes

### For Public Deployment:

If deploying publicly, consider:

1. **Add authentication** (Streamlit supports this)
2. **Rate limiting** to prevent abuse
3. **Don't commit sensitive data** (.env files, credentials)
4. **Monitor usage** to avoid exceeding free tier limits

### Private Deployment:

- Use Streamlit Cloud's privacy settings
- Deploy to private server with authentication
- Use VPN for access control

---

## 📊 Free Tier Limits

### Streamlit Cloud (FREE):
- ✅ Unlimited public apps
- ✅ 1 GB RAM per app
- ✅ 1 CPU core
- ✅ Custom domains
- ❌ Sleeps after inactivity (wakes on access)

**Perfect for personal use!**

### Upgrade Options:
- **Streamlit Teams**: More resources, always-on
- **Your own server**: Full control, no limits

---

## 🎉 Next Steps

1. **Test locally** first to make sure everything works
2. **Deploy to Streamlit Cloud** for free online access
3. **Add to phone home screen** for app-like experience
4. **Share the URL** with trusted users (if desired)

## 📞 Support

If you encounter issues:
- Check logs in Streamlit Cloud dashboard
- Review this guide's troubleshooting section
- Check that all files are committed to GitHub

---

**Enjoy your web-based Stock Picker! 📈📱**
