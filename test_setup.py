#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify the installation and proper functioning
of the Trading Strategy Backtester application.
"""

import sys
import os
import traceback

# Add root directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_imports():
    """Tests the import of all modules."""
    print("🧪 Testing imports...")
    
    try:
        # Test main imports
        from strategies.base.abstract_trading_strategy import AbstractTradingStrategy
        from strategies.implementations.sma_strategy import SMAStrategy
        from backtesting.backtest_engine import BacktestEngine
        from backtesting.performance_analyzer import PerformanceAnalyzer
        from market_data.market_data_provider import MarketDataProvider
        from visualization.backtest_chart_generator import BacktestChartGenerator
        from persistence.strategy_archiver import StrategyArchiver
        print("✅ All modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def test_dependencies():
    """Tests the availability of dependencies."""
    print("\n📦 Testing dependencies...")
    
    dependencies = [
        'pandas', 'numpy', 'yfinance', 'plotly', 'vectorbt'
    ]
    
    missing = []
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} - MISSING")
            missing.append(dep)
    
    if missing:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing)}")
        print("Install them with: pip install -r requirements.txt")
        return False
    
    return True


def test_strategy_creation():
    """Tests the creation of a strategy."""
    print("\n🎯 Testing strategy creation...")
    
    try:
        from strategies.implementations.sma_strategy import SMAStrategy
        
        strategy = SMAStrategy(short_window=10, long_window=20)
        print(f"✅ Strategy created: {strategy.name}")
        print(f"   Description: {strategy.get_explanation()}")
        print(f"   Parameters: {strategy.get_parameters()}")
        return True
    except Exception as e:
        print(f"❌ Error creating strategy: {e}")
        return False


def test_data_loading():
    """Tests data loading (without actual downloading)."""
    print("\n📥 Testing data loading...")
    
    try:
        from market_data.market_data_provider import MarketDataProvider
        
        loader = MarketDataProvider()
        symbols = loader.get_available_symbols()
        print(f"✅ DataLoader initialized")
        print(f"   Available symbols: {len(symbols)} (e.g.: {symbols[:3]})")
        return True
    except Exception as e:
        print(f"❌ Error initializing DataLoader: {e}")
        return False


def test_backtest_engine():
    """Tests the initialization of the backtest engine."""
    print("\n⚡ Testing backtest engine...")
    
    try:
        from backtesting.backtest_engine import BacktestEngine
        
        engine = BacktestEngine(initial_cash=10000, commission=0.001)
        print(f"✅ BacktestEngine initialized")
        print(f"   Initial capital: ${engine.initial_cash:,.2f}")
        print(f"   Commission: {engine.commission:.3%}")
        return True
    except Exception as e:
        print(f"❌ Error initializing BacktestEngine: {e}")
        return False


def test_file_structure():
    """Checks the file structure."""
    print("\n📁 Testing file structure...")
    
    required_dirs = ['cache', 'results', 'strategies', 'backtesting', 'market_data', 'visualization', 'persistence', 'core', 'ui', 'utils']
    required_files = ['main.py', 'requirements.txt', 'README.md']
    
    all_good = True
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✅ Directory {directory}/")
        else:
            print(f"❌ Directory {directory}/ - MISSING")
            all_good = False
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ File {file}")
        else:
            print(f"❌ File {file} - MISSING")
            all_good = False
    
    return all_good


def run_mini_backtest():
    """Runs a mini backtest with simulated data."""
    print("\n🚀 Testing mini backtest...")
    
    try:
        import pandas as pd
        import numpy as np
        from datetime import datetime, timedelta
        from strategies.implementations.sma_strategy import SMAStrategy
        from backtesting.backtest_engine import BacktestEngine
        
        # Creating simulated data
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        np.random.seed(42)
        
        # Price simulation with trend
        price_base = 30000
        returns = np.random.normal(0.001, 0.02, len(dates))
        prices = [price_base]
        
        for ret in returns[1:]:
            prices.append(prices[-1] * (1 + ret))
        
        # Creating DataFrame
        data = pd.DataFrame({
            'Open': prices,
            'High': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
            'Low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
            'Close': prices,
            'Volume': np.random.randint(1000, 10000, len(dates))
        }, index=dates)
        
        # Adjusting High/Low
        data['High'] = np.maximum(data['High'], data[['Open', 'Close']].max(axis=1))
        data['Low'] = np.minimum(data['Low'], data[['Open', 'Close']].min(axis=1))
        
        # Testing strategy
        strategy = SMAStrategy(short_window=10, long_window=20)
        engine = BacktestEngine(initial_cash=10000)
        
        results = engine.execute_strategy_evaluation(strategy, data)
        
        print(f"✅ Mini backtest successful!")
        print(f"   Return: {results['metrics']['total_return']:.2%}")
        print(f"   Trades: {results['metrics']['total_trades']}")
        print(f"   Period: {len(data)} days")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during mini backtest: {e}")
        traceback.print_exc()
        return False


def main():
    """Main test function."""
    print("=" * 60)
    print("🧪 Trading Strategy Backtester - VALIDATION TESTS")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Dependencies", test_dependencies),
        ("File structure", test_file_structure),
        ("Strategy creation", test_strategy_creation),
        ("Data loading", test_data_loading),
        ("Backtest engine", test_backtest_engine),
        ("Mini backtest", run_mini_backtest),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} - CRITICAL ERROR: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application is ready.")
        print("\n💡 To start the application:")
        print("   python main.py")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        print("\n🔧 Recommended actions:")
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. Check file structure")
        print("   3. Run tests again: python test_setup.py")
    
    print("=" * 60)
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())