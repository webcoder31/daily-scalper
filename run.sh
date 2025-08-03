#!/bin/bash
# Trading Strategy Backtester - Quick start script
# This script sets up the virtual environment and launches the application

echo "🚀 Setting up Trading Strategy Backtester..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
echo "Activating virtual environment and installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt

echo "✅ Setup complete! Starting Trading Strategy Backtester..."
echo ""

# Launch application
python main.py