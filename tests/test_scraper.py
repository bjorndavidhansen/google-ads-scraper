# tests/test_scraper.py
import pytest
from src.config import ScrapingConfig
from src.models.ad_data import AdData
from google_ads_scraper import EnhancedGoogleAdsScraper

@pytest.fixture
def scraper():
    config = ScrapingConfig()
    return EnhancedGoogleAdsScraper(config)

@pytest.mark.asyncio
async def test_scraper_initialization(scraper):
    assert isinstance(scraper, EnhancedGoogleAdsScraper)
    assert isinstance(scraper.config, ScrapingConfig)

@pytest.mark.asyncio
async def test_scraper_basic_scrape(scraper):
    results = await scraper.scrape()
    assert isinstance(results, list)
    # More assertions to be added as implementation grows