@echo off
REM Helper script to prepare files for Hugging Face Spaces deployment (Windows)

echo ======================================
echo Preparing files for Hugging Face
echo ======================================
echo.

REM Create deployment directory
set DEPLOY_DIR=hf_deployment
if not exist %DEPLOY_DIR% mkdir %DEPLOY_DIR%

echo Copying core files...
echo.

REM Copy Python files
copy app.py %DEPLOY_DIR%\ >nul 2>&1
copy bse_loader.py %DEPLOY_DIR%\ >nul 2>&1
copy momentum_features.py %DEPLOY_DIR%\ >nul 2>&1
copy stock_picker_5session.py %DEPLOY_DIR%\ >nul 2>&1
copy backtest_5session.py %DEPLOY_DIR%\ >nul 2>&1
copy get_picks.py %DEPLOY_DIR%\ >nul 2>&1
copy incremental_training.py %DEPLOY_DIR%\ >nul 2>&1

REM Copy optional files
copy momentum_features_enhanced.py %DEPLOY_DIR%\ >nul 2>&1
copy market_regime.py %DEPLOY_DIR%\ >nul 2>&1
copy stock_picker_enhanced.py %DEPLOY_DIR%\ >nul 2>&1
copy advanced_features.py %DEPLOY_DIR%\ >nul 2>&1

echo Creating configuration files...
echo.

REM Create requirements.txt
copy requirements-streamlit.txt %DEPLOY_DIR%\requirements.txt >nul 2>&1

REM Create README.md
copy README_HUGGINGFACE.md %DEPLOY_DIR%\README.md >nul 2>&1

REM Create .gitignore
(
echo # Python
echo *.pyc
echo __pycache__/
echo *.py[cod]
echo.
echo # Cache files
echo *.pkl
echo *.cache
echo.
echo # Data files
echo *.csv
echo stock_picker_data/
echo.
echo # Environment
echo venv/
echo env/
echo .env
echo.
echo # OS
echo .DS_Store
echo Thumbs.db
echo.
echo # Logs
echo *.log
echo.
echo # Streamlit
echo .streamlit/
) > %DEPLOY_DIR%\.gitignore

echo Copying documentation...
echo.

copy WEBAPP_FEATURES.md %DEPLOY_DIR%\ >nul 2>&1
copy INCREMENTAL_LEARNING.md %DEPLOY_DIR%\ >nul 2>&1
copy DEPLOYMENT_GUIDE.md %DEPLOY_DIR%\ >nul 2>&1

echo.
echo ======================================
echo Files prepared in: %DEPLOY_DIR%\
echo ======================================
echo.
echo Next steps:
echo.
echo   1. Go to https://huggingface.co/spaces
echo   2. Click 'Create new Space'
echo   3. Select 'Streamlit' as SDK
echo   4. Upload all files from %DEPLOY_DIR%\
echo.
echo ======================================
echo Ready to deploy!
echo ======================================
echo.
pause
