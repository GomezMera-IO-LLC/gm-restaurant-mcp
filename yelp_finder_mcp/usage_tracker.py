"""Track API usage for Yelp Fusion API"""
import json
import time
from pathlib import Path
from datetime import datetime

class YelpUsageTracker:
    def __init__(self, usage_file=".cache_yelp/usage.json"):
        """Initialize usage tracker"""
        self.usage_file = Path(usage_file)
        self.usage_file.parent.mkdir(exist_ok=True)
        self._load_usage()
        
        # Yelp Fusion API limits (free tier)
        self.daily_limit = 500  # 500 calls per day
    
    def _load_usage(self):
        """Load usage data"""
        if self.usage_file.exists():
            with open(self.usage_file, 'r') as f:
                self.usage = json.load(f)
        else:
            self.usage = {
                "current_date": datetime.now().strftime("%Y-%m-%d"),
                "calls": 0
            }
    
    def _save_usage(self):
        """Save usage data"""
        with open(self.usage_file, 'w') as f:
            json.dump(self.usage, f, indent=2)
    
    def _check_day_reset(self):
        """Reset counters if new day"""
        current_date = datetime.now().strftime("%Y-%m-%d")
        if current_date != self.usage["current_date"]:
            self.usage = {
                "current_date": current_date,
                "calls": 0
            }
            self._save_usage()
    
    def track(self, count=1):
        """Track API usage"""
        self._check_day_reset()
        self.usage["calls"] += count
        self._save_usage()
    
    def get_usage_summary(self):
        """Get current day usage summary"""
        self._check_day_reset()
        
        remaining_calls = max(0, self.daily_limit - self.usage["calls"])
        usage_percent = (self.usage["calls"] / self.daily_limit) * 100
        
        return {
            "date": self.usage["current_date"],
            "total_api_calls": self.usage["calls"],
            "daily_limit": self.daily_limit,
            "remaining_calls": remaining_calls,
            "usage_percentage": f"{usage_percent:.1f}%",
            "within_limit": self.usage["calls"] <= self.daily_limit
        }
    
    def get_warning(self):
        """Get warning if approaching daily limit"""
        if self.usage["calls"] >= self.daily_limit:
            return "⚠️ WARNING: You've reached your daily API limit (500 calls)!"
        elif self.usage["calls"] > self.daily_limit * 0.9:
            return "⚠️ CAUTION: You've used 90%+ of your daily API limit."
        return None
