# 🔧 Installation Troubleshooting Guide

Common installation issues and solutions for Windows, Mac, and Linux.

---

## 🚨 Common Errors

### ❌ Error: "Could not find a version that satisfies the requirement pandas_ta"

**Problem:** Old requirements.txt had pandas_ta which is no longer needed

**Solution:** Update your code and use the new requirements.txt:

```bash
# Pull latest code
git pull origin claude/indian-equity-trading-system-011CUX7MGPY37GwYWmG29cb6

# Install (pandas_ta is removed)
pip install -r requirements.txt
```

**Or install directly:**
```bash
pip install numpy pandas yfinance lightgbm scikit-learn requests beautifulsoup4 tqdm joblib imbalanced-learn python-dateutil pytz numba plotly
```

**Note:** pandas_ta is NOT needed - system has built-in fallbacks for all technical indicators

---

### ❌ Error: "Microsoft Visual C++ 14.0 or greater is required"

**Problem:** Windows needs C++ build tools for some packages (numba, etc.)

**Solution:**

**Option 1 - Install Visual C++ Build Tools (Recommended):**
1. Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Run installer
3. Select "Desktop development with C++"
4. Install (takes ~10 minutes)
5. Restart terminal
6. Try `pip install -r requirements.txt` again

**Option 2 - Use pre-built wheels:**
```bash
pip install --only-binary :all: -r requirements.txt
```

**Option 3 - Skip problematic packages:**
```bash
# Install without numba (slower but works)
pip install numpy pandas yfinance lightgbm scikit-learn requests beautifulsoup4 tqdm joblib
```

---

### ❌ Error: "ERROR: Failed building wheel for numba"

**Problem:** Numba compilation issues

**Solutions:**

**Option 1 - Use compatible numba version:**
```bash
pip install numba==0.57.1
```

**Option 2 - Skip numba (system still works, just slower):**
```bash
pip install -r requirements-minimal.txt
# Skip numba - indicators will be slightly slower but functional
```

**Option 3 - Use conda (if you have Anaconda):**
```bash
conda install numba
pip install -r requirements-minimal.txt
```

---

### ❌ Error: "Python was not found"

**Problem:** Python not in PATH

**Windows Solution:**
1. Reinstall Python from https://www.python.org/downloads/
2. ✅ **CHECK "Add Python to PATH"** during installation
3. Or manually add to PATH:
   - Search "Environment Variables"
   - Edit PATH
   - Add: `C:\Users\YOUR_USERNAME\AppData\Local\Programs\Python\Python310\`
   - Add: `C:\Users\YOUR_USERNAME\AppData\Local\Programs\Python\Python310\Scripts\`
4. Restart terminal

**Mac/Linux Solution:**
```bash
# Check Python location
which python3

# Add to PATH in ~/.bashrc or ~/.zshrc
export PATH="/usr/local/bin/python3:$PATH"
source ~/.bashrc
```

---

### ❌ Error: "No module named 'venv'"

**Problem:** venv module not installed

**Solution:**

**Ubuntu/Debian:**
```bash
sudo apt-get install python3-venv
```

**CentOS/RHEL:**
```bash
sudo yum install python3-venv
```

**Mac:**
```bash
# Usually included, but if not:
brew install python@3.10
```

---

### ❌ Error: "Permission denied" (Mac/Linux)

**Problem:** Permissions issue

**Solution:**
```bash
# DON'T use sudo pip install!
# Instead, use virtual environment:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

### ❌ Error: "SSL Certificate verification failed"

**Problem:** Corporate firewall or network issues

**Solution:**

**Option 1 - Upgrade pip/certificates:**
```bash
pip install --upgrade pip certifi
pip install -r requirements.txt
```

**Option 2 - Use HTTP (not recommended, only for testing):**
```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

**Option 3 - Set corporate proxy:**
```bash
set HTTP_PROXY=http://proxy.company.com:8080
set HTTPS_PROXY=http://proxy.company.com:8080
pip install -r requirements.txt
```

---

## 🎯 Step-by-Step Verified Installation

### Windows 10/11 (Python 3.10)

```bash
# 1. Download and install Python 3.10 from python.org
#    ✅ Check "Add Python to PATH"

# 2. Verify installation
python --version
# Should show: Python 3.10.x

# 3. Clone repository
git clone https://github.com/harshitsingh85420/letssee.git
cd letssee

# 4. Create virtual environment
python -m venv venv

# 5. Activate virtual environment
venv\Scripts\activate
# You should see (venv) in prompt

# 6. Upgrade pip
python -m pip install --upgrade pip

# 7. Install dependencies (try full requirements first)
pip install -r requirements.txt

# If that fails, use minimal:
pip install -r requirements-minimal.txt

# 8. Verify installation
python -c "import pandas, numpy, lightgbm, yfinance; print('✅ Success!')"
```

### Mac (Python 3.10)

```bash
# 1. Install Python via Homebrew
brew install python@3.10

# 2. Clone repository
git clone https://github.com/harshitsingh85420/letssee.git
cd letssee

# 3. Create virtual environment
python3 -m venv venv

# 4. Activate
source venv/bin/activate

# 5. Install
pip install --upgrade pip
pip install -r requirements.txt

# 6. Verify
python -c "import pandas, numpy, lightgbm, yfinance; print('✅ Success!')"
```

### Ubuntu/Debian Linux

```bash
# 1. Install Python and venv
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip git

# 2. Clone repository
git clone https://github.com/harshitsingh85420/letssee.git
cd letssee

# 3. Create virtual environment
python3 -m venv venv

# 4. Activate
source venv/bin/activate

# 5. Install
pip install --upgrade pip
pip install -r requirements.txt

# 6. Verify
python -c "import pandas, numpy, lightgbm, yfinance; print('✅ Success!')"
```

---

## 🧪 Testing Your Installation

After installation, test that everything works:

```bash
# Activate virtual environment first
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# Test imports
python << EOF
import pandas as pd
import numpy as np
import yfinance as yf
import lightgbm as lgb
from sklearn.model_selection import train_test_split

print("✅ All core imports successful!")
print(f"Pandas: {pd.__version__}")
print(f"NumPy: {np.__version__}")
print(f"LightGBM: {lgb.__version__}")
print(f"yfinance: {yf.__version__}")
EOF

# Test yfinance download
python -c "import yfinance as yf; print(yf.Ticker('RELIANCE.NS').history(period='5d'))"

# If this works, you're ready!
```

---

## 🔄 Alternative Installation Methods

### Method 1: Anaconda/Miniconda (Easiest)

```bash
# Install Anaconda from https://www.anaconda.com/download
# Then:

conda create -n trading python=3.10
conda activate trading

# Install using conda where possible
conda install numpy pandas scikit-learn jupyter

# Install rest with pip
pip install yfinance lightgbm pandas-ta requests beautifulsoup4 tqdm
```

### Method 2: Poetry (For Developers)

```bash
pip install poetry
poetry install
poetry shell
```

### Method 3: Docker (Advanced)

```dockerfile
# Use official Python image
FROM python:3.10-slim

WORKDIR /app
COPY requirements-minimal.txt .
RUN pip install -r requirements-minimal.txt

COPY . .
CMD ["python", "run_stock_picker.py"]
```

---

## 📋 Version Compatibility Matrix

| Python | NumPy | Pandas | LightGBM | Status |
|--------|-------|--------|----------|--------|
| 3.9 | 1.26.4 | 2.2.2 | 4.0+ | ✅ Tested |
| 3.10 | 1.26.4 | 2.2.2 | 4.0+ | ✅ Recommended |
| 3.11 | 1.26.4 | 2.2.2 | 4.0+ | ✅ Works |
| 3.12 | 1.26.4+ | 2.2.2+ | 4.0+ | ⚠️ Some packages not ready |

---

## 🆘 Still Having Issues?

If you're still stuck after trying the above:

### 1. **Collect Information:**
```bash
# Run this and share the output:
python --version
pip --version
pip list
```

### 2. **Try Absolute Minimal Install:**
```bash
pip install numpy pandas yfinance lightgbm scikit-learn
# This should always work
```

### 3. **Check Specific Errors:**
- Share full error message
- Mention your OS (Windows/Mac/Linux) and version
- Python version
- Any corporate firewall/proxy?

### 4. **Quick Workarounds:**

**Skip pandas-ta:**
```bash
# System works without it (uses pandas fallbacks)
pip install -r requirements-minimal.txt
```

**Skip numba:**
```bash
# Slightly slower but functional
pip install numpy pandas yfinance lightgbm scikit-learn requests beautifulsoup4 tqdm joblib
```

**Skip visualization:**
```bash
# Can still run trading system
pip install numpy pandas yfinance lightgbm scikit-learn requests beautifulsoup4 tqdm joblib
```

---

## ✅ Success Checklist

Before running the trading system, verify:

- [ ] Python 3.9+ installed and in PATH
- [ ] Virtual environment created and activated (`(venv)` in prompt)
- [ ] Core packages installed (numpy, pandas, yfinance, lightgbm)
- [ ] Test import successful: `python -c "import pandas, numpy, lightgbm"`
- [ ] yfinance can download data: `python -c "import yfinance; print('OK')"`
- [ ] Repository cloned with all files present
- [ ] Ready to run!

---

## 🚀 Next Steps

Once installation is successful:

1. **Test the system:**
   ```bash
   python run_stock_picker.py --mode predict
   ```

2. **Read the docs:**
   - `LOCAL_SETUP_GUIDE.md` - Complete usage guide
   - `NOTEBOOK_ERROR_ANALYSIS.md` - Understanding the code

3. **Start small:**
   - Test with 10 stocks first
   - Verify everything works
   - Scale up gradually

---

**Remember:** The core system needs only:
- numpy
- pandas
- yfinance
- lightgbm
- scikit-learn

Everything else is optional enhancements!
