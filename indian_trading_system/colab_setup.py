# Fix imports for Google Colab
import sys
import os

# Add the project root to Python path
project_root = '/content/letssee'
if os.path.exists(project_root):
    sys.path.insert(0, project_root)

    # Also add indian_trading_system to path
    trading_system_path = os.path.join(project_root, 'indian_trading_system')
    if os.path.exists(trading_system_path):
        sys.path.insert(0, trading_system_path)

print(f"✅ Python path configured")
print(f"Current working directory: {os.getcwd()}")
