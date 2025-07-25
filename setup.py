#!/usr/bin/env python3
"""
Setup script for NVSTWZ Autonomous Investment Bot.
"""
import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def create_env_file():
    """Create .env file from template."""
    env_template = Path("config.env.example")
    env_file = Path(".env")
    
    if env_file.exists():
        print("✓ .env file already exists")
        return True
    
    if not env_template.exists():
        print("✗ config.env.example not found")
        return False
    
    # Copy template to .env
    with open(env_template, 'r') as f:
        content = f.read()
    
    with open(env_file, 'w') as f:
        f.write(content)
    
    print("✓ Created .env file from template")
    print("⚠️  Please edit .env file with your API keys and configuration")
    return True

def install_dependencies():
    """Install Python dependencies."""
    return run_command("pip install -r requirements.txt", "Installing Python dependencies")

def create_directories():
    """Create necessary directories."""
    directories = ["logs", "data", "config"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✓ Created necessary directories")
    return True

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("✗ Python 3.8 or higher is required")
        return False
    
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def main():
    """Main setup function."""
    print("=" * 60)
    print("NVSTWZ Autonomous Investment Bot Setup")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Create directories
    if not create_directories():
        return 1
    
    # Create .env file
    if not create_env_file():
        return 1
    
    # Install dependencies
    if not install_dependencies():
        return 1
    
    print("\n" + "=" * 60)
    print("Setup completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Edit .env file with your API keys:")
    print("   - Fidelity API credentials")
    print("   - Alpha Vantage API key")
    print("   - News API key")
    print("   - Finnhub API key")
    print("   - Database connection string")
    print("\n2. Configure your trading parameters in .env")
    print("\n3. Run the bot: python main.py")
    print("\nFor more information, see README.md")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 