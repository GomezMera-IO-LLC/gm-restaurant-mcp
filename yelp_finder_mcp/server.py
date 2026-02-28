#!/usr/bin/env python3
import os
import sys
import json
from pathlib import Path

# Import optimized client
try:
    from .optimized_client import OptimizedYelpClient
    USE_OPTIMIZED = True
except ImportError:
    USE_OPTIMIZED = False

# Global client instance
_yelp_client = None

def get_api_key():
    """Get API key from ~/.env.yelpapi file or environment variable"""
    # First try environment variable
    api_key = os.getenv("YELP_API_KEY")
    if api_key:
        return api_key
    
    # Try reading from .env.yelpapi file in user's home directory
    env_file = Path.home() / ".env.yelpapi"
    
    if env_file.exists():
        try:
            with open(env_file, 'r') as f:
                api_key = f.read().strip()
                if api_key:
                    return api_key
        except Exception as e:
            print(f"Error reading {env_file}: {e}", file=sys.stderr)
    
    raise ValueError(
        f"Yelp API key not found. Please either:\n"
        f"1. Create {env_file} with your API key, or\n"
        f"2. Set YELP_API_KEY environment variable\n\n"
        f"Get your API key at: https://www.yelp.com/developers/v3/manage_app"
    )

def get_yelp_client():
    """Initialize Yelp client with API key"""
    global _yelp_client
    
    if _yelp_client is not None:
        return _yelp_client
    
    api_key = get_api_key()
    
    if USE_OPTIMIZED:
        _yelp_client = OptimizedYelpClient(api_key, cache_ttl=86400)
    else:
        # Fallback to basic client without caching
        import requests
        class BasicYelpClient:
            def __init__(self, api_key):
                self.api_key = api_key
                self.base_url = "https://api.yelp.com/v3"
                self.headers = {"Authorization": f"Bearer {api_key}"}
            
            def search(self, **params):
                params = {k: v for k, v in params.items() if v is not None}
                response = requests.get(f"{self.base_url}/businesses/search", 
                                      headers=self.headers, params=params)
                response.raise_for_status()
                return response.json()
            
            def get_business_details(self, business_id):
                response = requests.get(f"{self.base_url}/businesses/{business_id}", 
                                      headers=self.headers)
                response.raise_for_status()
                return response.json()
            
            def get_reviews(self, business_id, limit=3):
                response = requests.get(f"{self.base_url}/businesses/{business_id}/reviews", 
                                      headers=self.headers, params={"limit": limit})
                response.raise_for_status()
                return response.json()
        
        _yelp_client = BasicYelpClient(api_key)
    
    return _yelp_client

def find_restaurants_by_location(yelp, location, radius=1500, max_results=10, 
                                 min_rating=0, cuisine_type=None, max_price=None, 
                                 open_now=None):
    """Find restaurants near a specific location"""
    params = {
        "location": location,
        "categories": "restaurants" if not cuisine_type else f"{cuisine_type},restaurants",
        "radius": min(radius, 40000),  # Yelp max is 40000m
        "limit": min(max_results, 50),  # Yelp max is 50
        "sort_by": "rating"
    }
    
    if max_price:
        params["price"] = ",".join(str(i) for i in range(1, max_price + 1))
    
    if open_now:
        params["open_now"] = True
    
    result = yelp.search(**params)
    businesses = result.get("businesses", [])
    
    # Filter by minimum rating
    if min_rating > 0:
        businesses = [b for b in businesses if b.get("rating", 0) >= min_rating]
    
    return format_restaurant_results(yelp, businesses[:max_results])

def get_restaurant_details(yelp, restaurant_name, location):
    """Get detailed information about a specific restaurant"""
    # Search for the restaurant
    search_result = yelp.search(term=restaurant_name, location=location, limit=1)
    
    if not search_result.get("businesses"):
        return {"error": f"Could not find restaurant: {restaurant_name}"}
    
    business = search_result["businesses"][0]
    business_id = business["id"]
    
    # Get detailed info
    details = yelp.get_business_details(business_id)
    
    # Try to get reviews, but handle errors gracefully
    reviews = []
    try:
        reviews_data = yelp.get_reviews(business_id, limit=3)
        reviews = reviews_data.get("reviews", [])
    except Exception as e:
        # Reviews endpoint might not be available or have restrictions
        pass
    
    # Categorize reviews
    good_reviews = [r for r in reviews if r.get("rating", 0) >= 4]
    bad_reviews = [r for r in reviews if r.get("rating", 0) <= 2]
    neutral_reviews = [r for r in reviews if 2 < r.get("rating", 0) < 4]
    
    return {
        "name": details.get("name", "Unknown"),
        "address": ", ".join(details.get("location", {}).get("display_address", [])),
        "phone": details.get("display_phone", "N/A"),
        "website": details.get("url", "N/A"),
        "rating": details.get("rating", "N/A"),
        "total_ratings": details.get("review_count", 0),
        "price_level": details.get("price", "N/A"),
        "cuisine_types": [c.get("title") for c in details.get("categories", [])],
        "yelp_url": details.get("url", "N/A"),
        "hours": format_hours(details.get("hours", [])),
        "is_closed": details.get("is_closed", False),
        "review_summary": {
            "total_reviews": len(reviews),
            "good_reviews_count": len(good_reviews),
            "bad_reviews_count": len(bad_reviews),
            "neutral_reviews_count": len(neutral_reviews)
        },
        "good_reviews": [format_review(r) for r in good_reviews] if reviews else [],
        "bad_reviews": [format_review(r) for r in bad_reviews] if reviews else [],
        "neutral_reviews": [format_review(r) for r in neutral_reviews] if reviews else [],
        "note": "Reviews may not be available due to API restrictions" if not reviews else None
    }

def compare_restaurants(yelp, restaurant_names, location):
    """Compare 2-3 restaurants side by side"""
    if not isinstance(restaurant_names, list) or len(restaurant_names) < 2 or len(restaurant_names) > 3:
        return {"error": "Please provide 2-3 restaurant names as a list"}
    
    comparison = []
    
    for restaurant_name in restaurant_names:
        search_result = yelp.search(term=restaurant_name, location=location, limit=1)
        
        if not search_result.get("businesses"):
            comparison.append({"name": restaurant_name, "error": "Not found"})
            continue
        
        business = search_result["businesses"][0]
        details = yelp.get_business_details(business["id"])
        
        comparison.append({
            "name": details.get("name", restaurant_name),
            "rating": details.get("rating", "N/A"),
            "total_ratings": details.get("review_count", 0),
            "price_level": details.get("price", "N/A"),
            "address": ", ".join(details.get("location", {}).get("display_address", [])),
            "distance": f"{business.get('distance', 0) / 1609.34:.1f} miles",
            "yelp_url": details.get("url", "N/A")
        })
    
    return {"comparison": comparison, "reference_location": location}

def get_restaurant_hours(yelp, restaurant_name, location):
    """Check restaurant hours and if it's currently open"""
    search_result = yelp.search(term=restaurant_name, location=location, limit=1)
    
    if not search_result.get("businesses"):
        return {"error": f"Could not find restaurant: {restaurant_name}"}
    
    business = search_result["businesses"][0]
    details = yelp.get_business_details(business["id"])
    
    hours_data = details.get("hours", [])
    is_open = hours_data[0].get("is_open_now", False) if hours_data else False
    
    return {
        "name": details.get("name", restaurant_name),
        "address": ", ".join(details.get("location", {}).get("display_address", [])),
        "open_now": is_open,
        "hours": format_hours(hours_data),
        "yelp_url": details.get("url", "N/A")
    }

def find_nearby_alternatives(yelp, restaurant_name, location, radius=1000, max_results=5):
    """Find similar restaurants near a specific restaurant"""
    # First find the target restaurant
    search_result = yelp.search(term=restaurant_name, location=location, limit=1)
    
    if not search_result.get("businesses"):
        return {"error": f"Could not find restaurant: {restaurant_name}"}
    
    business = search_result["businesses"][0]
    lat = business["coordinates"]["latitude"]
    lon = business["coordinates"]["longitude"]
    categories = ",".join([c["alias"] for c in business.get("categories", [])])
    
    # Search for similar restaurants nearby
    nearby_result = yelp.search(
        latitude=lat,
        longitude=lon,
        categories=categories if categories else "restaurants",
        radius=min(radius, 40000),
        limit=max_results + 1
    )
    
    # Filter out the original restaurant
    alternatives = [b for b in nearby_result.get("businesses", []) 
                   if b["id"] != business["id"]]
    
    return {
        "original_restaurant": business.get("name"),
        "alternatives": format_restaurant_results(yelp, alternatives[:max_results])
    }

def recommend_restaurants(yelp, location, preferences, max_results=5):
    """Get restaurant recommendations based on preferences"""
    cuisine = preferences.get("cuisine")
    min_rating = preferences.get("min_rating", 4.0)
    max_price = preferences.get("max_price_level", 3)
    open_now = preferences.get("open_now", False)
    attributes = preferences.get("attributes", [])
    
    params = {
        "location": location,
        "categories": f"{cuisine},restaurants" if cuisine else "restaurants",
        "limit": 50,
        "sort_by": "rating"
    }
    
    if max_price:
        params["price"] = ",".join(str(i) for i in range(1, max_price + 1))
    
    if open_now:
        params["open_now"] = True
    
    if attributes:
        params["attributes"] = ",".join(attributes)
    
    result = yelp.search(**params)
    businesses = result.get("businesses", [])
    
    # Filter by minimum rating
    filtered = [b for b in businesses if b.get("rating", 0) >= min_rating]
    
    return {
        "location": location,
        "preferences": preferences,
        "recommendations": format_restaurant_results(yelp, filtered[:max_results]),
        "total_found": len(filtered)
    }

def get_usage_stats():
    """Get API usage statistics"""
    yelp = get_yelp_client()
    
    if USE_OPTIMIZED and hasattr(yelp, 'get_usage_stats'):
        return yelp.get_usage_stats()
    else:
        return {
            "message": "Usage tracking not available. Install optimized client for tracking."
        }

def format_restaurant_results(yelp, businesses):
    """Format restaurant data"""
    formatted = []
    
    for business in businesses:
        restaurant_info = {
            "name": business.get("name", "Unknown"),
            "address": ", ".join(business.get("location", {}).get("display_address", [])),
            "rating": business.get("rating", "N/A"),
            "total_ratings": business.get("review_count", 0),
            "price_level": business.get("price", "N/A"),
            "cuisine_types": [c.get("title") for c in business.get("categories", [])],
            "distance": f"{business.get('distance', 0) / 1609.34:.1f} miles" if business.get('distance') else "N/A",
            "phone": business.get("display_phone", "N/A"),
            "yelp_url": business.get("url", "N/A"),
            "is_closed": business.get("is_closed", False)
        }
        
        formatted.append(restaurant_info)
    
    return formatted

def format_review(review):
    """Format a single review"""
    return {
        "author": review.get("user", {}).get("name", "Anonymous"),
        "rating": review.get("rating", "N/A"),
        "text": review.get("text", ""),
        "time": review.get("time_created", "")
    }

def format_hours(hours_data):
    """Format hours data"""
    if not hours_data:
        return []
    
    hours = hours_data[0].get("open", [])
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    formatted = []
    
    for day_idx, day_name in enumerate(days):
        day_hours = [h for h in hours if h.get("day") == day_idx]
        if day_hours:
            times = []
            for h in day_hours:
                start = h.get("start", "")
                end = h.get("end", "")
                times.append(f"{start[:2]}:{start[2:]} - {end[:2]}:{end[2:]}")
            formatted.append(f"{day_name}: {', '.join(times)}")
        else:
            formatted.append(f"{day_name}: Closed")
    
    return formatted

def send_response(response):
    """Send JSON-RPC response to stdout"""
    print(json.dumps(response), flush=True)

def handle_request(request):
    """Handle incoming JSON-RPC request"""
    try:
        yelp = get_yelp_client()
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "yelp-finder-mcp",
                        "version": "0.1.0"
                    }
                }
            }
        
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": [
                        {
                            "name": "find_restaurants_by_location",
                            "description": "Find restaurants near a specific location using Yelp",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "location": {
                                        "type": "string",
                                        "description": "Location to search (e.g., 'New York, NY' or '123 Main St')"
                                    },
                                    "radius": {
                                        "type": "number",
                                        "description": "Search radius in meters (default: 1500, max: 40000)",
                                        "default": 1500
                                    },
                                    "max_results": {
                                        "type": "number",
                                        "description": "Maximum number of results (default: 10, max: 50)",
                                        "default": 10
                                    },
                                    "min_rating": {
                                        "type": "number",
                                        "description": "Minimum rating filter (0-5, default: 0)",
                                        "default": 0
                                    },
                                    "cuisine_type": {
                                        "type": "string",
                                        "description": "Cuisine type (e.g., 'italian', 'chinese', 'mexican', 'japanese')"
                                    },
                                    "max_price": {
                                        "type": "number",
                                        "description": "Maximum price level (1-4: 1=$, 2=$$, 3=$$$, 4=$$$$)"
                                    },
                                    "open_now": {
                                        "type": "boolean",
                                        "description": "Only show restaurants open now"
                                    }
                                },
                                "required": ["location"]
                            }
                        },
                        {
                            "name": "get_restaurant_details",
                            "description": "Get detailed information about a specific restaurant",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "restaurant_name": {
                                        "type": "string",
                                        "description": "Name of the restaurant"
                                    },
                                    "location": {
                                        "type": "string",
                                        "description": "Location context (e.g., 'New York, NY')"
                                    }
                                },
                                "required": ["restaurant_name", "location"]
                            }
                        },
                        {
                            "name": "compare_restaurants",
                            "description": "Compare 2-3 restaurants side by side",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "restaurant_names": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "List of 2-3 restaurant names"
                                    },
                                    "location": {
                                        "type": "string",
                                        "description": "Reference location"
                                    }
                                },
                                "required": ["restaurant_names", "location"]
                            }
                        },
                        {
                            "name": "get_restaurant_hours",
                            "description": "Check if a restaurant is open now and get its hours",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "restaurant_name": {
                                        "type": "string",
                                        "description": "Name of the restaurant"
                                    },
                                    "location": {
                                        "type": "string",
                                        "description": "Location context"
                                    }
                                },
                                "required": ["restaurant_name", "location"]
                            }
                        },
                        {
                            "name": "find_nearby_alternatives",
                            "description": "Find similar restaurants near a specific restaurant",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "restaurant_name": {
                                        "type": "string",
                                        "description": "Name of the reference restaurant"
                                    },
                                    "location": {
                                        "type": "string",
                                        "description": "Location context"
                                    },
                                    "radius": {
                                        "type": "number",
                                        "description": "Search radius in meters (default: 1000)",
                                        "default": 1000
                                    },
                                    "max_results": {
                                        "type": "number",
                                        "description": "Maximum number of alternatives (default: 5)",
                                        "default": 5
                                    }
                                },
                                "required": ["restaurant_name", "location"]
                            }
                        },
                        {
                            "name": "recommend_restaurants",
                            "description": "Get restaurant recommendations based on preferences",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "location": {
                                        "type": "string",
                                        "description": "Location to search"
                                    },
                                    "preferences": {
                                        "type": "object",
                                        "description": "Preferences: cuisine, min_rating, max_price_level, open_now, attributes"
                                    },
                                    "max_results": {
                                        "type": "number",
                                        "description": "Maximum recommendations (default: 5)",
                                        "default": 5
                                    }
                                },
                                "required": ["location", "preferences"]
                            }
                        },
                        {
                            "name": "get_usage_stats",
                            "description": "Get API usage statistics and cache performance",
                            "inputSchema": {
                                "type": "object",
                                "properties": {},
                                "required": []
                            }
                        }
                    ]
                }
            }
        
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if tool_name == "find_restaurants_by_location":
                result = find_restaurants_by_location(
                    yelp,
                    arguments.get("location"),
                    arguments.get("radius", 1500),
                    arguments.get("max_results", 10),
                    arguments.get("min_rating", 0),
                    arguments.get("cuisine_type"),
                    arguments.get("max_price"),
                    arguments.get("open_now")
                )
            elif tool_name == "get_restaurant_details":
                result = get_restaurant_details(
                    yelp,
                    arguments.get("restaurant_name"),
                    arguments.get("location")
                )
            elif tool_name == "compare_restaurants":
                result = compare_restaurants(
                    yelp,
                    arguments.get("restaurant_names"),
                    arguments.get("location")
                )
            elif tool_name == "get_restaurant_hours":
                result = get_restaurant_hours(
                    yelp,
                    arguments.get("restaurant_name"),
                    arguments.get("location")
                )
            elif tool_name == "find_nearby_alternatives":
                result = find_nearby_alternatives(
                    yelp,
                    arguments.get("restaurant_name"),
                    arguments.get("location"),
                    arguments.get("radius", 1000),
                    arguments.get("max_results", 5)
                )
            elif tool_name == "recommend_restaurants":
                result = recommend_restaurants(
                    yelp,
                    arguments.get("location"),
                    arguments.get("preferences", {}),
                    arguments.get("max_results", 5)
                )
            elif tool_name == "get_usage_stats":
                result = get_usage_stats()
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Unknown tool: {tool_name}"
                    }
                }
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                }
            }
        
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
    
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }

def main():
    """Main loop for MCP server"""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        
        try:
            request = json.loads(line)
            response = handle_request(request)
            send_response(response)
        except json.JSONDecodeError as e:
            send_response({
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {str(e)}"
                }
            })
        except Exception as e:
            send_response({
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            })

if __name__ == "__main__":
    main()
