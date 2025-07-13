# Daily Scalper - Documentation Technique

## Architecture du Projet

### Vue d'ensemble
Daily Scalper est une application Python modulaire conçue pour tester et évaluer des stratégies de trading de cryptomonnaies. L'architecture suit les principes SOLID et utilise une approche orientée objet pour maximiser la réutilisabilité et la maintenabilité.

### Structure des Modules

```
daily-scalper/
├── strategies/          # 🎯 Stratégies de trading
│   ├── __init__.py
│   ├── base_strategy.py     # Classe abstraite de base
│   └── sma_crossover.py     # Exemple: SMA Crossover
├── backtest/           # ⚡ Moteur de backtest
│   ├── __init__.py
│   ├── backtest_engine.py   # Moteur principal avec vectorbt
│   └── performance_metrics.py # Calcul des métriques
├── utils/              # 🛠️ Utilitaires
│   ├── __init__.py
│   ├── data_loader.py       # Chargement des données (yfinance)
│   ├── visualizer.py        # Graphiques interactifs (plotly)
│   └── strategy_saver.py    # Sauvegarde des stratégies
├── data/               # 📊 Cache des données
├── results/            # 💾 Résultats sauvegardés
│   ├── strategies/          # Stratégies au format JSON/PKL
│   ├── reports/            # Rapports textuels
│   └── charts/             # Graphiques HTML
├── main.py             # 🚀 Application principale
├── test_setup.py       # 🧪 Tests de validation
├── start.sh            # 📜 Script de démarrage
└── config.py           # ⚙️ Configuration globale
```

## Composants Principaux

### 1. Stratégies (`strategies/`)

#### BaseStrategy (Classe Abstraite)
- **Rôle**: Définit l'interface commune pour toutes les stratégies
- **Méthodes clés**:
  - `generate_signals()`: Génère les signaux d'achat/vente
  - `validate_data()`: Valide les données d'entrée
  - `get_description()`: Description de la stratégie
  - `to_dict()`: Sérialisation pour sauvegarde

#### SMACrossoverStrategy
- **Rôle**: Exemple d'implémentation de stratégie
- **Logique**: Croisement de moyennes mobiles simples
- **Paramètres**: `short_window`, `long_window`
- **Signaux**:
  - Achat: SMA courte > SMA longue
  - Vente: SMA courte < SMA longue

### 2. Moteur de Backtest (`backtest/`)

#### BacktestEngine
- **Rôle**: Exécute les backtests avec vectorbt
- **Fonctionnalités**:
  - Simulation de trading avec commissions/slippage
  - Calcul automatique des métriques de base
  - Gestion des erreurs et validation des données
- **Configuration**:
  - Capital initial: $10,000 (par défaut)
  - Commission: 0.1% par transaction
  - Slippage: 0.01% par transaction

#### PerformanceMetrics
- **Rôle**: Calcul et analyse des métriques avancées
- **Métriques calculées**:
  - **Rendement**: Total return, Alpha vs Buy & Hold
  - **Risque**: Sharpe ratio, Volatilité, Max Drawdown, VaR 95%
  - **Trading**: Win rate, Profit factor, Nombre de trades
  - **Avancées**: Calmar ratio, Sortino ratio

### 3. Utilitaires (`utils/`)

#### DataLoader
- **Rôle**: Récupération et gestion des données de marché
- **Sources**: yfinance (Yahoo Finance)
- **Fonctionnalités**:
  - Cache automatique des données
  - Validation et nettoyage des données
  - Support de multiples cryptomonnaies
  - Gestion des erreurs de réseau

#### Visualizer
- **Rôle**: Création de graphiques interactifs
- **Technologies**: Plotly pour l'interactivité
- **Types de graphiques**:
  - Chandelier avec signaux d'achat/vente
  - Évolution du portfolio
  - Métriques de performance (radar chart)
  - Analyse du drawdown

#### StrategySaver
- **Rôle**: Persistance des stratégies et résultats
- **Formats de sauvegarde**:
  - JSON: Métadonnées et paramètres
  - Pickle: Données complètes (portfolio, signaux)
  - HTML: Graphiques interactifs
  - TXT: Rapports formatés

## Flux d'Exécution

### 1. Chargement des Données
```python
# DataLoader récupère les données via yfinance
data = loader.load_crypto_data("BTC-USD", period="1y")
# Validation automatique et cache local
```

### 2. Initialisation de la Stratégie
```python
# Création d'une stratégie avec paramètres
strategy = SMACrossoverStrategy(short_window=20, long_window=50)
# Validation des paramètres
```

### 3. Génération des Signaux
```python
# La stratégie analyse les données et génère les signaux
buy_signals, sell_signals = strategy.generate_signals(data)
# Signaux booléens indexés par date
```

### 4. Exécution du Backtest
```python
# BacktestEngine utilise vectorbt pour la simulation
results = engine.run_backtest(strategy, data)
# Calcul automatique des métriques
```

### 5. Analyse et Visualisation
```python
# Calcul des métriques avancées
metrics = PerformanceMetrics.calculate_advanced_metrics(results)
# Génération des graphiques interactifs
Visualizer.show_all_plots(results)
```

### 6. Sauvegarde (Optionnelle)
```python
# Sauvegarde si la stratégie est profitable
if PerformanceMetrics.is_strategy_profitable(metrics):
    saver.save_strategy_results(results)
```

## Critères de Profitabilité

Une stratégie est considérée comme profitable si elle respecte **tous** les critères suivants :

- **Rendement minimum**: 10% (`min_return = 0.1`)
- **Ratio de Sharpe minimum**: 1.0 (`min_sharpe = 1.0`)
- **Drawdown maximum**: 20% (`max_drawdown = 0.2`)
- **Nombre minimum de trades**: 5 (`min_trades = 5`)

Ces critères peuvent être ajustés dans `config.py`.

## Extension du Système

### Créer une Nouvelle Stratégie

1. **Hériter de BaseStrategy**:
```python
from strategies.base_strategy import BaseStrategy

class MaStrategie(BaseStrategy):
    def __init__(self, param1, param2):
        super().__init__("Ma Stratégie", {
            'param1': param1,
            'param2': param2
        })
```

2. **Implémenter les méthodes requises**:
```python
def generate_signals(self, data):
    # Votre logique ici
    buy_signals = ...
    sell_signals = ...
    return buy_signals, sell_signals

def get_description(self):
    return "Description de ma stratégie"
```

3. **Ajouter à l'initialisation**:
```python
# Dans strategies/__init__.py
from .ma_strategie import MaStrategie
__all__ = ['BaseStrategy', 'SMACrossoverStrategy', 'MaStrategie']
```

### Ajouter de Nouvelles Métriques

1. **Étendre PerformanceMetrics**:
```python
@staticmethod
def calculate_custom_metric(results):
    # Votre calcul personnalisé
    return custom_value
```

2. **Intégrer dans le calcul principal**:
```python
# Dans calculate_advanced_metrics()
metrics['custom_metric'] = calculate_custom_metric(results)
```

## Configuration Avancée

### Paramètres de Backtest
```python
# Dans config.py
DEFAULT_BACKTEST_CONFIG = {
    'initial_cash': 10000.0,    # Capital initial
    'commission': 0.001,        # 0.1% de commission
    'slippage': 0.0001,        # 0.01% de slippage
}
```

### Critères de Profitabilité
```python
PROFITABILITY_CRITERIA = {
    'min_return': 0.1,      # 10% minimum
    'min_sharpe': 1.0,      # Sharpe ratio minimum
    'max_drawdown': 0.2,    # 20% maximum
    'min_trades': 5,        # Minimum de trades
}
```

### Symboles Supportés
```python
POPULAR_CRYPTO_SYMBOLS = [
    "BTC-USD", "ETH-USD", "BNB-USD", "XRP-USD", "ADA-USD",
    # ... autres cryptomonnaies
]
```

## Dépannage

### Problèmes Courants

1. **Erreur d'import de modules**:
   - Vérifier que l'environnement virtuel est activé
   - Réinstaller les dépendances: `pip install -r requirements.txt`

2. **Données manquantes**:
   - Vérifier la connexion internet
   - Supprimer le cache: `rm -rf data/*.csv`

3. **Erreurs de calcul vectorbt**:
   - Vérifier que les données ont suffisamment de points (>100)
   - S'assurer que les signaux ne sont pas tous vides

4. **Graphiques ne s'affichent pas**:
   - Vérifier que plotly est installé
   - Ouvrir manuellement les fichiers HTML dans `results/charts/`

### Logs et Debug

Pour activer le mode debug, modifier le niveau de logging dans `main.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance et Optimisation

### Cache des Données
- Les données sont automatiquement mises en cache dans `data/`
- Cache valide pendant 24h par défaut
- Supprimer le cache pour forcer le rechargement

### Optimisation des Backtests
- Utiliser des périodes plus courtes pour les tests rapides
- Vectorbt optimise automatiquement les calculs
- Éviter les stratégies avec trop de signaux (>1000 trades)

### Mémoire
- Les résultats complets sont stockés en mémoire
- Pour de gros datasets, considérer la sauvegarde incrémentale
- Limiter le nombre de stratégies comparées simultanément

## Sécurité et Bonnes Pratiques

### Gestion des Données
- Ne jamais committer les fichiers de cache (`data/`)
- Les clés API (si ajoutées) doivent être dans des variables d'environnement
- Sauvegarder régulièrement les résultats importants

### Code Quality
- Suivre les conventions PEP 8
- Ajouter des docstrings pour les nouvelles fonctions
- Tester les nouvelles stratégies avec `test_setup.py`

### Limitations
- **Pas de trading en temps réel**: Uniquement du backtesting
- **Données limitées**: Dépendant de yfinance
- **Pas d'optimisation automatique**: Paramètres à ajuster manuellement