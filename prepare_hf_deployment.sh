#!/bin/bash
# Helper script to prepare files for Hugging Face Spaces deployment

echo "======================================"
echo "Preparing files for Hugging Face"
echo "======================================"

# Create deployment directory
DEPLOY_DIR="hf_deployment"
mkdir -p $DEPLOY_DIR

echo ""
echo "📦 Copying core files..."

# Copy Python files
cp app.py $DEPLOY_DIR/
cp bse_loader.py $DEPLOY_DIR/
cp momentum_features.py $DEPLOY_DIR/
cp stock_picker_5session.py $DEPLOY_DIR/
cp backtest_5session.py $DEPLOY_DIR/
cp get_picks.py $DEPLOY_DIR/
cp incremental_training.py $DEPLOY_DIR/

# Copy optional files (comment out if not needed)
cp momentum_features_enhanced.py $DEPLOY_DIR/ 2>/dev/null || echo "  ⚠️  momentum_features_enhanced.py not found (optional)"
cp market_regime.py $DEPLOY_DIR/ 2>/dev/null || echo "  ⚠️  market_regime.py not found (optional)"
cp stock_picker_enhanced.py $DEPLOY_DIR/ 2>/dev/null || echo "  ⚠️  stock_picker_enhanced.py not found (optional)"
cp advanced_features.py $DEPLOY_DIR/ 2>/dev/null || echo "  ⚠️  advanced_features.py not found (optional)"

echo ""
echo "📝 Creating configuration files..."

# Create requirements.txt for HF (use streamlit version)
cp requirements-streamlit.txt $DEPLOY_DIR/requirements.txt

# Create README.md with YAML header
cp README_HUGGINGFACE.md $DEPLOY_DIR/README.md

# Create .gitignore
cat > $DEPLOY_DIR/.gitignore << 'EOF'
# Python
*.pyc
__pycache__/
*.py[cod]
*$py.class

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
EOF

echo ""
echo "📚 Copying documentation (optional)..."
cp WEBAPP_FEATURES.md $DEPLOY_DIR/ 2>/dev/null || echo "  ⚠️  WEBAPP_FEATURES.md not found (optional)"
cp INCREMENTAL_LEARNING.md $DEPLOY_DIR/ 2>/dev/null || echo "  ⚠️  INCREMENTAL_LEARNING.md not found (optional)"
cp DEPLOYMENT_GUIDE.md $DEPLOY_DIR/ 2>/dev/null || echo "  ⚠️  DEPLOYMENT_GUIDE.md not found (optional)"

echo ""
echo "✅ Files prepared in: $DEPLOY_DIR/"
echo ""
echo "📋 Next steps:"
echo ""
echo "  1. Go to https://huggingface.co/spaces"
echo "  2. Click 'Create new Space'"
echo "  3. Select 'Streamlit' as SDK"
echo "  4. Upload all files from $DEPLOY_DIR/"
echo ""
echo "OR use Git:"
echo ""
echo "  git clone https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME"
echo "  cp $DEPLOY_DIR/* YOUR_SPACE_NAME/"
echo "  cd YOUR_SPACE_NAME"
echo "  git add ."
echo "  git commit -m 'Initial deployment'"
echo "  git push"
echo ""
echo "======================================"
echo "✨ Ready to deploy!"
echo "======================================"
