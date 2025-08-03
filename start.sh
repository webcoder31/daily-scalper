#!/bin/bash
# Startup script for Trading Strategy Backtester

echo "🚀 Trading Strategy Backtester - Starting..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if [ ! -f "venv/pyvenv.cfg" ] || ! python -c "import vectorbt" 2>/dev/null; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
fi

# Launch the application
echo "▶️  Launching application..."
python main.py

echo "✅ Finished!"