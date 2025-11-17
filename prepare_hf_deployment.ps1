# Helper script to prepare files for Hugging Face Spaces deployment (Windows PowerShell)

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Preparing files for Hugging Face" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Create deployment directory
$DEPLOY_DIR = "hf_deployment"
New-Item -ItemType Directory -Force -Path $DEPLOY_DIR | Out-Null

Write-Host "📦 Copying core files..." -ForegroundColor Yellow
Write-Host ""

# Copy Python files
Copy-Item "app.py" -Destination $DEPLOY_DIR
Copy-Item "bse_loader.py" -Destination $DEPLOY_DIR
Copy-Item "momentum_features.py" -Destination $DEPLOY_DIR
Copy-Item "stock_picker_5session.py" -Destination $DEPLOY_DIR
Copy-Item "backtest_5session.py" -Destination $DEPLOY_DIR
Copy-Item "get_picks.py" -Destination $DEPLOY_DIR
Copy-Item "incremental_training.py" -Destination $DEPLOY_DIR

# Copy optional files
try {
    Copy-Item "momentum_features_enhanced.py" -Destination $DEPLOY_DIR -ErrorAction Stop
} catch {
    Write-Host "  ⚠️  momentum_features_enhanced.py not found (optional)" -ForegroundColor DarkYellow
}

try {
    Copy-Item "market_regime.py" -Destination $DEPLOY_DIR -ErrorAction Stop
} catch {
    Write-Host "  ⚠️  market_regime.py not found (optional)" -ForegroundColor DarkYellow
}

try {
    Copy-Item "stock_picker_enhanced.py" -Destination $DEPLOY_DIR -ErrorAction Stop
} catch {
    Write-Host "  ⚠️  stock_picker_enhanced.py not found (optional)" -ForegroundColor DarkYellow
}

try {
    Copy-Item "advanced_features.py" -Destination $DEPLOY_DIR -ErrorAction Stop
} catch {
    Write-Host "  ⚠️  advanced_features.py not found (optional)" -ForegroundColor DarkYellow
}

Write-Host ""
Write-Host "📝 Creating configuration files..." -ForegroundColor Yellow

# Create requirements.txt for HF (use streamlit version)
Copy-Item "requirements-streamlit.txt" -Destination "$DEPLOY_DIR\requirements.txt"

# Create README.md with YAML header
Copy-Item "README_HUGGINGFACE.md" -Destination "$DEPLOY_DIR\README.md"

# Create .gitignore
$gitignore = @"
# Python
*.pyc
__pycache__/
*.py[cod]
*`$py.class

# Cache files
*.pkl
*.cache

# Data files
*.csv
stock_picker_data/

# Environment
venv/
env/
.env

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Streamlit
.streamlit/
"@

$gitignore | Out-File -FilePath "$DEPLOY_DIR\.gitignore" -Encoding UTF8

Write-Host ""
Write-Host "📚 Copying documentation (optional)..." -ForegroundColor Yellow

try {
    Copy-Item "WEBAPP_FEATURES.md" -Destination $DEPLOY_DIR -ErrorAction Stop
} catch {
    Write-Host "  ⚠️  WEBAPP_FEATURES.md not found (optional)" -ForegroundColor DarkYellow
}

try {
    Copy-Item "INCREMENTAL_LEARNING.md" -Destination $DEPLOY_DIR -ErrorAction Stop
} catch {
    Write-Host "  ⚠️  INCREMENTAL_LEARNING.md not found (optional)" -ForegroundColor DarkYellow
}

try {
    Copy-Item "DEPLOYMENT_GUIDE.md" -Destination $DEPLOY_DIR -ErrorAction Stop
} catch {
    Write-Host "  ⚠️  DEPLOYMENT_GUIDE.md not found (optional)" -ForegroundColor DarkYellow
}

Write-Host ""
Write-Host "✅ Files prepared in: $DEPLOY_DIR\" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  1. Go to https://huggingface.co/spaces" -ForegroundColor White
Write-Host "  2. Click 'Create new Space'" -ForegroundColor White
Write-Host "  3. Select 'Streamlit' as SDK" -ForegroundColor White
Write-Host "  4. Upload all files from $DEPLOY_DIR\" -ForegroundColor White
Write-Host ""
Write-Host "OR use Git:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  git clone https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME" -ForegroundColor White
Write-Host "  Copy-Item $DEPLOY_DIR\* -Destination YOUR_SPACE_NAME\" -ForegroundColor White
Write-Host "  cd YOUR_SPACE_NAME" -ForegroundColor White
Write-Host "  git add ." -ForegroundColor White
Write-Host "  git commit -m 'Initial deployment'" -ForegroundColor White
Write-Host "  git push" -ForegroundColor White
Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "✨ Ready to deploy!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan
