import httpx
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import asyncio
from backend.core.config import settings


class MarketplaceProvider(ABC):
    """Abstract base class for marketplace providers."""
    
    @abstractmethod
    async def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search for items on the marketplace."""
        pass
    
    @abstractmethod
    def calculate_relevance_score(self, item: Dict[str, Any], query: str) -> float:
        """Calculate relevance score for an item."""
        pass


class EbayProvider(MarketplaceProvider):
    """eBay marketplace provider."""
    
    def __init__(self):
        self.app_id = settings.EBAY_APP_ID
        self.base_url = "https://svcs.ebay.com/services/search/FindingService/v1"
    
    async def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search eBay for items."""
        if not self.app_id:
            return self._mock_search(query, max_results)
        
        params = {
            "OPERATION-NAME": "findItemsByKeywords",
            "SERVICE-VERSION": "1.0.0",
            "SECURITY-APPNAME": self.app_id,
            "RESPONSE-DATA-FORMAT": "JSON",
            "keywords": query,
            "paginationInput.entriesPerPage": max_results,
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                items = []
                search_result = data.get("findItemsByKeywordsResponse", [{}])[0]
                search_items = search_result.get("searchResult", [{}])[0].get("item", [])
                
                for item in search_items:
                    items.append({
                        "provider": "ebay",
                        "item_name": item.get("title", [""])[0],
                        "item_url": item.get("viewItemURL", [""])[0],
                        "price": float(item.get("sellingStatus", [{}])[0].get("currentPrice", [{"__value__": 0}])[0].get("__value__", 0)),
                        "currency": item.get("sellingStatus", [{}])[0].get("currentPrice", [{"@currencyId": "USD"}])[0].get("@currencyId", "USD"),
                        "condition": item.get("condition", [{"conditionDisplayName": ["Unknown"]}])[0].get("conditionDisplayName", ["Unknown"])[0],
                        "image_url": item.get("galleryURL", [""])[0],
                        "metadata": {
                            "item_id": item.get("itemId", [""])[0],
                            "location": item.get("location", [""])[0],
                        }
                    })
                
                return items
        except Exception as e:
            print(f"eBay search error: {e}")
            return self._mock_search(query, max_results)
    
    def _mock_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Mock search results when API is not configured."""
        return [
            {
                "provider": "ebay",
                "item_name": f"{query} - eBay Item {i+1}",
                "item_url": f"https://ebay.com/item/{i}",
                "price": 29.99 + (i * 10),
                "currency": "USD",
                "condition": "New" if i % 2 == 0 else "Used",
                "image_url": f"https://via.placeholder.com/150?text=Item{i+1}",
                "metadata": {"mock": True}
            }
            for i in range(min(max_results, 5))
        ]
    
    def calculate_relevance_score(self, item: Dict[str, Any], query: str) -> float:
        """Calculate relevance score based on title match."""
        query_words = set(query.lower().split())
        title_words = set(item.get("item_name", "").lower().split())
        
        if not query_words or not title_words:
            return 0.0
        
        intersection = query_words.intersection(title_words)
        score = len(intersection) / len(query_words)
        
        # Boost for exact match
        if query.lower() in item.get("item_name", "").lower():
            score += 0.3
        
        return min(score, 1.0)


class AmazonProvider(MarketplaceProvider):
    """Amazon marketplace provider."""
    
    def __init__(self):
        self.access_key = settings.AMAZON_ACCESS_KEY
        self.secret_key = settings.AMAZON_SECRET_KEY
    
    async def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search Amazon for items (mock implementation)."""
        # Note: Amazon Product Advertising API requires complex signing
        # This is a simplified mock implementation
        return self._mock_search(query, max_results)
    
    def _mock_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Mock search results."""
        return [
            {
                "provider": "amazon",
                "item_name": f"{query} - Amazon Product {i+1}",
                "item_url": f"https://amazon.com/dp/MOCK{i}",
                "price": 39.99 + (i * 15),
                "currency": "USD",
                "condition": "New",
                "availability": "In Stock" if i % 3 != 0 else "Limited",
                "image_url": f"https://via.placeholder.com/150?text=Amazon{i+1}",
                "metadata": {"mock": True, "prime": i % 2 == 0}
            }
            for i in range(min(max_results, 5))
        ]
    
    def calculate_relevance_score(self, item: Dict[str, Any], query: str) -> float:
        """Calculate relevance score."""
        query_words = set(query.lower().split())
        title_words = set(item.get("item_name", "").lower().split())
        
        if not query_words or not title_words:
            return 0.0
        
        intersection = query_words.intersection(title_words)
        score = len(intersection) / len(query_words)
        
        # Boost for prime items
        if item.get("metadata", {}).get("prime"):
            score += 0.1
        
        return min(score, 1.0)


class StockXProvider(MarketplaceProvider):
    """StockX marketplace provider."""
    
    def __init__(self):
        self.api_key = settings.STOCKX_API_KEY
        self.base_url = "https://api.stockx.com/v1"
    
    async def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search StockX for items (mock implementation)."""
        return self._mock_search(query, max_results)
    
    def _mock_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Mock search results for sneakers and collectibles."""
        return [
            {
                "provider": "stockx",
                "item_name": f"{query} - StockX Item {i+1}",
                "item_url": f"https://stockx.com/item-{i}",
                "price": 150.00 + (i * 50),
                "currency": "USD",
                "condition": "New",
                "availability": "Available",
                "image_url": f"https://via.placeholder.com/150?text=StockX{i+1}",
                "metadata": {
                    "mock": True,
                    "lowest_ask": 150.00 + (i * 50),
                    "highest_bid": 140.00 + (i * 50)
                }
            }
            for i in range(min(max_results, 5))
        ]
    
    def calculate_relevance_score(self, item: Dict[str, Any], query: str) -> float:
        """Calculate relevance score."""
        query_words = set(query.lower().split())
        title_words = set(item.get("item_name", "").lower().split())
        
        if not query_words or not title_words:
            return 0.0
        
        intersection = query_words.intersection(title_words)
        return len(intersection) / len(query_words)


class GrailedProvider(MarketplaceProvider):
    """Grailed marketplace provider for fashion/streetwear."""
    
    def __init__(self):
        self.api_key = settings.GRAILED_API_KEY
        self.base_url = "https://api.grailed.com/api"
    
    async def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search Grailed for items (mock implementation)."""
        return self._mock_search(query, max_results)
    
    def _mock_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Mock search results for fashion items."""
        conditions = ["New with tags", "Gently used", "Used"]
        return [
            {
                "provider": "grailed",
                "item_name": f"{query} - Grailed Item {i+1}",
                "item_url": f"https://grailed.com/listings/{i}",
                "price": 75.00 + (i * 25),
                "currency": "USD",
                "condition": conditions[i % len(conditions)],
                "availability": "Available",
                "image_url": f"https://via.placeholder.com/150?text=Grailed{i+1}",
                "metadata": {
                    "mock": True,
                    "designer": f"Designer {i % 3}",
                    "size": f"Size {['S', 'M', 'L', 'XL'][i % 4]}"
                }
            }
            for i in range(min(max_results, 5))
        ]
    
    def calculate_relevance_score(self, item: Dict[str, Any], query: str) -> float:
        """Calculate relevance score."""
        query_words = set(query.lower().split())
        title_words = set(item.get("item_name", "").lower().split())
        
        if not query_words or not title_words:
            return 0.0
        
        intersection = query_words.intersection(title_words)
        return len(intersection) / len(query_words)


class MarketplaceService:
    """Unified marketplace service with pluggable provider registry."""
    
    def __init__(self):
        self.providers: Dict[str, MarketplaceProvider] = {
            "ebay": EbayProvider(),
            "amazon": AmazonProvider(),
            "stockx": StockXProvider(),
            "grailed": GrailedProvider(),
        }
    
    async def search_all_providers(
        self,
        query: str,
        provider_names: Optional[List[str]] = None,
        max_results_per_provider: int = 10
    ) -> List[Dict[str, Any]]:
        """Search across multiple marketplace providers."""
        if provider_names is None:
            provider_names = list(self.providers.keys())
        
        # Filter to valid providers
        valid_providers = [
            name for name in provider_names 
            if name in self.providers
        ]
        
        # Execute searches in parallel
        tasks = [
            self.providers[name].search(query, max_results_per_provider)
            for name in valid_providers
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten results and calculate relevance scores
        all_items = []
        for provider_name, provider_results in zip(valid_providers, results):
            if isinstance(provider_results, Exception):
                print(f"Error from {provider_name}: {provider_results}")
                continue
            
            for item in provider_results:
                # Calculate relevance score
                provider = self.providers[provider_name]
                relevance_score = provider.calculate_relevance_score(item, query)
                item['relevance_score'] = relevance_score
                all_items.append(item)
        
        # Sort by relevance score and price
        all_items.sort(key=lambda x: (x.get('relevance_score', 0), -x.get('price', float('inf'))), reverse=True)
        
        return all_items


# Global marketplace service instance
marketplace_service = MarketplaceService()
