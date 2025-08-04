"""
Market data loading and caching module for cryptocurrency trading strategies.

This module provides the DataLoader class for fetching, caching, and validating
cryptocurrency market data from Yahoo Finance. It includes intelligent caching,
data validation, and comprehensive error handling.

Classes:
    DataLoader: Main class for loading and managing market data
    DataLoadError: Custom exception for data loading errors
    CacheError: Custom exception for cache-related errors
    ValidationError: Custom exception for data validation errors

Example:
    >>> from utils.data_loader import DataLoader
    >>> loader = DataLoader(cache_dir="cache")
    >>> data = loader.load_crypto_data("BTC-USD", "1y")
    >>> print(f"Loaded {len(data)} data points")
"""

from typing import Optional, List, Dict, Any, Union
from pathlib import Path
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import os
import logging

# Configure logging
from logging.logging_manager import get_logger
logger = get_logger(__name__)


class DataLoadError(Exception):
    """Exception raised when data loading fails."""
    

    def __init__(self, message: str, symbol: Optional[str] = None, cause: Optional[Exception] = None) -> None:
        """
        Initialize DataLoadError.
        
        Args:
            message: Error message describing the issue.
            symbol: The symbol that caused the error (optional).
            cause: The underlying exception that caused this error (optional).
        """
        self.symbol = symbol
        self.cause = cause
        super().__init__(message)


class CacheError(Exception):
    """Exception raised when cache operations fail."""
    

    def __init__(self, message: str, cache_path: Optional[str] = None, cause: Optional[Exception] = None) -> None:
        """
        Initialize CacheError.
        
        Args:
            message: Error message describing the issue.
            cache_path: The cache file path that caused the error (optional).
            cause: The underlying exception that caused this error (optional).
        """
        self.cache_path = cache_path
        self.cause = cause
        super().__init__(message)


class ValidationError(Exception):
    """Exception raised when data validation fails."""
    

    def __init__(self, message: str, data_info: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize ValidationError.
        
        Args:
            message: Error message describing the validation issue.
            data_info: Additional information about the invalid data (optional).
        """
        self.data_info = data_info or {}
        super().__init__(message)


class MarketDataProvider:
    """
    Class for loading and managing cryptocurrency market data with caching.
    
    This class provides methods to fetch cryptocurrency data from Yahoo Finance,
    cache it locally for performance, and validate the data quality. It includes
    comprehensive error handling and data validation.
    
    Attributes:
        cache_dir: Directory path for storing cached data files.
        cache_max_age_hours: Maximum age of cached data in hours before refresh.
        
    Example:
        >>> loader = MarketDataProvider(cache_dir="data", cache_max_age_hours=24)
        >>> data = loader.fetch_cryptocurrency_data("BTC-USD", "1y")
        >>> symbols = loader.get_supported_cryptocurrency_symbols()
    """
    
    # Valid period values for yfinance
    VALID_PERIODS: List[str] = [
        "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"
    ]
    
    # Required columns for OHLCV data
    REQUIRED_COLUMNS: List[str] = ["Open", "High", "Low", "Close", "Volume"]
    

    def __init__(self, cache_dir: str = "cache", cache_max_age_hours: int = 24) -> None:
        """
        Initialize the DataLoader with caching configuration.
        
        Args:
            cache_dir: Directory for storing cached data files.
            cache_max_age_hours: Maximum age of cached data in hours before refresh.
            
        Raises:
            CacheError: If cache directory cannot be created.
        """
        self.cache_dir = Path(cache_dir)
        self.cache_max_age_hours = cache_max_age_hours
        
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Cache directory initialized: {self.cache_dir}")
        except OSError as e:
            raise CacheError(
                f"Failed to create cache directory: {cache_dir}",
                cache_path=str(cache_dir),
                cause=e
            ) from e
    

    def fetch_cryptocurrency_data(
        self,
        symbol: str = "BTC-USD",
        period: str = "1y",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        use_cache: bool = True,
        force_refresh: bool = False
    ) -> pd.DataFrame:
        """
        Load cryptocurrency data from Yahoo Finance with caching support.
        
        Args:
            symbol: Cryptocurrency symbol (e.g., "BTC-USD", "ETH-USD").
            period: Data period for yfinance. Valid values: "1d", "5d", "1mo", 
                   "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max".
            start_date: Start date in 'YYYY-MM-DD' format (overrides period).
            end_date: End date in 'YYYY-MM-DD' format (overrides period).
            use_cache: Whether to use local cache for data storage and retrieval.
            force_refresh: Force refresh of cached data even if recent.
            
        Returns:
            DataFrame with OHLCV data indexed by date.
            
        Raises:
            DataLoadError: If data loading fails or no data is available.
            ValidationError: If loaded data fails validation checks.
            ValueError: If invalid parameters are provided.
        """
        # Validate inputs
        self._validate_load_parameters(symbol, period, start_date, end_date)
        
        # Generate cache filename
        cache_key = self._generate_cache_key(symbol, period, start_date, end_date)
        cache_file = self.cache_dir / f"{cache_key}.csv"
        
        # Try to load from cache first
        if use_cache and not force_refresh:
            cached_data = self._load_from_cache(cache_file)
            if cached_data is not None:
                logger.info(f"Data loaded from cache: {cache_file}")
                return cached_data
        
        # Download fresh data from Yahoo Finance
        try:
            logger.info(f"Downloading data for {symbol}...")
            data = self._download_data(symbol, period, start_date, end_date)
            
            # Validate and clean the data
            validated_data = self._validate_and_clean_data(data, symbol)
            
            # Save to cache if enabled
            if use_cache:
                self._save_to_cache(validated_data, cache_file)
                logger.info(f"Data saved to cache: {cache_file}")
            
            logger.info(
                f"Data loaded successfully: {len(validated_data)} points "
                f"from {validated_data.index[0].strftime('%Y-%m-%d')} "
                f"to {validated_data.index[-1].strftime('%Y-%m-%d')}"
            )
            
            return validated_data
            
        except Exception as e:
            if isinstance(e, (DataLoadError, ValidationError)):
                raise
            raise DataLoadError(
                f"Unexpected error loading data for {symbol}: {str(e)}",
                symbol=symbol,
                cause=e
            ) from e
    

    def _validate_load_parameters(
        self,
        symbol: str,
        period: str,
        start_date: Optional[str],
        end_date: Optional[str]
    ) -> None:
        """
        Validate parameters for data loading.
        
        Args:
            symbol: Cryptocurrency symbol to validate.
            period: Period string to validate.
            start_date: Start date string to validate.
            end_date: End date string to validate.
            
        Raises:
            ValueError: If any parameter is invalid.
        """
        if not symbol or not isinstance(symbol, str):
            raise ValueError("Symbol must be a non-empty string")
        
        if period not in self.VALID_PERIODS:
            raise ValueError(
                f"Invalid period '{period}'. Valid periods: {', '.join(self.VALID_PERIODS)}"
            )
        
        # Validate date formats if provided
        if start_date:
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError as e:
                raise ValueError(f"Invalid start_date format. Use 'YYYY-MM-DD': {start_date}") from e
        
        if end_date:
            try:
                datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError as e:
                raise ValueError(f"Invalid end_date format. Use 'YYYY-MM-DD': {end_date}") from e
        
        # Validate date range if both provided
        if start_date and end_date:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            if start >= end:
                raise ValueError("start_date must be before end_date")
    

    def _generate_cache_key(
        self,
        symbol: str,
        period: str,
        start_date: Optional[str],
        end_date: Optional[str]
    ) -> str:
        """
        Generate a unique cache key for the data request.
        
        Args:
            symbol: Cryptocurrency symbol.
            period: Data period.
            start_date: Start date (optional).
            end_date: End date (optional).
            
        Returns:
            Unique cache key string.
        """
        if start_date and end_date:
            return f"{symbol}_{start_date}_{end_date}"
        return f"{symbol}_{period}"
    

    def _load_from_cache(self, cache_file: Path) -> Optional[pd.DataFrame]:
        """
        Load data from cache file if it exists and is recent.
        
        Args:
            cache_file: Path to the cache file.
            
        Returns:
            Cached DataFrame if available and recent, None otherwise.
            
        Raises:
            CacheError: If cache file exists but cannot be read.
        """
        if not cache_file.exists():
            return None
        
        try:
            # Check if cache is recent enough
            if not self._is_cache_recent(cache_file):
                logger.info(f"Cache file is stale: {cache_file}")
                return None
            
            # Load and validate cached data
            data = pd.read_csv(cache_file, index_col=0, parse_dates=True)
            return self._validate_and_clean_data(data, cache_file.stem.split('_')[0])
            
        except Exception as e:
            logger.warning(f"Error loading from cache {cache_file}: {e}")
            # Don't raise exception, just return None to trigger fresh download
            return None
    

    def _is_cache_recent(self, cache_file: Path) -> bool:
        """
        Check if the cache file is recent enough to use.
        
        Args:
            cache_file: Path to the cache file.
            
        Returns:
            True if cache is recent enough, False otherwise.
        """
        try:
            file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
            age = datetime.now() - file_time
            return age < timedelta(hours=self.cache_max_age_hours)
        except OSError:
            return False
    

    def _download_data(
        self,
        symbol: str,
        period: str,
        start_date: Optional[str],
        end_date: Optional[str]
    ) -> pd.DataFrame:
        """
        Download data from Yahoo Finance.
        
        Args:
            symbol: Cryptocurrency symbol.
            period: Data period.
            start_date: Start date (optional).
            end_date: End date (optional).
            
        Returns:
            Raw DataFrame from yfinance.
            
        Raises:
            DataLoadError: If download fails or no data is returned.
        """
        try:
            ticker = yf.Ticker(symbol)
            
            if start_date and end_date:
                data = ticker.history(start=start_date, end=end_date)
            else:
                data = ticker.history(period=period)
            
            if data.empty:
                raise DataLoadError(
                    f"No data available for symbol '{symbol}' with the specified parameters",
                    symbol=symbol
                )
            
            return data
            
        except Exception as e:
            if isinstance(e, DataLoadError):
                raise
            raise DataLoadError(
                f"Failed to download data from Yahoo Finance for {symbol}: {str(e)}",
                symbol=symbol,
                cause=e
            ) from e
    

    def _validate_and_clean_data(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """
        Validate and clean the loaded data.
        
        Args:
            data: Raw DataFrame to validate and clean.
            symbol: Symbol name for error reporting.
            
        Returns:
            Cleaned and validated DataFrame.
            
        Raises:
            ValidationError: If data fails validation checks.
        """
        if data.empty:
            raise ValidationError(
                "Data is empty after loading",
                data_info={"symbol": symbol, "shape": data.shape}
            )
        
        # Check for required columns
        missing_columns = [col for col in self.REQUIRED_COLUMNS if col not in data.columns]
        if missing_columns:
            raise ValidationError(
                f"Missing required columns: {missing_columns}",
                data_info={
                    "symbol": symbol,
                    "available_columns": list(data.columns),
                    "missing_columns": missing_columns
                }
            )
        
        # Remove rows with missing values in critical columns
        original_length = len(data)
        data = data.dropna(subset=self.REQUIRED_COLUMNS)
        
        if data.empty:
            raise ValidationError(
                "No valid data remaining after removing rows with missing values",
                data_info={"symbol": symbol, "original_length": original_length}
            )
        
        # Sort by date index
        data = data.sort_index()
        
        # Validate price consistency (High >= Low, Close between High and Low, etc.)
        invalid_rows = self._find_invalid_price_rows(data)
        if invalid_rows.any():
            invalid_count = invalid_rows.sum()
            logger.warning(f"Removing {invalid_count} rows with inconsistent prices for {symbol}")
            data = data[~invalid_rows]
        
        if data.empty:
            raise ValidationError(
                "No valid data remaining after price consistency checks",
                data_info={"symbol": symbol, "original_length": original_length}
            )
        
        # Validate volume data
        if (data['Volume'] < 0).any():
            logger.warning(f"Found negative volume values for {symbol}, setting to 0")
            data.loc[data['Volume'] < 0, 'Volume'] = 0
        
        return data
    

    def _find_invalid_price_rows(self, data: pd.DataFrame) -> pd.Series:
        """
        Find rows with invalid price relationships.
        
        Args:
            data: DataFrame with OHLC data.
            
        Returns:
            Boolean Series indicating invalid rows.
        """
        invalid_conditions = [
            data['High'] < data['Low'],           # High must be >= Low
            data['High'] < data['Open'],          # High must be >= Open
            data['High'] < data['Close'],         # High must be >= Close
            data['Low'] > data['Open'],           # Low must be <= Open
            data['Low'] > data['Close'],          # Low must be <= Close
            data['High'] <= 0,                    # Prices must be positive
            data['Low'] <= 0,
            data['Open'] <= 0,
            data['Close'] <= 0
        ]
        
        # Combine all invalid conditions
        invalid_rows = pd.Series(False, index=data.index)
        for condition in invalid_conditions:
            invalid_rows |= condition
        
        return invalid_rows
    

    def _save_to_cache(self, data: pd.DataFrame, cache_file: Path) -> None:
        """
        Save data to cache file.
        
        Args:
            data: DataFrame to save.
            cache_file: Path where to save the cache file.
            
        Raises:
            CacheError: If saving to cache fails.
        """
        try:
            data.to_csv(cache_file)
        except Exception as e:
            raise CacheError(
                f"Failed to save data to cache: {cache_file}",
                cache_path=str(cache_file),
                cause=e
            ) from e
    

    def get_available_symbols(self) -> List[str]:
        """
        Get a list of popular cryptocurrency symbols supported by Yahoo Finance.
        
        Returns:
            List of cryptocurrency symbol strings.
        """
        return [
            "BTC-USD", "ETH-USD", "BNB-USD", "XRP-USD", "ADA-USD",
            "SOL-USD", "DOGE-USD", "DOT-USD", "AVAX-USD", "SHIB-USD",
            "MATIC-USD", "LTC-USD", "UNI-USD", "LINK-USD", "ATOM-USD",
            "ALGO-USD", "VET-USD", "ICP-USD", "FIL-USD", "TRX-USD"
        ]
    

    def get_symbol_info(self, symbol: str) -> Dict[str, Any]:
        """
        Get basic information about a cryptocurrency symbol.
        
        Args:
            symbol: Cryptocurrency symbol to get info for.
            
        Returns:
            Dictionary with symbol information.
            
        Raises:
            DataLoadError: If symbol information cannot be retrieved.
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                "symbol": symbol,
                "name": info.get("longName", "Unknown"),
                "currency": info.get("currency", "USD"),
                "market_cap": info.get("marketCap"),
                "volume": info.get("volume24Hr"),
                "price": info.get("regularMarketPrice")
            }
        except Exception as e:
            raise DataLoadError(
                f"Failed to get symbol information for {symbol}: {str(e)}",
                symbol=symbol,
                cause=e
            ) from e
    

    def clear_cache(self, symbol: Optional[str] = None) -> int:
        """
        Clear cached data files.
        
        Args:
            symbol: Specific symbol to clear cache for. If None, clears all cache.
            
        Returns:
            Number of files deleted.
            
        Raises:
            CacheError: If cache clearing fails.
        """
        try:
            deleted_count = 0
            
            if symbol:
                # Clear cache for specific symbol
                pattern = f"{symbol}_*.csv"
                for cache_file in self.cache_dir.glob(pattern):
                    cache_file.unlink()
                    deleted_count += 1
                    logger.info(f"Deleted cache file: {cache_file}")
            else:
                # Clear all cache files
                for cache_file in self.cache_dir.glob("*.csv"):
                    cache_file.unlink()
                    deleted_count += 1
                    logger.info(f"Deleted cache file: {cache_file}")
            
            logger.info(f"Cache cleared successfully: {deleted_count} files deleted")
            return deleted_count
            
        except Exception as e:
            raise CacheError(
                f"Failed to clear cache: {str(e)}",
                cache_path=str(self.cache_dir),
                cause=e
            ) from e
    
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get information about the current cache state.
        
        Returns:
            Dictionary with cache information including file count, total size, etc.
        """
        try:
            cache_files = list(self.cache_dir.glob("*.csv"))
            total_size = sum(f.stat().st_size for f in cache_files)
            
            file_info = []
            for cache_file in cache_files:
                stat = cache_file.stat()
                file_info.append({
                    "name": cache_file.name,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime),
                    "is_recent": self.is_cached_data_fresh(cache_file)
                })
            
            return {
                "cache_dir": str(self.cache_dir),
                "file_count": len(cache_files),
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "max_age_hours": self.cache_max_age_hours,
                "files": file_info
            }
            
        except Exception as e:
            logger.error(f"Error getting cache info: {e}")
            return {
                "cache_dir": str(self.cache_dir),
                "error": str(e)
            }