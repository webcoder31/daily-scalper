"""
Configuration globale pour l'application Daily Scalper.
"""

# Configuration par défaut pour les backtests
DEFAULT_BACKTEST_CONFIG = {
    'initial_cash': 10000.0,
    'commission': 0.001,  # 0.1%
    'slippage': 0.0001,   # 0.01%
}

# Configuration pour la récupération des données
DEFAULT_DATA_CONFIG = {
    'default_symbol': 'BTC-USD',
    'default_period': '1y',
    'cache_enabled': True,
    'cache_max_age_hours': 24,
}

# Critères pour considérer une stratégie comme profitable
PROFITABILITY_CRITERIA = {
    'min_return': 0.1,      # 10% minimum
    'min_sharpe': 1.0,      # Sharpe ratio minimum
    'max_drawdown': 0.2,    # 20% maximum
    'min_trades': 5,        # Minimum de trades
}

# Configuration de visualisation
VISUALIZATION_CONFIG = {
    'default_height': 800,
    'show_volume': True,
    'show_signals': True,
    'show_indicators': True,
}

# Symboles crypto populaires
POPULAR_CRYPTO_SYMBOLS = [
    "BTC-USD", "ETH-USD", "BNB-USD", "XRP-USD", "ADA-USD",
    "SOL-USD", "DOGE-USD", "DOT-USD", "AVAX-USD", "SHIB-USD",
    "MATIC-USD", "LTC-USD", "UNI-USD", "LINK-USD", "ATOM-USD"
]