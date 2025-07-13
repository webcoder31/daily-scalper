# Daily Scalper - Crypto Trading Strategy Tester

Application Python modulaire pour tester, évaluer et sauvegarder des stratégies de trading de cryptomonnaies utilisant vectorbt.

## Structure du Projet

```
daily-scalper/
├── data/                   # Données de marché et cache
├── strategies/             # Modules de stratégies de trading
├── backtest/              # Moteur de backtest
├── results/               # Résultats et sauvegardes
├── utils/                 # Utilitaires et helpers
├── main.py               # Script principal
├── requirements.txt      # Dépendances Python
└── README.md            # Documentation
```

## Installation

1. **Créer un environnement virtuel** (recommandé) :
```bash
python3 -m venv venv
source venv/bin/activate  # Sur macOS/Linux
# ou
venv\Scripts\activate     # Sur Windows
```

2. **Installer les dépendances** :
```bash
pip install -r requirements.txt
```

3. **Tester l'installation** :
```bash
python test_setup.py
```

## Utilisation

### Démarrage rapide
```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Lancer l'application
python main.py
```

### Script de démarrage automatique
```bash
# Utiliser le script de démarrage (recommandé)
./start.sh
```

## Fonctionnalités

- ✅ Stratégies modulaires et paramétrables
- ✅ Backtest avec vectorbt
- ✅ Visualisation interactive des résultats
- ✅ Sauvegarde des stratégies performantes
- ✅ Récupération automatique des données via yfinance

## Stratégies Disponibles

- **SMA Crossover**: Croisement de moyennes mobiles simples