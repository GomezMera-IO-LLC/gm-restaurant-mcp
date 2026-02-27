"""Optimized Google Maps client with caching and usage tracking"""
import googlemaps
from .cache import RestaurantCache
from .usage_tracker import UsageTracker

class OptimizedGoogleMapsClient:
    def __init__(self, api_key, cache_ttl=86400):
        """
        Initialize optimized client
        
        Args:
            api_key: Google Maps API key
            cache_ttl: Cache time-to-live in seconds (default: 24 hours)
        """
        self.client = googlemaps.Client(key=api_key)
        self.cache = RestaurantCache(ttl=cache_ttl)
        self.tracker = UsageTracker()
    
    def geocode(self, address):
        """Geocode with caching"""
        cache_key = ("geocode", {"address": address})
        cached = self.cache.get("geocode", {"address": address})
        
        if cached is not None:
            return cached
        
        result = self.client.geocode(address)
        self.cache.set("geocode", {"address": address}, result)
        self.tracker.track("geocoding")
        
        return result
    
    def places_nearby(self, location, radius, type=None, keyword=None):
        """Places nearby search with caching"""
        params = {
            "location": f"{location[0]},{location[1]}",
            "radius": radius,
            "type": type,
            "keyword": keyword
        }
        
        cached = self.cache.get("places_nearby", params)
        if cached is not None:
            return cached
        
        result = self.client.places_nearby(
            location=location,
            radius=radius,
            type=type,
            keyword=keyword
        )
        
        self.cache.set("places_nearby", params, result)
        self.tracker.track("places_nearby")
        
        return result
    
    def places(self, query, location=None, radius=None):
        """Places search with caching"""
        params = {
            "query": query,
            "location": f"{location[0]},{location[1]}" if location else None,
            "radius": radius
        }
        
        cached = self.cache.get("places_search", params)
        if cached is not None:
            return cached
        
        result = self.client.places(query=query, location=location, radius=radius)
        
        self.cache.set("places_search", params, result)
        self.tracker.track("places_search")
        
        return result
    
    def place(self, place_id, fields=None):
        """Place details with caching"""
        params = {
            "place_id": place_id,
            "fields": ",".join(sorted(fields)) if fields else None
        }
        
        cached = self.cache.get("place_details", params)
        if cached is not None:
            return cached
        
        result = self.client.place(place_id=place_id, fields=fields)
        
        self.cache.set("place_details", params, result)
        self.tracker.track("place_details")
        
        return result
    
    def directions(self, origin, destination, mode="driving"):
        """Directions with caching"""
        params = {
            "origin": origin,
            "destination": destination,
            "mode": mode
        }
        
        cached = self.cache.get("directions", params)
        if cached is not None:
            return cached
        
        result = self.client.directions(origin, destination, mode=mode)
        
        self.cache.set("directions", params, result)
        self.tracker.track("directions")
        
        return result
    
    def distance_matrix(self, origins, destinations, mode="driving"):
        """Distance matrix with caching"""
        params = {
            "origins": str(origins),
            "destinations": str(destinations),
            "mode": mode
        }
        
        cached = self.cache.get("distance_matrix", params)
        if cached is not None:
            return cached
        
        result = self.client.distance_matrix(origins, destinations, mode=mode)
        
        self.cache.set("distance_matrix", params, result)
        self.tracker.track("distance_matrix", count=len(origins) * len(destinations))
        
        return result
    
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
