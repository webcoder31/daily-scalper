"""
Module pour charger les données de marché via yfinance.
"""

from typing import Optional, List
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import os


class DataLoader:
    """
    Classe pour charger et gérer les données de marché.
    """
    
    def __init__(self, cache_dir: str = "data"):
        """
        Initialise le chargeur de données.
        
        Args:
            cache_dir: Répertoire pour le cache des données
        """
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def load_crypto_data(self, 
                        symbol: str = "BTC-USD",
                        period: str = "1y",
                        start_date: Optional[str] = None,
                        end_date: Optional[str] = None,
                        use_cache: bool = True) -> pd.DataFrame:
        """
        Charge les données de cryptomonnaie depuis yfinance.
        
        Args:
            symbol: Symbole de la crypto (ex: "BTC-USD", "ETH-USD")
            period: Période des données ("1d" (1 jour), "5d" (5 jours), "1mo" (1 mois), "3mo" (3 mois), "6mo" (6 mois), "1y" (1 an), "2y" (2 ans), "5y" (5 ans), "10y" (10 ans), "ytd" (depuis début d'année), "max" (maximum))
            start_date: Date de début (format 'YYYY-MM-DD')
            end_date: Date de fin (format 'YYYY-MM-DD')
            use_cache: Utiliser le cache local
            
        Returns:
            DataFrame avec les données OHLCV
        """
        # Nom du fichier cache
        cache_file = os.path.join(self.cache_dir, f"{symbol}_{period}.csv")
        
        # Vérifier le cache
        if use_cache and os.path.exists(cache_file):
            try:
                data = pd.read_csv(cache_file, index_col=0, parse_dates=True)
                print(f"Données chargées depuis le cache: {cache_file}")
                
                # Vérifier si les données sont récentes (moins de 1 jour)
                if self._is_cache_recent(cache_file):
                    return self._validate_and_clean_data(data)
            except Exception as e:
                print(f"Erreur lors du chargement du cache: {e}")
        
        # Télécharger les données depuis yfinance
        try:
            print(f"Téléchargement des données pour {symbol}...")
            ticker = yf.Ticker(symbol)
            
            if start_date and end_date:
                data = ticker.history(start=start_date, end=end_date)
            else:
                data = ticker.history(period=period)
            
            if data.empty:
                raise ValueError(f"Aucune donnée trouvée pour {symbol}")
            
            # Sauvegarder dans le cache
            if use_cache:
                data.to_csv(cache_file)
                print(f"Données sauvegardées dans le cache: {cache_file}")
            
            return self._validate_and_clean_data(data)
            
        except Exception as e:
            raise RuntimeError(f"Erreur lors du téléchargement des données: {e}")
    
    def _is_cache_recent(self, cache_file: str, max_age_hours: int = 24) -> bool:
        """
        Vérifie si le fichier cache est récent.
        
        Args:
            cache_file: Chemin du fichier cache
            max_age_hours: Âge maximum en heures
            
        Returns:
            True si le cache est récent, False sinon
        """
        try:
            file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
            age = datetime.now() - file_time
            return age < timedelta(hours=max_age_hours)
        except:
            return False
    
    def _validate_and_clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Valide et nettoie les données.
        
        Args:
            data: DataFrame brut
            
        Returns:
            DataFrame nettoyé et validé
        """
        # Vérifier les colonnes requises
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_columns = [col for col in required_columns if col not in data.columns]
        
        if missing_columns:
            raise ValueError(f"Colonnes manquantes: {missing_columns}")
        
        # Supprimer les lignes avec des valeurs manquantes
        data = data.dropna()
        
        # Vérifier qu'il reste des données
        if data.empty:
            raise ValueError("Aucune donnée valide après nettoyage")
        
        # Trier par date
        data = data.sort_index()
        
        # Vérifier la cohérence des prix (High >= Low, etc.)
        invalid_rows = (data['High'] < data['Low']) | (data['High'] < data['Close']) | (data['Low'] > data['Close'])
        if invalid_rows.any():
            print(f"Attention: {invalid_rows.sum()} lignes avec des prix incohérents supprimées")
            data = data[~invalid_rows]
        
        print(f"Données chargées: {len(data)} points de {data.index[0].strftime('%Y-%m-%d')} à {data.index[-1].strftime('%Y-%m-%d')}")
        
        return data
    
    def get_available_symbols(self) -> List[str]:
        """
        Retourne une liste des symboles crypto populaires.
        
        Returns:
            Liste des symboles disponibles
        """
        return [
            "BTC-USD", "ETH-USD", "BNB-USD", "XRP-USD", "ADA-USD",
            "SOL-USD", "DOGE-USD", "DOT-USD", "AVAX-USD", "SHIB-USD",
            "MATIC-USD", "LTC-USD", "UNI-USD", "LINK-USD", "ATOM-USD"
        ]
    
    def clear_cache(self) -> None:
        """
        Supprime tous les fichiers de cache.
        """
        try:
            for file in os.listdir(self.cache_dir):
                if file.endswith('.csv'):
                    os.remove(os.path.join(self.cache_dir, file))
            print("Cache supprimé avec succès")
        except Exception as e:
            print(f"Erreur lors de la suppression du cache: {e}")