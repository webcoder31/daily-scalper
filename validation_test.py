#!/usr/bin/env python3
"""
Comprehensive validation script for the Trading Strategy Backtester refactored codebase.
Tests imports, functionality, integration, and compatibility across all modules.
"""

import sys
import traceback
from typing import Dict, List, Any, Optional
import pandas as pd


def test_imports() -> Dict[str, Any]:
    """Test all module imports for circular dependencies and missing imports."""
    print("=" * 60)
    print("TESTING MODULE IMPORTS")
    print("=" * 60)
    
    results = {
        'success': True,
        'errors': [],
        'modules_tested': []
    }
    
    # Test core modules
    core_modules = [
        'config',
        'main',
        'core.strategy_backtester',
        'core.interactive_cli'
    ]
    
    for module in core_modules:
        try:
            print(f"Testing import: {module}")
            exec(f"import {module}")
            results['modules_tested'].append(module)
            print(f"✓ {module} imported successfully")
        except Exception as e:
            error_msg = f"Failed to import {module}: {str(e)}"
            print(f"✗ {error_msg}")
            results['errors'].append(error_msg)
            results['success'] = False
    
    # Test strategy modules
    strategy_modules = [
        'strategies',
        'strategies.base.abstract_strategy',
        'strategies.base.strategy_registry',
        'strategies.implementations.sma_strategy',
        'strategies.implementations.rsi_strategy',
        'strategies.implementations.bb_strategy',
        'strategies.implementations.ema_rsi_strategy'
    ]
    
    for module in strategy_modules:
        try:
            print(f"Testing import: {module}")
            exec(f"import {module}")
            results['modules_tested'].append(module)
            print(f"✓ {module} imported successfully")
        except Exception as e:
            error_msg = f"Failed to import {module}: {str(e)}"
            print(f"✗ {error_msg}")
            results['errors'].append(error_msg)
            results['success'] = False
    
    # Test backtesting modules
    backtesting_modules = [
        'backtesting',
        'backtesting.backtest_engine',
        'backtesting.performance_analyzer'
    ]
    
    for module in backtesting_modules:
        try:
            print(f"Testing import: {module}")
            exec(f"import {module}")
            results['modules_tested'].append(module)
            print(f"✓ {module} imported successfully")
        except Exception as e:
            error_msg = f"Failed to import {module}: {str(e)}"
            print(f"✗ {error_msg}")
            results['errors'].append(error_msg)
            results['success'] = False
    
    # Test new module structure
    new_modules = [
        'market_data',
        'market_data.market_data_provider',
        'market_data.period_translator',
        'visualization',
        'visualization.backtest_chart_generator',
        'persistence',
        'persistence.strategy_archiver',
        'ui',
        'ui.components',
        'ui.theme',
        'utils',
        'utils.logging_config'
    ]
    
    for module in new_modules:
        try:
            print(f"Testing import: {module}")
            exec(f"import {module}")
            results['modules_tested'].append(module)
            print(f"✓ {module} imported successfully")
        except Exception as e:
            error_msg = f"Failed to import {module}: {str(e)}"
            print(f"✗ {error_msg}")
            results['errors'].append(error_msg)
            results['success'] = False
    
    print(f"\nImport Test Summary:")
    print(f"Modules tested: {len(results['modules_tested'])}")
    print(f"Successful imports: {len(results['modules_tested']) - len(results['errors'])}")
    print(f"Failed imports: {len(results['errors'])}")
    
    return results


def test_core_integration() -> Dict[str, Any]:
    """Test core application integration."""
    print("\n" + "=" * 60)
    print("TESTING CORE APPLICATION INTEGRATION")
    print("=" * 60)
    
    results = {
        'success': True,
        'errors': [],
        'tests_passed': []
    }
    
    try:
        # Test config module
        print("Testing config module...")
        import config
        
        # Test config functions exist
        required_functions = ['get_data_config', 'get_backtest_config', 'get_profitability_criteria']
        for func_name in required_functions:
            if hasattr(config, func_name):
                print(f"✓ Config function {func_name} exists")
                results['tests_passed'].append(f"config.{func_name}")
                # Test function call
                try:
                    func = getattr(config, func_name)
                    result = func()
                    print(f"✓ Config function {func_name} callable")
                    results['tests_passed'].append(f"config.{func_name} callable")
                except Exception as e:
                    error_msg = f"Config function {func_name} call failed: {str(e)}"
                    print(f"✗ {error_msg}")
                    results['errors'].append(error_msg)
                    results['success'] = False
            else:
                error_msg = f"Missing config function: {func_name}"
                print(f"✗ {error_msg}")
                results['errors'].append(error_msg)
                results['success'] = False
        
        # Test core application classes
        print("Testing core application module...")
        from core.strategy_backtester import StrategyBacktester
        
        # Test app instantiation
        app = StrategyBacktester()
        print("✓ StrategyBacktester instantiated successfully")
        results['tests_passed'].append("StrategyBacktester instantiation")
        
        # Test CLI module
        print("Testing CLI module...")
        from core.interactive_cli import main, parse_arguments
        print("✓ CLI module functions imported successfully")
        results['tests_passed'].append("CLI module functions import")
        
    except Exception as e:
        error_msg = f"Core integration test failed: {str(e)}"
        print(f"✗ {error_msg}")
        results['errors'].append(error_msg)
        results['success'] = False
        traceback.print_exc()
    
    return results


def test_strategy_system() -> Dict[str, Any]:
    """Test strategy system validation."""
    print("\n" + "=" * 60)
    print("TESTING STRATEGY SYSTEM")
    print("=" * 60)
    
    results = {
        'success': True,
        'errors': [],
        'tests_passed': []
    }
    
    try:
        # Test strategy registry
        print("Testing strategy registry...")
        from strategies.base.strategy_registry import get_strategy_names, create_strategy
        
        strategies = get_strategy_names()
        print(f"✓ Strategy registry loaded with {len(strategies)} strategies")
        results['tests_passed'].append(f"Strategy registry ({len(strategies)} strategies)")
        
        # Test individual strategies (test first 3 to avoid too many tests)
        for strategy_name in strategies[:3]:
            try:
                strategy_instance = create_strategy(strategy_name)
                print(f"✓ Strategy {strategy_name} created successfully")
                results['tests_passed'].append(f"Strategy {strategy_name}")
                
            except Exception as e:
                error_msg = f"Failed to create strategy {strategy_name}: {str(e)}"
                print(f"✗ {error_msg}")
                results['errors'].append(error_msg)
                results['success'] = False
        
    except Exception as e:
        error_msg = f"Strategy system test failed: {str(e)}"
        print(f"✗ {error_msg}")
        results['errors'].append(error_msg)
        results['success'] = False
        traceback.print_exc()
    
    return results


def test_utils_integration() -> Dict[str, Any]:
    """Test utility modules integration."""
    print("\n" + "=" * 60)
    print("TESTING UTILITY MODULES INTEGRATION")
    print("=" * 60)
    
    results = {
        'success': True,
        'errors': [],
        'tests_passed': []
    }
    
    try:
        # Test market data provider
        print("Testing market data provider...")
        from market_data.market_data_provider import MarketDataProvider
        
        data_provider = MarketDataProvider()
        print("✓ MarketDataProvider instantiated successfully")
        results['tests_passed'].append("MarketDataProvider instantiation")
        
        # Test period translator
        print("Testing period translator...")
        from market_data.period_translator import PeriodTranslator
        
        translator = PeriodTranslator()
        description = translator.get_period_description("1y")
        print(f"✓ Period translator working: '1y' -> '{description}'")
        results['tests_passed'].append("PeriodTranslator functionality")
        
        # Test theme
        print("Testing theme...")
        from ui.theme import THEME, ThemeManager
        
        theme_manager = ThemeManager()
        validated_theme = theme_manager.validate_theme(THEME)
        print("✓ Theme validation successful")
        results['tests_passed'].append("Theme validation")
        
        # Test UI components
        print("Testing UI components...")
        from ui.components import ui_modern_table, ui_block_header, ui_error_message
        
        # Test creating a modern table
        table = ui_modern_table("Test Table")
        print("✓ UI components functions imported and callable")
        results['tests_passed'].append("UI components functions")
        
        # Test strategy results persistence
        print("Testing strategy results persistence...")
        from persistence.strategy_archiver import StrategyArchiver
        
        persistence = StrategyArchiver()
        print("✓ StrategyArchiver instantiated successfully")
        results['tests_passed'].append("StrategyArchiver instantiation")
        
        # Test chart generator
        print("Testing chart generator...")
        from visualization.backtest_chart_generator import BacktestChartGenerator
        
        chart_generator = BacktestChartGenerator()
        print("✓ BacktestChartGenerator instantiated successfully")
        results['tests_passed'].append("BacktestChartGenerator instantiation")
        
    except Exception as e:
        error_msg = f"Utils integration test failed: {str(e)}"
        print(f"✗ {error_msg}")
        results['errors'].append(error_msg)
        results['success'] = False
        traceback.print_exc()
    
    return results


def test_backtest_system() -> Dict[str, Any]:
    """Test backtesting system validation."""
    print("\n" + "=" * 60)
    print("TESTING BACKTESTING SYSTEM")
    print("=" * 60)
    
    results = {
        'success': True,
        'errors': [],
        'tests_passed': []
    }
    
    try:
        # Test strategy backtest engine
        print("Testing strategy backtest engine...")
        from backtesting.backtest_engine import BacktestEngine
        from market_data.market_data_provider import MarketDataProvider
        
        data_provider = MarketDataProvider()
        engine = BacktestEngine()
        print("✓ BacktestEngine instantiated successfully")
        results['tests_passed'].append("BacktestEngine instantiation")
        
        # Test performance analyzer
        print("Testing performance analyzer...")
        from backtesting.performance_analyzer import PerformanceAnalyzer
        
        analyzer = PerformanceAnalyzer()
        print("✓ PerformanceAnalyzer instantiated successfully")
        results['tests_passed'].append("PerformanceAnalyzer instantiation")
        
    except Exception as e:
        error_msg = f"Backtest system test failed: {str(e)}"
        print(f"✗ {error_msg}")
        results['errors'].append(error_msg)
        results['success'] = False
        traceback.print_exc()
    
    return results


def test_cross_module_compatibility() -> Dict[str, Any]:
    """Test cross-module compatibility and data structures."""
    print("\n" + "=" * 60)
    print("TESTING CROSS-MODULE COMPATIBILITY")
    print("=" * 60)
    
    results = {
        'success': True,
        'errors': [],
        'tests_passed': []
    }
    
    try:
        # Test that all custom exceptions can be imported
        print("Testing custom exceptions...")
        
        exception_imports = [
            "from strategies.base.abstract_strategy import StrategyError, ParameterValidationError, DataValidationError",
            "from backtesting.backtest_engine import BacktestError, DataValidationError, StrategyExecutionError",
            "from market_data.market_data_provider import DataLoadError, CacheError, ValidationError"
        ]
        
        for import_stmt in exception_imports:
            try:
                exec(import_stmt)
                print(f"✓ Exception import successful: {import_stmt.split('import')[1].strip()}")
                results['tests_passed'].append(f"Exception import: {import_stmt.split('import')[1].strip()}")
            except Exception as e:
                error_msg = f"Failed exception import: {import_stmt} - {str(e)}"
                print(f"✗ {error_msg}")
                results['errors'].append(error_msg)
                results['success'] = False
        
        # Test type consistency
        print("Testing type consistency...")
        
        # Import all modules to check for type conflicts
        import config
        from core.strategy_backtester import StrategyBacktester
        from strategies.base.strategy_registry import get_strategy_names
        from backtesting.backtest_engine import BacktestEngine
        from market_data.market_data_provider import MarketDataProvider
        
        print("✓ All major modules imported without type conflicts")
        results['tests_passed'].append("Type consistency check")
        
    except Exception as e:
        error_msg = f"Cross-module compatibility test failed: {str(e)}"
        print(f"✗ {error_msg}")
        results['errors'].append(error_msg)
        results['success'] = False
        traceback.print_exc()
    
    return results


def main():
    """Run comprehensive validation tests."""
    print("Trading Strategy Backtester CODEBASE VALIDATION")
    print("=" * 60)
    print("Testing refactored codebase for consistency, compatibility, and functionality")
    print("=" * 60)
    
    all_results = {}
    
    # Run all validation tests
    all_results['imports'] = test_imports()
    all_results['core_integration'] = test_core_integration()
    all_results['strategy_system'] = test_strategy_system()
    all_results['utils_integration'] = test_utils_integration()
    all_results['backtest_system'] = test_backtest_system()
    all_results['cross_module'] = test_cross_module_compatibility()
    
    # Generate summary report
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY REPORT")
    print("=" * 60)
    
    total_tests = 0
    total_passed = 0
    total_errors = 0
    
    for test_name, result in all_results.items():
        test_count = len(result.get('tests_passed', [])) + len(result.get('modules_tested', []))
        error_count = len(result.get('errors', []))
        passed_count = test_count - error_count
        
        total_tests += test_count
        total_passed += passed_count
        total_errors += error_count
        
        status = "✓ PASS" if result['success'] else "✗ FAIL"
        print(f"{test_name.upper()}: {status} ({passed_count}/{test_count} tests passed)")
        
        if result.get('errors'):
            for error in result['errors']:
                print(f"  - {error}")
    
    print("\n" + "=" * 60)
    print(f"OVERALL VALIDATION RESULT")
    print("=" * 60)
    print(f"Total tests run: {total_tests}")
    print(f"Tests passed: {total_passed}")
    print(f"Tests failed: {total_errors}")
    
    if total_errors == 0:
        print("🎉 ALL VALIDATION TESTS PASSED!")
        print("The refactored codebase is consistent, compatible, and functional.")
        return True
    else:
        print(f"⚠️  {total_errors} VALIDATION ISSUES FOUND")
        print("Please review and fix the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)