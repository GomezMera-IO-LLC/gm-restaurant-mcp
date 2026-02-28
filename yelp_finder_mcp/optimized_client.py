"""Optimized Yelp client with caching and usage tracking"""
import requests
from .cache import YelpCache
from .usage_tracker import YelpUsageTracker

class OptimizedYelpClient:
    def __init__(self, api_key, cache_ttl=86400):
        """
        Initialize optimized Yelp client
        
        Args:
            api_key: Yelp Fusion API key
            cache_ttl: Cache time-to-live in seconds (default: 24 hours)
        """
        self.api_key = api_key
        self.base_url = "https://api.yelp.com/v3"
        self.headers = {"Authorization": f"Bearer {api_key}"}
        self.cache = YelpCache(ttl=cache_ttl)
        self.tracker = YelpUsageTracker()
    
    def _make_request(self, endpoint, params, operation_name):
        """Make API request with caching"""
        cache_params = {**params, "endpoint": endpoint}
        cached = self.cache.get(operation_name, cache_params)
        
        if cached is not None:
            return cached
        
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        result = response.json()
        self.cache.set(operation_name, cache_params, result)
        self.tracker.track()
        
        return result
    
    def search(self, location=None, latitude=None, longitude=None, term=None, 
               categories=None, radius=None, limit=10, sort_by="best_match", 
               price=None, open_now=None, attributes=None):
        """Search for businesses"""
        params = {
            "location": location,
            "latitude": latitude,
            "longitude": longitude,
            "term": term,
            "categories": categories,
            "radius": radius,
            "limit": limit,
            "sort_by": sort_by,
            "price": price,
            "open_now": open_now,
            "attributes": attributes
        }
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        return self._make_request("businesses/search", params, "business_search")
    
    def get_business_details(self, business_id):
        """Get detailed business information"""
        params = {"business_id": business_id}
        return self._make_request(f"businesses/{business_id}", {}, "business_details")
    
    def get_reviews(self, business_id, limit=3):
        """Get business reviews"""
        params = {"limit": limit}
        return self._make_request(f"businesses/{business_id}/reviews", params, "business_reviews")
    
    def get_usage_stats(self):
        """Get usage statistics"""
        cache_stats = self.cache.get_stats()
        usage_summary = self.tracker.get_usage_summary()
        warning = self.tracker.get_warning()
        
        return {
            "cache": cache_stats,
            "usage": usage_summary,
            "warning": warning
        }
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache.clear()
    
    def clear_old_cache(self, max_age_days=7):
        """Clear cache older than specified days"""
        self.cache.clear_old(max_age_days)
