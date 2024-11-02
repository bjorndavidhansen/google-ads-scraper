# src/config.py
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from logging import FileHandler, Handler, StreamHandler
from pathlib import Path
from typing import List, Optional, Tuple, Union
from urllib.parse import urlparse
import logging
import yaml


class LogLevel(str, Enum):
    """Valid logging levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class ProxyConfig:
    """
    Proxy configuration settings
    
    Attributes:
        enabled: Whether to use proxies
        urls: List of proxy URLs
        rotation_interval: Time in seconds between proxy rotations
        max_retries: Maximum number of proxy retry attempts
    """
    enabled: bool = False
    urls: List[str] = field(default_factory=list)
    rotation_interval: int = 300
    max_retries: int = 3

    def __post_init__(self) -> None:
        """Validate proxy configuration settings"""
        if self.enabled and not self.urls:
            raise ValueError("Proxy URLs required when enabled")
        if self.rotation_interval <= 0:
            raise ValueError("rotation_interval must be positive")
        if self.max_retries <= 0:
            raise ValueError("max_retries must be positive")
        if self.urls:
            for url in self.urls:
                self._validate_url(url)

    @staticmethod
    def _validate_url(url: str) -> None:
        """
        Validate proxy URL format
        
        Args:
            url: Proxy URL to validate
            
        Raises:
            ValueError: If URL format is invalid
        """
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            raise ValueError(f"Invalid proxy URL: {url}")


@dataclass 
class LoggingConfig:
    """
    Logging configuration settings
    
    Attributes:
        level: Logging level (DEBUG, INFO, etc.)
        format: Log message format string
        file: Optional log file path
        console: Whether to output logs to console
    """
    level: LogLevel = LogLevel.INFO
    format: str = "%(asctime)s - %(levelname)s - %(message)s"
    file: Optional[str] = "scraper.log"
    console: bool = True

    def __post_init__(self) -> None:
        """Convert and validate logging level"""
        if not isinstance(self.level, LogLevel):
            try:
                self.level = LogLevel(str(self.level).upper())
            except (ValueError, AttributeError) as e:
                raise ValueError(f"Invalid logging level: {self.level}") from e


@dataclass
class TargetsConfig:
    """
    Scraping targets configuration
    
    Attributes:
        keywords: List of search keywords
        locations: List of target locations
    """
    keywords: List[str] = field(default_factory=list)
    locations: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate target configuration"""
        if not self.keywords:
            raise ValueError("At least one keyword required")
        if not self.locations:
            raise ValueError("At least one location required")
        if not all(isinstance(keyword, str) for keyword in self.keywords):
            raise ValueError("All keywords must be strings")
        if not all(isinstance(location, str) for location in self.locations):
            raise ValueError("All locations must be strings")


@dataclass
class ScrapingConfig:
    """
    Main scraper configuration
    
    Attributes:
        headless: Whether to run browser in headless mode
        proxy: Proxy configuration settings
        logging: Logging configuration settings
        retry_limit: Maximum number of retry attempts
        timeout: Request timeout in seconds
        delay_range: Range of delay between requests (min, max)
        max_concurrent: Maximum concurrent requests
        max_requests_per_window: Request limit per time window
        time_window: Time window in seconds for rate limiting
        base_url: Base URL for scraping
        output_dir: Directory for output files
    """
    headless: bool = True
    proxy: ProxyConfig = field(default_factory=ProxyConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    retry_limit: int = 3
    timeout: int = 10
    delay_range: Tuple[int, int] = (2, 5)
    max_concurrent: int = 3
    max_requests_per_window: int = 10
    time_window: int = 60
    base_url: str = "https://www.google.com"
    output_dir: Path = field(default_factory=lambda: Path("results"))

    def __post_init__(self) -> None:
        """Validate and normalize configuration settings"""
        if isinstance(self.output_dir, str):
            self.output_dir = Path(self.output_dir)
        if self.retry_limit <= 0:
            raise ValueError("retry_limit must be positive")
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")
        if len(self.delay_range) != 2:
            raise ValueError("delay_range must have exactly 2 values")
        if self.delay_range[0] > self.delay_range[1]:
            raise ValueError("Invalid delay range")
        if not isinstance(self.proxy, ProxyConfig):
            # pylint: disable=not-a-mapping
            self.proxy = ProxyConfig(**self.proxy)
        if not isinstance(self.logging, LoggingConfig):
            # pylint: disable=not-a-mapping
            self.logging = LoggingConfig(**self.logging)

    @classmethod
def from_yaml(cls, path: Union[str, Path]) -> ScrapingConfig:
    """
    Load configuration from YAML file
    
    Args:
        path: Path to YAML configuration file
        
    Returns:
        ScrapingConfig: Configuration instance
        
    Raises:
        FileNotFoundError: If config file not found
        yaml.YAMLError: If YAML format is invalid
        ValueError: If config content is invalid
    """
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
        
    try:
        with open(config_path, encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)
            
        if not isinstance(config_dict, dict):
            raise ValueError("Invalid YAML format: must be a dictionary")
            
        # Convert nested dicts to dataclass instances
        if 'proxy' in config_dict:
            config_dict['proxy'] = ProxyConfig(**config_dict['proxy'])
        if 'logging' in config_dict:
            config_dict['logging'] = LoggingConfig(**config_dict['logging'])
            
        instance = cls(**config_dict)
        instance.validate()
        return instance
        
    except yaml.YAMLError:
        # Re-raise YAML errors directly
        raise
    except Exception as e:
        raise ValueError(f"Error loading config: {str(e)}") from e

    # Update the validate() method in ScrapingConfig
def validate(self) -> None:
    """Additional validation of config values"""
    if not isinstance(self.base_url, str):
        raise ValueError("base_url must be a string")
        
    try:
        result = urlparse(self.base_url)
        if not all([result.scheme, result.netloc]):
            raise ValueError(f"Invalid base URL: {self.base_url}")
        if result.scheme not in ['http', 'https']:
            raise ValueError(f"Invalid URL scheme: {result.scheme}")
    except Exception as e:
        raise ValueError(f"Invalid base URL: {str(e)}")

def __post_init__(self) -> None:
    """Validate and normalize configuration settings"""
    if isinstance(self.output_dir, str):
        self.output_dir = Path(self.output_dir)
    if self.retry_limit <= 0:
        raise ValueError("retry_limit must be positive")
    if self.timeout <= 0:
        raise ValueError("timeout must be positive")
    if len(self.delay_range) != 2:
        raise ValueError("delay_range must have exactly 2 values")
    if self.delay_range[0] > self.delay_range[1]:
        raise ValueError("Invalid delay range")
    if not isinstance(self.proxy, ProxyConfig):
        self.proxy = ProxyConfig(**self.proxy)
    if not isinstance(self.logging, LoggingConfig):
        self.logging = LoggingConfig(**self.logging)
    self.validate()  # Call validate after initialization

    def ensure_paths(self) -> None:
        """Ensure required directories exist"""
        self.output_dir.mkdir(parents=True, exist_ok=True)

   def setup_logging(self) -> None:
    """Configure logging based on settings"""
    # Remove any existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        handler.close()
        root_logger.removeHandler(handler)
        
    handlers: List[Handler] = []
    
    if self.logging.file:
        handlers.append(FileHandler(self.logging.file))
    if self.logging.console:
        handlers.append(StreamHandler())
        
    logging.basicConfig(
        level=self.logging.level.value,
        format=self.logging.format,
        handlers=handlers,
        force=True
    )