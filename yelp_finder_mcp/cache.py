"""Simple caching system to reduce API calls"""
import json
import time
import hashlib
from pathlib import Path

class YelpCache:
    def __init__(self, cache_dir=".cache_yelp", ttl=86400):  # 24 hour default TTL
        """
        Initialize cache
        
        Args:
            cache_dir: Directory to store cache files
            ttl: Time to live in seconds (default: 86400 = 24 hours)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl = ttl
        self.stats_file = self.cache_dir / "stats.json"
        self._load_stats()
    
    def _load_stats(self):
        """Load usage statistics"""
        if self.stats_file.exists():
            with open(self.stats_file, 'r') as f:
                self.stats = json.load(f)
        else:
            self.stats = {
                "api_calls_saved": 0,
                "api_calls_made": 0,
                "last_reset": time.time()
            }
    
    def _save_stats(self):
        """Save usage statistics"""
        with open(self.stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def _get_cache_key(self, operation, params):
        """Generate cache key from operation and parameters"""
        param_str = json.dumps(params, sort_keys=True)
        key_str = f"{operation}:{param_str}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, operation, params):
        """Get cached result if available and not expired"""
        cache_key = self._get_cache_key(operation, params)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r') as f:
                cached = json.load(f)
            
            if time.time() - cached['timestamp'] > self.ttl:
                cache_file.unlink()
                return None
            
            self.stats["api_calls_saved"] += 1
            self._save_stats()
            return cached['data']
        except Exception:
            return None
    
    def set(self, operation, params, data):
        """Cache API result"""
        cache_key = self._get_cache_key(operation, params)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        cached = {
            'timestamp': time.time(),
            'operation': operation,
            'data': data
        }
        
        with open(cache_file, 'w') as f:
            json.dump(cached, f)
        
        self.stats["api_calls_made"] += 1
        self._save_stats()
    
    def get_stats(self):
        """Get cache statistics"""
        total_calls = self.stats["api_calls_saved"] + self.stats["api_calls_made"]
        if total_calls == 0:
            hit_rate = 0
        else:
            hit_rate = (self.stats["api_calls_saved"] / total_calls) * 100
        
        return {
            "api_calls_made": self.stats["api_calls_made"],
            "api_calls_saved": self.stats["api_calls_saved"],
            "cache_hit_rate": f"{hit_rate:.1f}%"
        }
    
    def clear(self):
        """Clear all cache files"""
        for cache_file in self.cache_dir.glob("*.json"):
            if cache_file.name != "stats.json":
                cache_file.unlink()
    
    def clear_old(self, max_age_days=7):
        """Clear cache files older than specified days"""
        max_age_seconds = max_age_days * 86400
        current_time = time.time()
        
        for cache_file in self.cache_dir.glob("*.json"):
            if cache_file.name == "stats.json":
                continue
            
            try:
                with open(cache_file, 'r') as f:
                    cached = json.load(f)
                
                if current_time - cached['timestamp'] > max_age_seconds:
                    cache_file.unlink()
            except Exception:
                pass
