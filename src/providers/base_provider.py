from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

logger = logging.getLogger(__name__)

class ProviderError(Exception):
    """Base exception for provider errors"""
    pass

class BaseProvider(ABC):
    """
    Abstract base provider class
    
    All providers must implement:
    - fetch() method
    - validate_response() method
    """
    
    def __init__(self, name: str):
        self.name = name
        self.client = httpx.AsyncClient(timeout=30.0)
        logger.info(f"Initialized {name} provider")
    
    @abstractmethod
    async def fetch(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Fetch data from provider
        
        Args:
            query: Search query
            **kwargs: Provider-specific parameters
            
        Returns:
            Standardized response dictionary
        """
        pass
    
    @abstractmethod
    def validate_response(self, response: Any) -> bool:
        """
        Validate provider response
        
        Args:
            response: Raw provider response
            
        Returns:
            True if valid, False otherwise
        """
        pass
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(httpx.RequestError)
    )
    async def _make_request(
        self,
        url: str,
        method: str = "GET",
        **kwargs
    ) -> httpx.Response:
        """
        Make HTTP request with retry logic
        """
        try:
            if method == "GET":
                response = await self.client.get(url, **kwargs)
            elif method == "POST":
                response = await self.client.post(url, **kwargs)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response
        
        except httpx.HTTPStatusError as e:
            logger.error(f"{self.name} HTTP error: {e.response.status_code}")
            raise ProviderError(f"HTTP {e.response.status_code}: {str(e)}")
        
        except httpx.RequestError as e:
            logger.error(f"{self.name} request error: {str(e)}")
            raise ProviderError(f"Request failed: {str(e)}")
    
    def _create_response(
        self,
        success: bool,
        data: Any = None,
        error: str = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create standardized response"""
        return {
            "provider": self.name,
            "success": success,
            "data": data,
            "error": error,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()