"""
Module for loading market data via yfinance.
"""

from typing import Optional, List
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import os


class DataLoader:
    """
    Class for loading and managing market data.
    """
    
    def __init__(self, cache_dir: str = "data"):
        """
        Initializes the data loader.
        
        Args:
            cache_dir: Directory for data cache
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
        Loads cryptocurrency data from yfinance.
        
        Args:
            symbol: Crypto symbol (e.g., "BTC-USD", "ETH-USD")
            period: Data period ("1d" (1 day), "5d" (5 days), "1mo" (1 month), "3mo" (3 months), "6mo" (6 months), "1y" (1 year), "2y" (2 years), "5y" (5 years), "10y" (10 years), "ytd" (year to date), "max" (maximum))
            start_date: Start date (format 'YYYY-MM-DD')
            end_date: End date (format 'YYYY-MM-DD')
            use_cache: Use local cache
            
        Returns:
            DataFrame with OHLCV data
        """
        # Cache filename
        cache_file = os.path.join(self.cache_dir, f"{symbol}_{period}.csv")
        
        # Check cache
        if use_cache and os.path.exists(cache_file):
            try:
                data = pd.read_csv(cache_file, index_col=0, parse_dates=True)
                print(f"Data loaded from cache: {cache_file}")
                
                # Check if data is recent (less than 1 day)
                if self._is_cache_recent(cache_file):
                    return self._validate_and_clean_data(data)
            except Exception as e:
                print(f"Error loading from cache: {e}")
        
        # Download data from yfinance
        try:
            print(f"Downloading data for {symbol}...")
            ticker = yf.Ticker(symbol)
            
            if start_date and end_date:
                data = ticker.history(start=start_date, end=end_date)
            else:
                data = ticker.history(period=period)
            
            if data.empty:
                raise ValueError(f"No data found for {symbol}")
            
            # Save to cache
            if use_cache:
                data.to_csv(cache_file)
                print(f"Data saved to cache: {cache_file}")
            
            return self._validate_and_clean_data(data)
            
        except Exception as e:
            raise RuntimeError(f"Error downloading data: {e}")
    
    def _is_cache_recent(self, cache_file: str, max_age_hours: int = 24) -> bool:
        """
        Checks if the cache file is recent.
        
        Args:
            cache_file: Cache file path
            max_age_hours: Maximum age in hours
            
        Returns:
            True if cache is recent, False otherwise
        """
        try:
            file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
            age = datetime.now() - file_time
            return age < timedelta(hours=max_age_hours)
        except:
            return False
    
    def _validate_and_clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Validates and cleans the data.
        
        Args:
            data: Raw DataFrame
            
        Returns:
            Cleaned and validated DataFrame
        """
        # Check required columns
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_columns = [col for col in required_columns if col not in data.columns]
        
        if missing_columns:
            raise ValueError(f"Missing columns: {missing_columns}")
        
        # Remove rows with missing values
        data = data.dropna()
        
        # Check that data remains
        if data.empty:
            raise ValueError("No valid data after cleaning")
        
        # Sort by date
        data = data.sort_index()
        
        # Check price consistency (High >= Low, etc.)
        invalid_rows = (data['High'] < data['Low']) | (data['High'] < data['Close']) | (data['Low'] > data['Close'])
        if invalid_rows.any():
            print(f"Warning: {invalid_rows.sum()} rows with inconsistent prices removed")
            data = data[~invalid_rows]
        
        print(f"Data loaded: {len(data)} points from {data.index[0].strftime('%Y-%m-%d')} to {data.index[-1].strftime('%Y-%m-%d')}")
        
        return data
    
    def get_available_symbols(self) -> List[str]:
        """
        Returns a list of popular crypto symbols.
        
        Returns:
            List of available symbols
        """
        return [
            "BTC-USD", "ETH-USD", "BNB-USD", "XRP-USD", "ADA-USD",
            "SOL-USD", "DOGE-USD", "DOT-USD", "AVAX-USD", "SHIB-USD",
            "MATIC-USD", "LTC-USD", "UNI-USD", "LINK-USD", "ATOM-USD"
        ]
    
    def clear_cache(self) -> None:
        """
        Deletes all cache files.
        """
        try:
            for file in os.listdir(self.cache_dir):
                if file.endswith('.csv'):
                    os.remove(os.path.join(self.cache_dir, file))
            print("Cache successfully deleted")
        except Exception as e:
            print(f"Error deleting cache: {e}")