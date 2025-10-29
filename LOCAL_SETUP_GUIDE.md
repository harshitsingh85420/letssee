# 🚀 Local Setup Guide - 5-Session Stock Picker

**Stop fighting with Google Colab!** This guide will help you run the system locally on your computer for better reliability, performance, and control.

---

## 📋 Why Run Locally?

| Feature | Google Colab | Local Setup |
|---------|--------------|-------------|
| **Session timeouts** | ❌ 12 hours max | ✅ No limits |
| **Dependency conflicts** | ❌ Common | ✅ Full control |
| **Speed** | ⚠️ Network dependent | ✅ Fast |
| **Debugging** | ⚠️ Basic | ✅ Full IDE |
| **Automation** | ❌ Complex | ✅ Easy (cron/Task Scheduler) |
| **Cost** | Free | Free |
| **Reliability** | ⚠️ Session management | ✅ Stable |

---

## 🖥️ System Requirements

**Minimum:**
- Python 3.9+
- 4GB RAM
- 5GB disk space
- Internet connection

**Recommended:**
- Python 3.10+
- 8GB RAM
- 10GB disk space
- Stable internet

**No GPU needed!** This system uses LightGBM which is CPU-efficient.

---

## ⚡ Quick Start (5 minutes)

### **Option A: Windows**

```bash
# 1. Install Python (if not installed)
# Download from: https://www.python.org/downloads/
# ✅ Check "Add Python to PATH" during installation

# 2. Clone repository
git clone https://github.com/harshitsingh85420/letssee.git
cd letssee

# 3. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the system
python run_stock_picker.py --mode predict
```

### **Option B: Linux/Mac**

```bash
# 1. Check Python version (should be 3.9+)
python3 --version

# 2. Clone repository
git clone https://github.com/harshitsingh85420/letssee.git
cd letssee

# 3. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the system
python run_stock_picker.py --mode predict
```

---

## 📦 Detailed Installation

### **Step 1: Install Python**

**Windows:**
1. Download Python 3.10+ from https://www.python.org/downloads/
2. Run installer
3. ✅ **IMPORTANT:** Check "Add Python to PATH"
4. Verify: Open CMD and run `python --version`

**Mac:**
```bash
# Using Homebrew
brew install python@3.10
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip
```

### **Step 2: Clone Repository**

```bash
git clone https://github.com/harshitsingh85420/letssee.git
cd letssee
git checkout claude/indian-equity-trading-system-011CUX7MGPY37GwYWmG29cb6
```

### **Step 3: Create Virtual Environment**

Why? Isolates dependencies, prevents conflicts.

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### **Step 4: Install Dependencies**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install:
- pandas, numpy (data processing)
- yfinance (stock data)
- lightgbm (machine learning)
- scikit-learn (ML utilities)
- And more...

**Expected time:** 2-5 minutes

### **Step 5: Verify Installation**

```bash
python -c "import pandas, numpy, lightgbm, yfinance; print('✅ All imports successful!')"
```

---

## 🎯 Using the System

### **Option 1: Run Python Script (Coming Soon)**

```bash
# Train new model
python run_stock_picker.py --mode train --stocks 100

# Generate daily picks
python run_stock_picker.py --mode predict

# Both
python run_stock_picker.py --mode both --stocks 200
```

### **Option 2: Use Jupyter Locally**

**Install Jupyter:**
```bash
pip install jupyter
```

**Start Jupyter:**
```bash
jupyter notebook
```

**Open the notebook:**
- Navigate to `5Session_Stock_Picker_Production.ipynb`
- Run cells in order
- Much faster than Colab!

### **Option 3: Use VS Code (Recommended for Developers)**

1. Install VS Code: https://code.visualstudio.com/
2. Install Python extension
3. Open project folder
4. Open `.ipynb` file
5. Select Python interpreter from venv
6. Run cells interactively

**VS Code Benefits:**
- ✅ Best debugging experience
- ✅ Intellisense/autocomplete
- ✅ Git integration
- ✅ Terminal built-in
- ✅ Can run both notebooks and scripts

---

## 🤖 Automate Daily Runs

Once you have it working, automate daily stock picks!

### **Windows Task Scheduler**

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily at 9:00 AM
4. Action: Start a program
   - Program: `C:\path\to\letssee\venv\Scripts\python.exe`
   - Arguments: `run_stock_picker.py --mode predict`
   - Start in: `C:\path\to\letssee`

### **Linux/Mac Cron**

```bash
# Edit crontab
crontab -e

# Add line (runs daily at 9 AM)
0 9 * * * cd /path/to/letssee && ./venv/bin/python run_stock_picker.py --mode predict >> logs/picker.log 2>&1
```

### **Advanced: Email Results**

Add to script to email picks:
```python
import smtplib
from email.mime.text import MIMEText

# Send email with picks
# (Implementation can be added)
```

---

## 🐛 Troubleshooting

### **"Python not found"**
- ✅ Add Python to PATH
- Windows: System Properties → Environment Variables → Path
- Add: `C:\Python310\` and `C:\Python310\Scripts\`

### **"ModuleNotFoundError"**
- ✅ Activate virtual environment first!
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`
- Then install: `pip install -r requirements.txt`

### **"Permission denied"**
- Linux/Mac: Use `python3` instead of `python`
- Or: `chmod +x run_stock_picker.py`

### **TA-Lib installation fails**
- TA-Lib is optional
- System works without it (uses pandas-ta fallback)
- If you want it:
  - **Linux:** `sudo apt-get install ta-lib`
  - **Mac:** `brew install ta-lib`
  - **Windows:** Download wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib

### **LightGBM errors**
- Update: `pip install --upgrade lightgbm`
- Mac M1/M2: May need to install via conda

### **Slow data downloads**
- Normal for first run (downloads 2 years of data)
- Cached for subsequent runs
- Use `n_stocks_for_training=50` to start small

---

## 📁 Project Structure

```
letssee/
├── indian_trading_system/          # Core modules
│   ├── indicators/                 # Technical indicators
│   │   ├── technical.py           # 30+ indicators
│   │   ├── volatility.py          # Advanced volatility
│   │   └── patterns.py            # Candlestick patterns
│   ├── models/                    # ML models
│   │   └── features.py            # Feature engineering
│   └── utils/                     # Utilities
├── 5Session_Stock_Picker_Production.ipynb  # Notebook
├── run_stock_picker.py            # Standalone script
├── requirements.txt               # Dependencies
├── LOCAL_SETUP_GUIDE.md          # This file
└── stock_picker_data/             # Created at runtime
    ├── data/                      # Stock data cache
    ├── models/                    # Trained models
    └── results/                   # Daily picks
```

---

## 💡 Development Workflow

### **Recommended: VS Code + Jupyter**

1. **Open project in VS Code**
2. **Install extensions:**
   - Python
   - Jupyter
   - Pylance (better autocomplete)

3. **Select interpreter:**
   - Ctrl+Shift+P → "Python: Select Interpreter"
   - Choose `./venv/bin/python`

4. **Run notebook interactively:**
   - Open `.ipynb` file
   - Click "Run Cell" to execute
   - Much faster than Colab!

5. **Debug code:**
   - Set breakpoints
   - Step through code
   - Inspect variables
   - Better than print debugging!

### **Testing Changes**

```bash
# Activate environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run with small dataset for testing
python -c "
from run_stock_picker import *
# Test code here
"

# Or use IPython for interactive testing
pip install ipython
ipython
```

### **Git Workflow**

```bash
# Make changes
git add .
git commit -m "Your changes"

# Pull latest
git pull origin claude/indian-equity-trading-system-011CUX7MGPY37GwYWmG29cb6

# Push changes
git push origin claude/indian-equity-trading-system-011CUX7MGPY37GwYWmG29cb6
```

---

## 🌟 Benefits of Local Setup

### **1. Better Performance**
- No network latency
- Direct file access
- Faster iterations
- Can use all CPU cores

### **2. Professional Tools**
- VS Code / PyCharm
- Git integration
- Debugger
- Code navigation
- Refactoring tools

### **3. Automation**
- Cron jobs / Task Scheduler
- Email notifications
- Log files
- Background processing

### **4. Reliability**
- No session timeouts
- No kernel restarts
- Stable environment
- Predictable behavior

### **5. Privacy**
- Data stays local
- No cloud uploads
- Full control

---

## 🎓 Next Steps

1. **✅ Complete setup** following this guide
2. **🧪 Test with small dataset** (10-50 stocks)
3. **🎯 Train model** with more stocks (100-500)
4. **📊 Generate predictions** and analyze results
5. **🤖 Automate** daily runs
6. **📈 Track performance** over time
7. **🔧 Customize** strategy parameters

---

## 🆚 Comparison with Cloud Options

### **Kaggle Notebooks**
- **Pros:** Similar to Colab, 30 hours/week GPU (but we don't need GPU)
- **Cons:** Still cloud-based, session management, timeouts
- **Verdict:** ⚠️ Better than Colab but local is still better

### **GitHub Codespaces**
- **Pros:** Cloud VS Code, good for development
- **Cons:** 60 hours/month free, then paid
- **Verdict:** ⚠️ Good for occasional use, not daily automation

### **AWS/GCP/Azure VM**
- **Pros:** Always on, can schedule runs
- **Cons:** Costs money ($10-50/month), complex setup
- **Verdict:** 💰 Overkill unless you need 24/7 operation

### **Docker**
- **Pros:** Portable, reproducible
- **Cons:** More complex, unnecessary for this project
- **Verdict:** ⚠️ Optional for advanced users

---

## 📞 Support

**Issues?**
1. Check Troubleshooting section above
2. Verify all dependencies installed: `pip list`
3. Check Python version: `python --version`
4. Try fresh virtual environment

**Still stuck?**
- Share error message
- Mention your OS and Python version
- I'll help debug!

---

## ✅ Checklist

Before running the system:

- [ ] Python 3.9+ installed
- [ ] Git installed
- [ ] Repository cloned
- [ ] Virtual environment created
- [ ] Virtual environment activated (see `(venv)` in prompt)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Test import successful
- [ ] Ready to run!

---

**🎉 Welcome to professional Python development!**

No more fighting with Colab. You now have:
- Full control over your environment
- Professional development tools
- Ability to automate and schedule
- Better debugging and iteration speed
- A setup that scales to production

Happy trading! 📈
