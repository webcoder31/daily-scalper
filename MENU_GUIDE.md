# Menu Interactif - Daily Scalper

## Lancement de l'application

Pour lancer l'application avec le menu interactif :

```bash
python3 main.py
```

## Options du menu

Le menu principal propose 5 options :

### 1. 🧪 Tester une stratégie
- Permet de tester une stratégie SMA Crossover avec des paramètres personnalisés
- Vous pouvez choisir :
  - Le symbole crypto (ex: BTC-USD, ETH-USD)
  - La période d'analyse (1d (1 jour), 5d (5 jours), 1mo (1 mois), 3mo (3 mois), 6mo (6 mois), 1y (1 an), 2y (2 ans), 5y (5 ans), 10y (10 ans), ytd (depuis début d'année), max (maximum))
  - Les paramètres SMA (courte et longue)
  - Affichage des graphiques
  - Sauvegarde automatique si profitable

### 2. 🔄 Comparer des stratégies
- Compare automatiquement plusieurs configurations SMA
- Affiche un classement des meilleures stratégies
- Permet de choisir le symbole et la période

### 3. 📚 Voir les résultats sauvegardés
- Affiche l'historique des stratégies profitables sauvegardées
- Montre les métriques de performance de chaque stratégie

### 4. ⚙️ Configuration
- Affiche les paramètres actuels de configuration
- Guide pour modifier la configuration dans config.py

### 5. 🚪 Quitter
- Ferme l'application proprement

## Installation des dépendances

Si vous rencontrez des erreurs de modules manquants, utilisez :

```bash
python3 setup_and_test.py
```

Ou installez manuellement :

```bash
pip3 install -r requirements.txt
```

## Navigation

- Utilisez les chiffres 1-5 pour naviguer dans le menu
- Appuyez sur Ctrl+C pour annuler une opération en cours
- Suivez les instructions à l'écran pour chaque option

L'application est maintenant entièrement interactive et correspond à la documentation du README principal !