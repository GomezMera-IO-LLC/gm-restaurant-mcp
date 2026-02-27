"""Track API usage to stay within Google Maps free tier"""
import json
import time
from pathlib import Path
from datetime import datetime

class UsageTracker:
    def __init__(self, usage_file=".cache/usage.json"):
        """Initialize usage tracker"""
        self.usage_file = Path(usage_file)
        self.usage_file.parent.mkdir(exist_ok=True)
        self._load_usage()
        
        # Google Maps API pricing (per 1000 requests after $200 credit)
        self.pricing = {
            "places_nearby": 0.032,      # $32 per 1000
            "place_details": 0.017,      # $17 per 1000
            "directions": 0.005,         # $5 per 1000
            "geocoding": 0.005,          # $5 per 1000
            "distance_matrix": 0.005,    # $5 per 1000 elements
            "places_search": 0.032       # $32 per 1000
        }
        
        # Free tier: $200 credit per month
        self.monthly_credit = 200.0
    
    def _load_usage(self):
        """Load usage data"""
        if self.usage_file.exists():
            with open(self.usage_file, 'r') as f:
                self.usage = json.load(f)
        else:
            self.usage = {
                "current_month": datetime.now().strftime("%Y-%m"),
                "calls": {},
                "total_cost": 0.0
            }
    
    def _save_usage(self):
        """Save usage data"""
        with open(self.usage_file, 'w') as f:
            json.dump(self.usage, f, indent=2)
    
    def _check_month_reset(self):
        """Reset counters if new month"""
        current_month = datetime.now().strftime("%Y-%m")
        if current_month != self.usage["current_month"]:
            self.usage = {
                "current_month": current_month,
                "calls": {},
                "total_cost": 0.0
            }
            self._save_usage()
    
    def track(self, api_name, count=1):
        """
        Track API usage
        
        Args:
            api_name: Name of the API (e.g., 'places_nearby')
            count: Number of calls (default: 1)
        """
        self._check_month_reset()
        
        if api_name not in self.usage["calls"]:
            self.usage["calls"][api_name] = 0
        
        self.usage["calls"][api_name] += count
        
        # Calculate cost
        if api_name in self.pricing:
            cost = (count / 1000) * self.pricing[api_name]
            self.usage["total_cost"] += cost
        
        self._save_usage()
    
    def get_usage_summary(self):
        """Get current month usage summary"""
        self._check_month_reset()
        
        total_calls = sum(self.usage["calls"].values())
        remaining_credit = max(0, self.monthly_credit - self.usage["total_cost"])
        
        # Estimate remaining calls with current credit
        avg_cost_per_call = self.usage["total_cost"] / total_calls if total_calls > 0 else 0.015
        estimated_remaining_calls = int(remaining_credit / avg_cost_per_call) if avg_cost_per_call > 0 else 0
        
        return {
            "month": self.usage["current_month"],
            "total_api_calls": total_calls,
            "estimated_cost": f"${self.usage['total_cost']:.2f}",
            "free_credit_remaining": f"${remaining_credit:.2f}",
            "estimated_remaining_calls": estimated_remaining_calls,
            "calls_by_api": self.usage["calls"],
            "within_free_tier": self.usage["total_cost"] <= self.monthly_credit
        }
    
    def get_warning(self):
        """Get warning if approaching free tier limit"""
        if self.usage["total_cost"] > self.monthly_credit * 0.9:
            return "⚠️ WARNING: You've used 90%+ of your free tier credit this month!"
        elif self.usage["total_cost"] > self.monthly_credit * 0.75:
            return "⚠️ CAUTION: You've used 75%+ of your free tier credit this month."
        return None
