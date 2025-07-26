# Daily Scalper - Crypto Trading Strategy Tester

Application Python modulaire pour tester, évaluer et sauvegarder des stratégies de trading de cryptomonnaies utilisant vectorbt.

## 📋 Table des Matières

- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Stratégies Disponibles](#stratégies-disponibles)
- [Configuration des Backtests](#configuration-des-backtests)
- [Exemples d'Utilisation](#exemples-dutilisation)
- [Résultats et Visualisation](#résultats-et-visualisation)
- [Troubleshooting](#troubleshooting)
- [Structure du Projet](#structure-du-projet)

## 🚀 Installation

### Prérequis
- Python 3.8 ou supérieur
- pip (gestionnaire de packages Python)

### 1. Cloner le projet
```bash
git clone <votre-repo-url>
cd daily-scalper
```

### 2. Créer un environnement virtuel (recommandé)
```bash
python3 -m venv venv
source venv/bin/activate  # Sur macOS/Linux
# ou
venv\Scripts\activate     # Sur Windows
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Tester l'installation
```bash
python test_setup.py
```

Si tous les tests passent, votre installation est prête ! 🎉

## ⚙️ Configuration

### Configuration par défaut

Le fichier `config.py` contient toutes les configurations par défaut :

```python
# Configuration des backtests
DEFAULT_BACKTEST_CONFIG = {
    'initial_cash': 10000.0,     # Capital initial en USD
    'commission': 0.001,         # Commission (0.1%)
    'slippage': 0.0001,         # Slippage (0.01%)
}

# Configuration des données
DEFAULT_DATA_CONFIG = {
    'default_symbol': 'BTC-USD', # Symbole par défaut
    'default_period': '1y',      # Période par défaut (1 an)
    'cache_enabled': True,       # Cache des données activé
    'cache_max_age_hours': 24,   # Durée du cache (24h)
}
```

### Symboles supportés

L'application supporte tous les symboles crypto disponibles sur Yahoo Finance :
- **Bitcoin**: BTC-USD
- **Ethereum**: ETH-USD
- **Binance Coin**: BNB-USD
- **XRP**: XRP-USD
- **Cardano**: ADA-USD
- **Solana**: SOL-USD
- Et bien d'autres...

## 🎯 Utilisation

### Démarrage rapide

```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Lancer l'application
python main.py
```

### Interface interactive

L'application propose un menu interactif avec les options suivantes :

1. **Tester une stratégie** - Exécuter un backtest sur une stratégie
2. **Comparer des stratégies** - Comparer plusieurs stratégies
3. **Voir les résultats sauvegardés** - Consulter les résultats précédents
4. **Configuration** - Modifier les paramètres
5. **Quitter** - Fermer l'application

## 📈 Stratégies Disponibles

### 1. SMA Crossover (Croisement de Moyennes Mobiles)
**Fichier**: `strategies/sma_crossover.py`

**Description**: Stratégie basée sur le croisement de deux moyennes mobiles simples.

**Paramètres**:
- `short_window`: Période de la moyenne mobile courte (défaut: 10)
- `long_window`: Période de la moyenne mobile longue (défaut: 20)

**Signaux**:
- **Achat**: Quand la moyenne courte croise au-dessus de la moyenne longue
- **Vente**: Quand la moyenne courte croise en-dessous de la moyenne longue

### 2. RSI Strategy (Relative Strength Index)
**Fichier**: `strategies/rsi_strategy.py`

**Description**: Stratégie basée sur l'indicateur RSI pour identifier les zones de surachat/survente.

**Paramètres**:
- `rsi_period`: Période de calcul du RSI (défaut: 14)
- `oversold_threshold`: Seuil de survente (défaut: 30)
- `overbought_threshold`: Seuil de surachat (défaut: 70)

**Signaux**:
- **Achat**: Quand le RSI sort de la zone de survente (< 30)
- **Vente**: Quand le RSI entre en zone de surachat (> 70)

## 🔧 Configuration des Backtests

### Paramètres de base

```python
backtest_config = {
    'initial_cash': 10000.0,    # Capital de départ
    'commission': 0.001,        # Frais de transaction (0.1%)
    'slippage': 0.0001,        # Glissement de prix (0.01%)
}
```

### Critères de rentabilité

```python
PROFITABILITY_CRITERIA = {
    'min_return': 0.1,          # Rendement minimum (10%)
    'min_sharpe': 1.0,          # Ratio de Sharpe minimum
    'max_drawdown': 0.2,        # Drawdown maximum (20%)
    'min_trades': 5,            # Nombre minimum de trades
}
```

### Périodes de données

Vous pouvez utiliser différentes périodes pour vos backtests :

- `'1d'` - 1 jour
- `'5d'` - 5 jours
- `'1mo'` - 1 mois
- `'3mo'` - 3 mois
- `'6mo'` - 6 mois
- `'1y'` - 1 an (défaut)
- `'2y'` - 2 ans
- `'5y'` - 5 ans
- `'max'` - Maximum disponible

## 💡 Exemples d'Utilisation

### Exemple 1: Backtest simple avec SMA Crossover

```python
from strategies import SMACrossoverStrategy
from backtest import BacktestEngine
from utils import DataLoader

# 1. Charger les données
loader = DataLoader()
data = loader.get_data('BTC-USD', period='1y')  # 1y = 1 an

# 2. Créer la stratégie
strategy = SMACrossoverStrategy(short_window=10, long_window=20)

# 3. Configurer le backtest
engine = BacktestEngine(initial_cash=10000, commission=0.001)

# 4. Exécuter le backtest
results = engine.run_backtest(strategy, data)

# 5. Afficher les résultats
print(f"Rendement total: {results['metrics']['total_return']:.2%}")
print(f"Ratio de Sharpe: {results['metrics']['sharpe_ratio']:.2f}")
```

### Exemple 2: Comparer plusieurs stratégies

```python
from strategies import SMACrossoverStrategy, RSIStrategy
from backtest import BacktestEngine
from utils import DataLoader, Visualizer

# Charger les données
loader = DataLoader()
data = loader.get_data('ETH-USD', period='6mo')  # 6mo = 6 mois

# Créer les stratégies
sma_strategy = SMACrossoverStrategy(short_window=5, long_window=15)
rsi_strategy = RSIStrategy(rsi_period=14, oversold_threshold=30)

# Backtest des stratégies
engine = BacktestEngine(initial_cash=10000)
sma_results = engine.run_backtest(sma_strategy, data)
rsi_results = engine.run_backtest(rsi_strategy, data)

# Comparer les résultats
print("SMA Strategy:")
print(f"  Rendement: {sma_results['metrics']['total_return']:.2%}")
print(f"  Sharpe: {sma_results['metrics']['sharpe_ratio']:.2f}")

print("RSI Strategy:")
print(f"  Rendement: {rsi_results['metrics']['total_return']:.2%}")
print(f"  Sharpe: {rsi_results['metrics']['sharpe_ratio']:.2f}")
```

### Exemple 3: Optimisation des paramètres

```python
from strategies import SMACrossoverStrategy
from backtest import BacktestEngine
from utils import DataLoader

loader = DataLoader()
data = loader.get_data('BTC-USD', period='1y')  # 1y = 1 an
engine = BacktestEngine(initial_cash=10000)

best_return = 0
best_params = None

# Test de différents paramètres
for short in range(5, 20, 5):
    for long in range(20, 50, 10):
        strategy = SMACrossoverStrategy(short_window=short, long_window=long)
        results = engine.run_backtest(strategy, data)
        
        if results['metrics']['total_return'] > best_return:
            best_return = results['metrics']['total_return']
            best_params = (short, long)

print(f"Meilleurs paramètres: short={best_params[0]}, long={best_params[1]}")
print(f"Rendement: {best_return:.2%}")
```

## 📊 Résultats et Visualisation

### Métriques calculées

Chaque backtest génère les métriques suivantes :

- **Rendement total** (`total_return`): Performance globale
- **Rendement annualisé** (`annualized_return`): Performance annuelle
- **Volatilité** (`volatility`): Risque de la stratégie
- **Ratio de Sharpe** (`sharpe_ratio`): Rendement ajusté au risque
- **Drawdown maximum** (`max_drawdown`): Perte maximale
- **Nombre de trades** (`total_trades`): Fréquence de trading
- **Taux de réussite** (`win_rate`): Pourcentage de trades gagnants

### Visualisations disponibles

1. **Graphique des prix** avec signaux d'achat/vente
2. **Évolution du portfolio** vs Buy & Hold
3. **Courbe des drawdowns**
4. **Distribution des rendements**
5. **Indicateurs techniques** utilisés par la stratégie

### Sauvegarde des résultats

Les résultats sont automatiquement sauvegardés dans le dossier `results/` :

```
results/
├── strategies/           # Stratégies sauvegardées
├── backtests/           # Résultats de backtests
└── visualizations/      # Graphiques générés
```

## 🛠️ Troubleshooting

### Problèmes courants

#### 1. Erreur d'installation des dépendances
```bash
# Solution: Mettre à jour pip
pip install --upgrade pip
pip install -r requirements.txt
```

#### 2. Erreur de téléchargement des données
```bash
# Vérifier la connexion internet et le symbole
# Exemple: 'BTCUSD' n'existe pas, utiliser 'BTC-USD'
```

#### 3. Erreur "Module not found"
```bash
# Vérifier que l'environnement virtuel est activé
source venv/bin/activate
python test_setup.py
```

#### 4. Performance lente
- Réduire la période de données (`period='3mo'` (3 mois) au lieu de `period='5y'` (5 ans))
- Activer le cache dans la configuration
- Utiliser des paramètres de stratégie moins complexes

### Logs et débogage

Pour activer les logs détaillés, modifiez le niveau de logging dans votre script :

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Support

Si vous rencontrez des problèmes :

1. Vérifiez que tous les tests passent : `python test_setup.py`
2. Consultez les logs d'erreur
3. Vérifiez votre connexion internet pour le téléchargement des données
4. Assurez-vous d'utiliser Python 3.8+

## 📁 Structure du Projet

```
daily-scalper/
├── 📁 data/                    # Données de marché et cache
│   └── cache/                  # Cache des données téléchargées
├── 📁 strategies/              # Modules de stratégies de trading
│   ├── __init__.py            # Exports des stratégies
│   ├── base_strategy.py       # Classe de base pour les stratégies
│   ├── sma_crossover.py       # Stratégie SMA Crossover
│   └── rsi_strategy.py        # Stratégie RSI
├── 📁 backtest/               # Moteur de backtest
│   ├── __init__.py           # Exports du moteur
│   ├── engine.py             # Moteur principal de backtest
│   └── metrics.py            # Calcul des métriques de performance
├── 📁 utils/                  # Utilitaires et helpers
│   ├── __init__.py           # Exports des utilitaires
│   ├── data_loader.py        # Chargement des données de marché
│   ├── visualizer.py         # Génération des graphiques
│   └── strategy_saver.py     # Sauvegarde des stratégies
├── 📁 results/               # Résultats et sauvegardes
│   ├── strategies/           # Stratégies sauvegardées
│   ├── backtests/           # Résultats de backtests
│   └── visualizations/      # Graphiques générés
├── 📄 main.py               # Script principal avec interface
├── 📄 config.py             # Configuration globale
├── 📄 requirements.txt      # Dépendances Python
├── 📄 test_setup.py         # Tests de validation
└── 📄 README.md            # Cette documentation
```

## 🎯 Fonctionnalités

- ✅ **Stratégies modulaires** et paramétrables
- ✅ **Backtest vectorisé** avec vectorbt pour des performances optimales
- ✅ **Visualisation interactive** des résultats avec Plotly
- ✅ **Sauvegarde automatique** des stratégies performantes
- ✅ **Récupération automatique** des données via yfinance
- ✅ **Cache intelligent** pour éviter les téléchargements répétés
- ✅ **Métriques complètes** de performance et de risque
- ✅ **Interface utilisateur** simple et intuitive
- ✅ **Tests automatisés** pour valider l'installation

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

---

**Happy Trading! 🚀📈**