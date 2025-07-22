#!/bin/bash
# Daily Scalper - Script de démarrage rapide
# Ce script configure l'environnement virtuel et lance l'application

echo "🚀 Configuration de Daily Scalper..."

# Créer l'environnement virtuel s'il n'existe pas
if [ ! -d "venv" ]; then
    echo "Création de l'environnement virtuel..."
    python3 -m venv venv
fi

# Activer l'environnement virtuel et installer les dépendances
echo "Activation de l'environnement virtuel et installation des dépendances..."
source venv/bin/activate
pip install -r requirements.txt

echo "✅ Configuration terminée! Démarrage de Daily Scalper..."
echo ""

# Lancer l'application
python main.py