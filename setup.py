#!/usr/bin/env python3
"""
Setup script for Algo Trader
Handles environment setup and dependency installation
"""

import sys
import subprocess
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    if version.major == 3 and version.minor >= 13:
        print("⚠️  Warning: Python 3.13 detected. Some dependencies may have compatibility issues.")
        print("   Recommended: Python 3.10, 3.11, or 3.12")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    print("✅ Python version OK")

def create_venv():
    """Create virtual environment"""
    if os.path.exists("venv"):
        print("✅ Virtual environment already exists")
        return
    
    print("Creating virtual environment...")
    subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
    print("✅ Virtual environment created")

def get_pip_command():
    """Get the correct pip command for the virtual environment"""
    if sys.platform == "win32":
        return [sys.executable.replace("python", "venv\\Scripts\\python.exe"), "-m", "pip"]
    else:
        return ["./venv/bin/python", "-m", "pip"]

def install_dependencies():
    """Install minimal dependencies first"""
    pip_cmd = get_pip_command()
    
    print("\nUpgrading pip...")
    subprocess.run(pip_cmd + ["install", "--upgrade", "pip"], check=True)
    
    print("\nInstalling minimal dependencies...")
    try:
        subprocess.run(pip_cmd + ["install", "-r", "requirements-minimal.txt"], check=True)
        print("✅ Minimal dependencies installed")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        sys.exit(1)

def setup_env():
    """Set up environment file"""
    if os.path.exists(".env"):
        print("✅ .env file already exists")
        return
    
    print("Creating .env file from template...")
    with open(".env.example", "r") as src, open(".env", "w") as dst:
        dst.write(src.read())
    
    print("✅ .env file created")
    print("⚠️  Please edit .env and add your TRADINGVIEW_WEBHOOK_SECRET")

def main():
    """Main setup function"""
    print("🚀 Algo Trader Setup\n")
    
    # Check Python version
    check_python_version()
    
    # Create virtual environment
    create_venv()
    
    # Install dependencies
    install_dependencies()
    
    # Setup environment
    setup_env()
    
    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("1. Activate virtual environment:")
    if sys.platform == "win32":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("2. Edit .env file with your configuration")
    print("3. Run the test: python scripts/test_webhook_flow.py")
    print("\nOr use the quick test: ./run_test.sh")

if __name__ == "__main__":
    main()