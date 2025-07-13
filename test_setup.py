#!/usr/bin/env python3
"""
Script de test pour vérifier l'installation et le bon fonctionnement
de l'application Daily Scalper.
"""

import sys
import os
import traceback

# Ajout du répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Teste l'importation de tous les modules."""
    print("🧪 Test des imports...")
    
    try:
        # Test des imports principaux
        from strategies import BaseStrategy, SMACrossoverStrategy
        from backtest import BacktestEngine, PerformanceMetrics
        from utils import DataLoader, Visualizer, StrategySaver
        print("✅ Tous les modules importés avec succès")
        return True
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        return False

def test_dependencies():
    """Teste la disponibilité des dépendances."""
    print("\n📦 Test des dépendances...")
    
    dependencies = [
        'pandas', 'numpy', 'yfinance', 'plotly', 'vectorbt'
    ]
    
    missing = []
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} - MANQUANT")
            missing.append(dep)
    
    if missing:
        print(f"\n⚠️  Dépendances manquantes: {', '.join(missing)}")
        print("Installez-les avec: pip install -r requirements.txt")
        return False
    
    return True

def test_strategy_creation():
    """Teste la création d'une stratégie."""
    print("\n🎯 Test de création de stratégie...")
    
    try:
        from strategies import SMACrossoverStrategy
        
        strategy = SMACrossoverStrategy(short_window=10, long_window=20)
        print(f"✅ Stratégie créée: {strategy.name}")
        print(f"   Description: {strategy.get_description()}")
        print(f"   Paramètres: {strategy.get_parameters()}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création de stratégie: {e}")
        return False

def test_data_loading():
    """Teste le chargement de données (sans téléchargement réel)."""
    print("\n📥 Test de chargement de données...")
    
    try:
        from utils import DataLoader
        
        loader = DataLoader()
        symbols = loader.get_available_symbols()
        print(f"✅ DataLoader initialisé")
        print(f"   Symboles disponibles: {len(symbols)} (ex: {symbols[:3]})")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation du DataLoader: {e}")
        return False

def test_backtest_engine():
    """Teste l'initialisation du moteur de backtest."""
    print("\n⚡ Test du moteur de backtest...")
    
    try:
        from backtest import BacktestEngine
        
        engine = BacktestEngine(initial_cash=10000, commission=0.001)
        print(f"✅ BacktestEngine initialisé")
        print(f"   Capital initial: ${engine.initial_cash:,.2f}")
        print(f"   Commission: {engine.commission:.3%}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation du BacktestEngine: {e}")
        return False

def test_file_structure():
    """Vérifie la structure des fichiers."""
    print("\n📁 Test de la structure des fichiers...")
    
    required_dirs = ['data', 'results', 'strategies', 'backtest', 'utils']
    required_files = ['main.py', 'requirements.txt', 'README.md']
    
    all_good = True
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✅ Dossier {directory}/")
        else:
            print(f"❌ Dossier {directory}/ - MANQUANT")
            all_good = False
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ Fichier {file}")
        else:
            print(f"❌ Fichier {file} - MANQUANT")
            all_good = False
    
    return all_good

def run_mini_backtest():
    """Exécute un mini backtest avec des données simulées."""
    print("\n🚀 Test d'un mini backtest...")
    
    try:
        import pandas as pd
        import numpy as np
        from datetime import datetime, timedelta
        from strategies import SMACrossoverStrategy
        from backtest import BacktestEngine
        
        # Création de données simulées
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        np.random.seed(42)
        
        # Simulation d'un prix avec tendance
        price_base = 30000
        returns = np.random.normal(0.001, 0.02, len(dates))
        prices = [price_base]
        
        for ret in returns[1:]:
            prices.append(prices[-1] * (1 + ret))
        
        # Création du DataFrame
        data = pd.DataFrame({
            'Open': prices,
            'High': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
            'Low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
            'Close': prices,
            'Volume': np.random.randint(1000, 10000, len(dates))
        }, index=dates)
        
        # Ajustement High/Low
        data['High'] = np.maximum(data['High'], data[['Open', 'Close']].max(axis=1))
        data['Low'] = np.minimum(data['Low'], data[['Open', 'Close']].min(axis=1))
        
        # Test de la stratégie
        strategy = SMACrossoverStrategy(short_window=10, long_window=20)
        engine = BacktestEngine(initial_cash=10000)
        
        results = engine.run_backtest(strategy, data)
        
        print(f"✅ Mini backtest réussi!")
        print(f"   Rendement: {results['metrics']['total_return']:.2%}")
        print(f"   Trades: {results['metrics']['total_trades']}")
        print(f"   Période: {len(data)} jours")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du mini backtest: {e}")
        traceback.print_exc()
        return False

def main():
    """Fonction principale de test."""
    print("=" * 60)
    print("🧪 DAILY SCALPER - TESTS DE VALIDATION")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Dépendances", test_dependencies),
        ("Structure fichiers", test_file_structure),
        ("Création stratégie", test_strategy_creation),
        ("Chargement données", test_data_loading),
        ("Moteur backtest", test_backtest_engine),
        ("Mini backtest", run_mini_backtest),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} - ERREUR CRITIQUE: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 RÉSULTATS: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Tous les tests sont passés! L'application est prête.")
        print("\n💡 Pour démarrer l'application:")
        print("   python main.py")
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")
        print("\n🔧 Actions recommandées:")
        print("   1. Installez les dépendances: pip install -r requirements.txt")
        print("   2. Vérifiez la structure des fichiers")
        print("   3. Relancez les tests: python test_setup.py")
    
    print("=" * 60)
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())