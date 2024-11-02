# tests/test_config.py
import pytest
from pathlib import Path
import logging
import yaml
from tempfile import TemporaryDirectory

from src.config import (
    ProxyConfig,
    LoggingConfig, 
    TargetsConfig,
    ScrapingConfig
)


# ProxyConfig Tests
def test_proxy_config_defaults():
    config = ProxyConfig()
    assert not config.enabled
    assert config.urls == []
    assert config.rotation_interval == 300
    assert config.max_retries == 3


def test_proxy_config_validation():
    with pytest.raises(ValueError):
        ProxyConfig(rotation_interval=0)
    with pytest.raises(ValueError):
        ProxyConfig(max_retries=0)
    with pytest.raises(ValueError):
        ProxyConfig(urls=["not-a-url"])


def test_proxy_config_valid_urls():
    config = ProxyConfig(
        enabled=True,
        urls=["http://proxy1.com:8080", "https://proxy2.com:8080"]
    )
    assert len(config.urls) == 2


# LoggingConfig Tests  
def test_logging_config_defaults():
    config = LoggingConfig()
    assert config.level == "INFO"
    assert "%(asctime)s" in config.format
    assert config.file == "scraper.log"
    assert config.console


def test_logging_config_validation():
    with pytest.raises(ValueError):
        LoggingConfig(level="INVALID")


def test_logging_config_level_case_insensitive():
    config = LoggingConfig(level="debug")
    assert config.level == "DEBUG"


# TargetsConfig Tests
def test_targets_config_validation():
    with pytest.raises(ValueError):
        TargetsConfig()  # Empty lists
    
    config = TargetsConfig(
        keywords=["mercedes engine parts", "bmw brake pads"],
        locations=["Germany", "UK"]
    )
    assert len(config.keywords) == 2
    assert len(config.locations) == 2


def test_targets_config_invalid_types():
    with pytest.raises(ValueError):
        TargetsConfig(keywords=[1, 2], locations=["test"])
    with pytest.raises(ValueError):
        TargetsConfig(keywords=["test"], locations=[1, 2])


# ScrapingConfig Tests
@pytest.fixture
def valid_yaml_config():
    return """
    headless: true
    proxy:
        enabled: false
        urls: []
        rotation_interval: 300
        max_retries: 3
    logging:
        level: INFO
        format: "%(asctime)s - %(levelname)s - %(message)s"
        file: "scraper.log"
        console: true
    retry_limit: 3
    timeout: 10
    delay_range: [2, 5]
    max_concurrent: 3
    max_requests_per_window: 10
    time_window: 60
    base_url: "https://www.google.com"
    output_dir: "results"
    """


@pytest.fixture
def temp_config_file(valid_yaml_config):
    with TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.yaml"
        config_path.write_text(valid_yaml_config)
        yield str(config_path)


def test_scraping_config_defaults():
    config = ScrapingConfig()
    assert config.headless
    assert isinstance(config.proxy, ProxyConfig)
    assert isinstance(config.logging, LoggingConfig)
    assert config.retry_limit == 3
    assert config.timeout == 10
    assert config.delay_range == (2, 5)


def test_scraping_config_validation():
    with pytest.raises(ValueError):
        ScrapingConfig(retry_limit=0)
    with pytest.raises(ValueError):
        ScrapingConfig(timeout=0)
    with pytest.raises(ValueError):
        ScrapingConfig(delay_range=(5, 2))  # Invalid range
    with pytest.raises(ValueError):
        ScrapingConfig(base_url="invalid-url")


def test_load_from_yaml(temp_config_file):
    config = ScrapingConfig.from_yaml(temp_config_file)
    assert isinstance(config, ScrapingConfig)
    assert isinstance(config.proxy, ProxyConfig)
    assert isinstance(config.logging, LoggingConfig)


def test_ensure_paths():
    with TemporaryDirectory() as tmpdir:
        config = ScrapingConfig(output_dir=tmpdir)
        config.ensure_paths()
        assert Path(tmpdir).exists()


def test_setup_logging():
    """Test logging setup and cleanup"""
    config = ScrapingConfig()
    
    root_logger = logging.getLogger()
    
    with TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / "test.log"
        config.logging.file = str(log_file)
        
        try:
            config.setup_logging()
            
            test_logger = logging.getLogger("test")
            test_logger.info("Test message")
            
            assert log_file.exists()
            with open(log_file, 'r') as f:
                log_content = f.read()
                assert "Test message" in log_content
                
        finally:
            for handler in root_logger.handlers[:]:
                handler.close()
                root_logger.removeHandler(handler)


def test_invalid_yaml_file():
    with pytest.raises(FileNotFoundError):
        ScrapingConfig.from_yaml("nonexistent.yaml")


def test_invalid_yaml_content(config_file):
    Path(config_file).write_text("invalid: [yaml: content")
    with pytest.raises(yaml.YAMLError):
        ScrapingConfig.from_yaml(config_file)