# src/models/ad_data.py
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional, List
from urllib.parse import urlparse
from enum import Enum, auto


class AdPosition(Enum):
    """Enumeration for ad positions"""
    TOP = auto()
    SIDEBAR = auto()
    BOTTOM = auto()
    UNKNOWN = auto()

    @classmethod
    def from_int(cls, value: int) -> 'AdPosition':
        """Convert integer position to enum value"""
        position_map = {
            1: cls.TOP,
            2: cls.SIDEBAR,
            3: cls.BOTTOM
        }
        return position_map.get(value, cls.UNKNOWN)


class URLValidationError(ValueError):
    """Custom exception for URL validation errors"""
    pass


@dataclass
class AdData:
    """
    Data model for European auto parts advertisement information.
    
    Attributes:
        keyword (str): Search keyword that triggered the ad
        location (str): Geographic location targeted
        website_url (str): Landing page URL
        title (str): Ad title
        description (Optional[str]): Ad description text
        phone_number (Optional[str]): Contact phone number
        price (Optional[str]): Price information if available
        email (Optional[str]): Contact email address
        social_links (Dict[str, str]): Dictionary of social media links
        meta_tags (Dict[str, str]): Dictionary of meta information
        ad_position (AdPosition): Position of ad in results
        timestamp (str): ISO format timestamp of when ad was scraped
        product_categories (List[str]): Categories of auto parts
        brand (Optional[str]): Car brand (Mercedes, BMW, etc.)
        model (Optional[str]): Car model
        part_condition (Optional[str]): Condition of parts (new, used, etc.)
    """
    
    keyword: str
    location: str
    website_url: str
    title: str
    description: Optional[str] = None
    phone_number: Optional[str] = None
    price: Optional[str] = None
    email: Optional[str] = None
    social_links: Dict[str, str] = field(default_factory=dict)
    meta_tags: Dict[str, str] = field(default_factory=dict)
    ad_position: AdPosition = field(default=AdPosition.UNKNOWN)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    product_categories: List[str] = field(default_factory=list)
    brand: Optional[str] = None
    model: Optional[str] = None
    part_condition: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate and clean data after initialization"""
        if not self.website_url:
            raise URLValidationError("website_url cannot be empty")
        if not self.title:
            raise ValueError("title cannot be empty")
        if not self.keyword:
            raise ValueError("keyword cannot be empty")
        if not self.location:
            raise ValueError("location cannot be empty")
            
        # Clean and validate URL
        self.website_url = self.website_url.strip()
        self._validate_url(self.website_url)
        
        # Clean other fields
        self.title = self.title.strip()
        if self.description:
            self.description = self.description.strip()
        if self.phone_number:
            self.phone_number = self.clean_phone_number(self.phone_number)
        if self.email:
            self.email = self.email.lower().strip()

    @staticmethod
    def _validate_url(url: str) -> None:
        """
        Validate URL format and structure
        
        Args:
            url: URL string to validate
            
        Raises:
            URLValidationError: If URL is invalid
        """
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                raise URLValidationError("Invalid URL format: Missing scheme or domain")
            if not result.scheme in ['http', 'https']:
                raise URLValidationError(f"Invalid URL scheme: {result.scheme}")
        except Exception as e:
            raise URLValidationError(f"Invalid URL: {str(e)}")

    @staticmethod
    def clean_phone_number(phone: str) -> str:
        """Clean and format phone number"""
        # Remove all non-numeric characters
        cleaned = ''.join(filter(str.isdigit, phone))
        if not cleaned:
            return phone  # Return original if no digits found
        return cleaned

    def is_valid(self) -> bool:
        """
        Check if ad data meets minimum validity requirements
        
        Returns:
            bool: True if ad data is valid, False otherwise
        """
        return all([
            bool(self.website_url),
            bool(self.title),
            bool(self.keyword),
            bool(self.location)
        ])

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert instance to dictionary representation
        
        Returns:
            Dict[str, Any]: Dictionary of ad data
        """
        return {
            'keyword': self.keyword,
            'location': self.location,
            'website_url': self.website_url,
            'title': self.title,
            'description': self.description,
            'phone_number': self.phone_number,
            'price': self.price,
            'email': self.email,
            'social_links': self.social_links,
            'meta_tags': self.meta_tags,
            'ad_position': self.ad_position.name,
            'timestamp': self.timestamp,
            'product_categories': self.product_categories,
            'brand': self.brand,
            'model': self.model,
            'part_condition': self.part_condition
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AdData:
        """
        Create instance from dictionary
        
        Args:
            data: Dictionary containing ad data
            
        Returns:
            AdData: New instance with provided data
        """
        # Handle ad_position conversion if it's an integer
        if 'ad_position' in data:
            if isinstance(data['ad_position'], int):
                data['ad_position'] = AdPosition.from_int(data['ad_position'])
            elif isinstance(data['ad_position'], str):
                data['ad_position'] = AdPosition[data['ad_position']]
                
        return cls(**data)

    def __str__(self) -> str:
        """String representation of the ad"""
        return f"{self.title} - {self.website_url} ({self.ad_position.name})"