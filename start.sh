#!/bin/bash
# Script de démarrage pour Daily Scalper

echo "🚀 Daily Scalper - Démarrage..."

# Vérifier si l'environnement virtuel existe
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv
fi

# Activer l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
source venv/bin/activate

# Vérifier si les dépendances sont installées
if [ ! -f "venv/pyvenv.cfg" ] || ! python -c "import vectorbt" 2>/dev/null; then
    echo "📥 Installation des dépendances..."
    pip install -r requirements.txt
fi

# Lancer l'application
echo "▶️  Lancement de l'application..."
python main.py

echo "✅ Terminé!"