#!/usr/bin/env python3
import os
import sys
import json
import googlemaps
from pathlib import Path

# Import optimized client
try:
    from .optimized_client import OptimizedGoogleMapsClient
    USE_OPTIMIZED = True
except ImportError:
    USE_OPTIMIZED = False

# Global client instance
_gmaps_client = None

def get_api_key():
    """Get API key from ~/.env.googleapi file or environment variable (cross-platform)"""
    # First try environment variable
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if api_key:
        return api_key
    
    # Try reading from .env.googleapi file in user's home directory
    # Path.home() works on Windows, macOS, and Linux
    env_file = Path.home() / ".env.googleapi"
    
    if env_file.exists():
        try:
            with open(env_file, 'r') as f:
                api_key = f.read().strip()
                if api_key:
                    return api_key
        except Exception as e:
            print(f"Error reading {env_file}: {e}", file=sys.stderr)
    
    # Provide helpful error message with correct path for user's OS
    raise ValueError(
        f"Google Maps API key not found. Please either:\n"
        f"1. Create {env_file} with your API key, or\n"
        f"2. Set GOOGLE_MAPS_API_KEY environment variable\n\n"
        f"On Windows: {Path.home() / '.env.googleapi'}\n"
        f"On macOS/Linux: ~/.env.googleapi"
    )

def get_gmaps_client():
    """Initialize Google Maps client with API key from file or environment"""
    global _gmaps_client
    
    if _gmaps_client is not None:
        return _gmaps_client
    
    api_key = get_api_key()
    
    if USE_OPTIMIZED:
        _gmaps_client = OptimizedGoogleMapsClient(api_key, cache_ttl=86400)  # 24 hour cache
    else:
        _gmaps_client = googlemaps.Client(key=api_key)
    
    return _gmaps_client

def find_restaurants_by_location(gmaps, location, radius=1500, max_results=10, min_rating=0, cuisine_type=None, max_price_level=None):
    """Find restaurants near a specific location"""
    # Geocode the location to get coordinates
    geocode_result = gmaps.geocode(location)
    if not geocode_result:
        return {"error": f"Could not find location: {location}"}
    
    lat_lng = geocode_result[0]['geometry']['location']
    
    # Build search query with cuisine type if specified
    keyword = cuisine_type if cuisine_type else None
    
    # Search for restaurants using coordinates
    places_result = gmaps.places_nearby(
        location=(lat_lng['lat'], lat_lng['lng']),
        radius=radius,
        type="restaurant",
        keyword=keyword
    )
    
    # Filter by minimum rating and max price level if specified
    results = places_result.get("results", [])
    if min_rating > 0:
        results = [r for r in results if r.get("rating", 0) >= min_rating]
    if max_price_level is not None:
        results = [r for r in results if r.get("price_level") is not None and r.get("price_level") <= max_price_level]
    
    return format_restaurant_results(gmaps, results[:max_results])

def find_restaurants_along_route(gmaps, origin, destination, detour_distance=2000, max_results=10, min_rating=0, cuisine_type=None, max_price_level=None):
    """Find restaurants along a route between two locations"""
    directions = gmaps.directions(origin, destination, mode="driving")
    
    if not directions:
        return {"error": "No route found between locations"}
    
    route = directions[0]
    legs = route["legs"]
    
    all_restaurants = []
    seen_place_ids = set()
    
    for leg in legs:
        for step in leg["steps"][:5]:
            step_location = step["end_location"]
            location_str = f"{step_location['lat']},{step_location['lng']}"
            
            # Build search with cuisine type if specified
            keyword = cuisine_type if cuisine_type else None
            
            places_result = gmaps.places_nearby(
                location=location_str,
                radius=detour_distance,
                type="restaurant",
                keyword=keyword
            )
            
            for place in places_result.get("results", []):
                place_id = place.get("place_id")
                if place_id and place_id not in seen_place_ids:
                    # Apply filters
                    rating = place.get("rating", 0)
                    price_level = place.get("price_level")
                    
                    # Check rating filter
                    if min_rating > 0 and rating < min_rating:
                        continue
                    
                    # Check price filter
                    if max_price_level is not None and (price_level is None or price_level > max_price_level):
                        continue
                    
                    seen_place_ids.add(place_id)
                    all_restaurants.append(place)
                    
                    if len(all_restaurants) >= max_results:
                        break
            
            if len(all_restaurants) >= max_results:
                break
        
        if len(all_restaurants) >= max_results:
            break
    
    return format_restaurant_results(gmaps, all_restaurants[:max_results])

def get_restaurant_details(gmaps, restaurant_name, location):
    """Get detailed information about a specific restaurant with categorized reviews"""
    # Search for the restaurant
    search_query = f"{restaurant_name} {location}"
    geocode_result = gmaps.geocode(location)
    
    if not geocode_result:
        return {"error": f"Could not find location: {location}"}
    
    lat_lng = geocode_result[0]['geometry']['location']
    
    # Search for the specific restaurant
    places_result = gmaps.places(
        query=search_query,
        location=(lat_lng['lat'], lat_lng['lng']),
        radius=5000
    )
    
    if not places_result.get("results"):
        return {"error": f"Could not find restaurant: {restaurant_name}"}
    
    # Get the first result (most relevant)
    place = places_result["results"][0]
    place_id = place.get("place_id")
    
    # Get detailed information with all reviews
    details = gmaps.place(place_id, fields=[
        "name", "rating", "user_ratings_total", "price_level",
        "type", "vicinity", "formatted_address", "formatted_phone_number",
        "website", "url", "reviews", "opening_hours", "geometry"
    ])
    
    result = details.get("result", {})
    place_types = place.get("types", [])
    
    # Categorize reviews
    reviews = result.get("reviews", [])
    good_reviews = [r for r in reviews if r.get("rating", 0) >= 4]
    bad_reviews = [r for r in reviews if r.get("rating", 0) <= 2]
    neutral_reviews = [r for r in reviews if 2 < r.get("rating", 0) < 4]
    
    # Format reviews
    def format_review(review):
        return {
            "author": review.get("author_name", "Anonymous"),
            "rating": review.get("rating", "N/A"),
            "text": review.get("text", ""),
            "time": review.get("relative_time_description", "")
        }
    
    restaurant_details = {
        "name": result.get("name", "Unknown"),
        "address": result.get("formatted_address", result.get("vicinity", "N/A")),
        "phone": result.get("formatted_phone_number", "N/A"),
        "website": result.get("website", "N/A"),
        "rating": result.get("rating", "N/A"),
        "total_ratings": result.get("user_ratings_total", 0),
        "price_level": get_price_display(result.get("price_level")),
        "cuisine_types": [t.replace("_", " ").title() for t in place_types 
                        if t not in ["restaurant", "food", "point_of_interest", "establishment"]],
        "google_maps_url": result.get("url", "N/A"),
        "hours": result.get("opening_hours", {}).get("weekday_text", []),
        "review_summary": {
            "total_reviews": len(reviews),
            "good_reviews_count": len(good_reviews),
            "bad_reviews_count": len(bad_reviews),
            "neutral_reviews_count": len(neutral_reviews)
        },
        "good_reviews": [format_review(r) for r in good_reviews[:5]],
        "bad_reviews": [format_review(r) for r in bad_reviews[:5]],
        "neutral_reviews": [format_review(r) for r in neutral_reviews[:3]]
    }
    
    return restaurant_details

def compare_restaurants(gmaps, restaurant_names, location):
    """Compare 2-3 restaurants side by side"""
    if not isinstance(restaurant_names, list) or len(restaurant_names) < 2 or len(restaurant_names) > 3:
        return {"error": "Please provide 2-3 restaurant names as a list"}
    
    comparison = []
    geocode_result = gmaps.geocode(location)
    
    if not geocode_result:
        return {"error": f"Could not find location: {location}"}
    
    user_location = geocode_result[0]['geometry']['location']
    
    for restaurant_name in restaurant_names:
        search_query = f"{restaurant_name} {location}"
        places_result = gmaps.places(
            query=search_query,
            location=(user_location['lat'], user_location['lng']),
            radius=10000
        )
        
        if not places_result.get("results"):
            comparison.append({"name": restaurant_name, "error": "Not found"})
            continue
        
        place = places_result["results"][0]
        place_id = place.get("place_id")
        
        details = gmaps.place(place_id, fields=[
            "name", "rating", "user_ratings_total", "price_level",
            "vicinity", "formatted_address", "url", "geometry"
        ])
        
        result = details.get("result", {})
        restaurant_location = result.get("geometry", {}).get("location", {})
        
        # Calculate distance
        distance = gmaps.distance_matrix(
            origins=[(user_location['lat'], user_location['lng'])],
            destinations=[(restaurant_location.get('lat'), restaurant_location.get('lng'))],
            mode="driving"
        )
        
        distance_text = "N/A"
        duration_text = "N/A"
        if distance.get("rows"):
            element = distance["rows"][0]["elements"][0]
            if element.get("status") == "OK":
                distance_text = element["distance"]["text"]
                duration_text = element["duration"]["text"]
        
        comparison.append({
            "name": result.get("name", restaurant_name),
            "rating": result.get("rating", "N/A"),
            "total_ratings": result.get("user_ratings_total", 0),
            "price_level": get_price_display(result.get("price_level")),
            "address": result.get("vicinity", "N/A"),
            "distance": distance_text,
            "drive_time": duration_text,
            "google_maps_url": result.get("url", "N/A")
        })
    
    return {"comparison": comparison, "reference_location": location}

def get_restaurant_hours(gmaps, restaurant_name, location):
    """Check restaurant hours and if it's currently open"""
    search_query = f"{restaurant_name} {location}"
    geocode_result = gmaps.geocode(location)
    
    if not geocode_result:
        return {"error": f"Could not find location: {location}"}
    
    lat_lng = geocode_result[0]['geometry']['location']
    
    places_result = gmaps.places(
        query=search_query,
        location=(lat_lng['lat'], lat_lng['lng']),
        radius=5000
    )
    
    if not places_result.get("results"):
        return {"error": f"Could not find restaurant: {restaurant_name}"}
    
    place = places_result["results"][0]
    place_id = place.get("place_id")
    
    details = gmaps.place(place_id, fields=[
        "name", "opening_hours", "formatted_address", "url"
    ])
    
    result = details.get("result", {})
    opening_hours = result.get("opening_hours", {})
    
    return {
        "name": result.get("name", restaurant_name),
        "address": result.get("formatted_address", "N/A"),
        "open_now": opening_hours.get("open_now", "Unknown"),
        "hours": opening_hours.get("weekday_text", []),
        "google_maps_url": result.get("url", "N/A")
    }

def get_directions(gmaps, restaurant_name, location, origin, mode="driving"):
    """Get detailed directions to a restaurant"""
    search_query = f"{restaurant_name} {location}"
    geocode_result = gmaps.geocode(location)
    
    if not geocode_result:
        return {"error": f"Could not find location: {location}"}
    
    lat_lng = geocode_result[0]['geometry']['location']
    
    places_result = gmaps.places(
        query=search_query,
        location=(lat_lng['lat'], lat_lng['lng']),
        radius=5000
    )
    
    if not places_result.get("results"):
        return {"error": f"Could not find restaurant: {restaurant_name}"}
    
    place = places_result["results"][0]
    place_id = place.get("place_id")
    
    details = gmaps.place(place_id, fields=["name", "formatted_address", "geometry"])
    result = details.get("result", {})
    destination_address = result.get("formatted_address")
    
    # Get directions
    directions = gmaps.directions(origin, destination_address, mode=mode)
    
    if not directions:
        return {"error": "Could not find route"}
    
    route = directions[0]
    leg = route["legs"][0]
    
    steps = []
    for step in leg["steps"]:
        steps.append({
            "instruction": step["html_instructions"].replace("<b>", "").replace("</b>", "").replace("<div style=\"font-size:0.9em\">", " - ").replace("</div>", ""),
            "distance": step["distance"]["text"],
            "duration": step["duration"]["text"]
        })
    
    return {
        "restaurant": result.get("name"),
        "destination": destination_address,
        "origin": origin,
        "mode": mode,
        "total_distance": leg["distance"]["text"],
        "total_duration": leg["duration"]["text"],
        "steps": steps
    }

def find_nearby_alternatives(gmaps, restaurant_name, location, radius=1000, max_results=5):
    """Find similar restaurants near a specific restaurant"""
    search_query = f"{restaurant_name} {location}"
    geocode_result = gmaps.geocode(location)
    
    if not geocode_result:
        return {"error": f"Could not find location: {location}"}
    
    lat_lng = geocode_result[0]['geometry']['location']
    
    places_result = gmaps.places(
        query=search_query,
        location=(lat_lng['lat'], lat_lng['lng']),
        radius=5000
    )
    
    if not places_result.get("results"):
        return {"error": f"Could not find restaurant: {restaurant_name}"}
    
    place = places_result["results"][0]
    place_id = place.get("place_id")
    
    details = gmaps.place(place_id, fields=["name", "geometry", "type"])
    result = details.get("result", {})
    restaurant_location = result.get("geometry", {}).get("location", {})
    
    # Search for nearby restaurants
    nearby_result = gmaps.places_nearby(
        location=(restaurant_location['lat'], restaurant_location['lng']),
        radius=radius,
        type="restaurant"
    )
    
    # Filter out the original restaurant
    alternatives = [r for r in nearby_result.get("results", []) if r.get("place_id") != place_id]
    
    return {
        "original_restaurant": result.get("name"),
        "alternatives": format_restaurant_results(gmaps, alternatives[:max_results])
    }

def extract_popular_dishes(gmaps, restaurant_name, location):
    """Extract most-mentioned dishes from reviews"""
    search_query = f"{restaurant_name} {location}"
    geocode_result = gmaps.geocode(location)
    
    if not geocode_result:
        return {"error": f"Could not find location: {location}"}
    
    lat_lng = geocode_result[0]['geometry']['location']
    
    places_result = gmaps.places(
        query=search_query,
        location=(lat_lng['lat'], lat_lng['lng']),
        radius=5000
    )
    
    if not places_result.get("results"):
        return {"error": f"Could not find restaurant: {restaurant_name}"}
    
    place = places_result["results"][0]
    place_id = place.get("place_id")
    
    details = gmaps.place(place_id, fields=["name", "reviews"])
    result = details.get("result", {})
    reviews = result.get("reviews", [])
    
    # Extract food mentions from reviews (simple keyword extraction)
    food_mentions = {}
    common_foods = [
        "pizza", "burger", "steak", "chicken", "pasta", "salad", "sandwich", "tacos", 
        "burrito", "sushi", "ramen", "pho", "pad thai", "curry", "noodles", "rice",
        "wings", "fries", "soup", "seafood", "shrimp", "salmon", "tuna", "lobster",
        "dessert", "cake", "pie", "ice cream", "tiramisu", "cheesecake", "brownie",
        "appetizer", "nachos", "quesadilla", "enchilada", "fajitas", "ribs", "brisket",
        "pork", "beef", "lamb", "duck", "fish", "crab", "oyster", "clam", "mussels",
        "bread", "garlic bread", "breadsticks", "rolls", "biscuits", "pancakes", "waffles",
        "eggs", "bacon", "sausage", "hash browns", "omelet", "french toast"
    ]
    
    for review in reviews:
        text = review.get("text", "").lower()
        for food in common_foods:
            if food in text:
                food_mentions[food] = food_mentions.get(food, 0) + 1
    
    # Sort by mentions
    popular_dishes = sorted(food_mentions.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        "restaurant": result.get("name", restaurant_name),
        "popular_dishes": [{"dish": dish, "mentions": count} for dish, count in popular_dishes],
        "total_reviews_analyzed": len(reviews)
    }

def check_restaurant_features(gmaps, restaurant_name, location):
    """Check restaurant features including reservations, dietary options, and ambiance"""
    search_query = f"{restaurant_name} {location}"
    geocode_result = gmaps.geocode(location)
    
    if not geocode_result:
        return {"error": f"Could not find location: {location}"}
    
    lat_lng = geocode_result[0]['geometry']['location']
    
    places_result = gmaps.places(
        query=search_query,
        location=(lat_lng['lat'], lat_lng['lng']),
        radius=5000
    )
    
    if not places_result.get("results"):
        return {"error": f"Could not find restaurant: {restaurant_name}"}
    
    place = places_result["results"][0]
    place_id = place.get("place_id")
    
    details = gmaps.place(place_id, fields=[
        "name", "website", "type", "reviews", "formatted_address", "url"
    ])
    
    result = details.get("result", {})
    place_types = place.get("types", [])
    reviews = result.get("reviews", [])
    
    # Analyze reviews for features
    review_text = " ".join([r.get("text", "").lower() for r in reviews])
    
    # Check for dietary options
    dietary_options = {
        "vegetarian": "vegetarian" in review_text or "veggie" in review_text,
        "vegan": "vegan" in review_text,
        "gluten_free": "gluten free" in review_text or "gluten-free" in review_text or "celiac" in review_text,
        "halal": "halal" in review_text,
        "kosher": "kosher" in review_text
    }
    
    # Check for ambiance tags
    ambiance = {
        "romantic": "romantic" in review_text or "date night" in review_text or "anniversary" in review_text,
        "family_friendly": "family" in review_text or "kids" in review_text or "children" in review_text,
        "casual": "casual" in review_text,
        "upscale": "upscale" in review_text or "fancy" in review_text or "elegant" in review_text or "fine dining" in review_text,
        "outdoor_seating": "outdoor" in review_text or "patio" in review_text or "outside" in review_text
    }
    
    # Check for reservations
    website = result.get("website", "")
    accepts_reservations = (
        "reservation" in review_text or 
        "opentable" in website.lower() or 
        "resy" in website.lower() or
        "book" in review_text
    )
    
    return {
        "restaurant": result.get("name", restaurant_name),
        "address": result.get("formatted_address", "N/A"),
        "website": website if website else "N/A",
        "accepts_reservations": "Likely" if accepts_reservations else "Unknown (check website)",
        "dietary_options": {k: v for k, v in dietary_options.items() if v},
        "ambiance": {k: v for k, v in ambiance.items() if v},
        "google_maps_url": result.get("url", "N/A")
    }

def get_peak_hours(gmaps, restaurant_name, location):
    """Get popular times for a restaurant"""
    search_query = f"{restaurant_name} {location}"
    geocode_result = gmaps.geocode(location)
    
    if not geocode_result:
        return {"error": f"Could not find location: {location}"}
    
    lat_lng = geocode_result[0]['geometry']['location']
    
    places_result = gmaps.places(
        query=search_query,
        location=(lat_lng['lat'], lat_lng['lng']),
        radius=5000
    )
    
    if not places_result.get("results"):
        return {"error": f"Could not find restaurant: {restaurant_name}"}
    
    place = places_result["results"][0]
    place_id = place.get("place_id")
    
    # Note: Google Places API doesn't directly provide popular times via the Python client
    # This would require the Places API (New) or web scraping
    # For now, we'll provide general guidance based on restaurant type
    
    details = gmaps.place(place_id, fields=["name", "type", "formatted_address"])
    result = details.get("result", {})
    
    return {
        "restaurant": result.get("name", restaurant_name),
        "address": result.get("formatted_address", "N/A"),
        "note": "Peak hours data not available via API. Generally, restaurants are busiest:",
        "typical_peak_times": {
            "lunch": "12:00 PM - 1:30 PM (weekdays)",
            "dinner": "6:00 PM - 8:00 PM (all days)",
            "weekend_brunch": "10:00 AM - 1:00 PM (Saturday & Sunday)"
        },
        "recommendation": "Call ahead or check Google Maps app for live 'Popular Times' data"
    }

def recommend_restaurants(gmaps, location, preferences, max_results=5):
    """Get restaurant recommendations based on preferences"""
    geocode_result = gmaps.geocode(location)
    
    if not geocode_result:
        return {"error": f"Could not find location: {location}"}
    
    lat_lng = geocode_result[0]['geometry']['location']
    
    # Parse preferences
    cuisine = preferences.get("cuisine")
    min_rating = preferences.get("min_rating", 4.0)
    max_price = preferences.get("max_price_level", 3)
    dietary = preferences.get("dietary", [])
    ambiance = preferences.get("ambiance", [])
    
    # Build keyword from preferences
    keywords = []
    if cuisine:
        keywords.append(cuisine)
    if dietary:
        keywords.extend(dietary)
    if ambiance:
        keywords.extend(ambiance)
    
    keyword = " ".join(keywords) if keywords else None
    
    # Search for restaurants
    places_result = gmaps.places_nearby(
        location=(lat_lng['lat'], lat_lng['lng']),
        radius=5000,
        type="restaurant",
        keyword=keyword
    )
    
    # Filter results
    results = places_result.get("results", [])
    filtered = []
    
    for place in results:
        rating = place.get("rating", 0)
        price_level = place.get("price_level")
        
        if rating >= min_rating:
            if price_level is None or price_level <= max_price:
                filtered.append(place)
    
    # Sort by rating
    filtered.sort(key=lambda x: x.get("rating", 0), reverse=True)
    
    recommendations = format_restaurant_results(gmaps, filtered[:max_results])
    
    return {
        "location": location,
        "preferences": preferences,
        "recommendations": recommendations,
        "total_found": len(filtered)
    }

def get_review_link(gmaps, restaurant_name, location):
    """Get the direct link to leave a review for a restaurant"""
    search_query = f"{restaurant_name} {location}"
    geocode_result = gmaps.geocode(location)
    
    if not geocode_result:
        return {"error": f"Could not find location: {location}"}
    
    lat_lng = geocode_result[0]['geometry']['location']
    
    places_result = gmaps.places(
        query=search_query,
        location=(lat_lng['lat'], lat_lng['lng']),
        radius=5000
    )
    
    if not places_result.get("results"):
        return {"error": f"Could not find restaurant: {restaurant_name}"}
    
    place = places_result["results"][0]
    place_id = place.get("place_id")
    
    details = gmaps.place(place_id, fields=[
        "name", "formatted_address", "url", "place_id"
    ])
    
    result = details.get("result", {})
    
    # Construct review URL
    # Google Maps review URL format
    review_url = f"https://search.google.com/local/writereview?placeid={place_id}"
    
    return {
        "restaurant": result.get("name", restaurant_name),
        "address": result.get("formatted_address", "N/A"),
        "google_maps_url": result.get("url", "N/A"),
        "review_url": review_url,
        "place_id": place_id,
        "instructions": "Click the review_url to open Google Maps and leave your review. You'll need to be signed in to your Google account."
    }

def get_usage_stats():
    """Get API usage statistics and cache performance"""
    gmaps = get_gmaps_client()
    
    if USE_OPTIMIZED and hasattr(gmaps, 'get_usage_stats'):
        stats = gmaps.get_usage_stats()
        return stats
    else:
        return {
            "message": "Usage tracking not available. Install optimized client for tracking.",
            "recommendation": "Restart the MCP server to enable caching and usage tracking."
        }

def format_restaurant_results(gmaps, places):
    """Format restaurant data with reviews, type, price, and links"""
    formatted = []
    
    for place in places:
        place_id = place.get("place_id")
        place_types = place.get("types", [])
        
        details = gmaps.place(place_id, fields=[
            "name", "rating", "user_ratings_total", "price_level",
            "type", "vicinity", "url", "reviews", "geometry"
        ])
        
        result = details.get("result", {})
        
        restaurant_info = {
            "name": result.get("name", "Unknown"),
            "address": result.get("vicinity", "N/A"),
            "rating": result.get("rating", "N/A"),
            "total_ratings": result.get("user_ratings_total", 0),
            "price_level": get_price_display(result.get("price_level")),
            "cuisine_types": [t.replace("_", " ").title() for t in place_types 
                            if t not in ["restaurant", "food", "point_of_interest", "establishment"]],
            "google_maps_url": result.get("url", "N/A"),
            "reviews": []
        }
        
        reviews = result.get("reviews", [])[:3]
        for review in reviews:
            restaurant_info["reviews"].append({
                "author": review.get("author_name", "Anonymous"),
                "rating": review.get("rating", "N/A"),
                "text": review.get("text", "")[:200] + ("..." if len(review.get("text", "")) > 200 else ""),
                "time": review.get("relative_time_description", "")
            })
        
        formatted.append(restaurant_info)
    
    return formatted

def get_price_display(price_level):
    """Convert price level to dollar signs"""
    if price_level is None:
        return "N/A"
    return "$" * price_level

def send_response(response):
    """Send JSON-RPC response to stdout"""
    print(json.dumps(response), flush=True)

def handle_request(request):
    """Handle incoming JSON-RPC request"""
    try:
        gmaps = get_gmaps_client()
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
                        "name": "restaurant-finder-mcp",
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
                            "description": "Find restaurants near a specific location (address, city, or coordinates)",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "location": {
                                        "type": "string",
                                        "description": "Location to search (e.g., '123 Main St, New York' or 'Times Square')"
                                    },
                                    "radius": {
                                        "type": "number",
                                        "description": "Search radius in meters (default: 1500)",
                                        "default": 1500
                                    },
                                    "max_results": {
                                        "type": "number",
                                        "description": "Maximum number of results to return (default: 10)",
                                        "default": 10
                                    },
                                    "min_rating": {
                                        "type": "number",
                                        "description": "Minimum rating filter (0-5, default: 0 for no filter)",
                                        "default": 0
                                    },
                                    "cuisine_type": {
                                        "type": "string",
                                        "description": "Filter by cuisine type (e.g., 'chinese', 'italian', 'mexican', 'japanese', 'american', 'indian', 'thai', 'greek', 'french', 'korean', 'vietnamese', 'mediterranean', 'latin', 'breakfast', 'lunch', 'dinner', 'brunch')"
                                    },
                                    "max_price_level": {
                                        "type": "number",
                                        "description": "Maximum price level (1=$ budget, 2=$$ moderate, 3=$$$ expensive, 4=$$$$ very expensive). Filters to show only restaurants at or below this price level."
                                    }
                                },
                                "required": ["location"]
                            }
                        },
                        {
                            "name": "find_restaurants_along_route",
                            "description": "Find restaurants along a route between two locations",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "origin": {
                                        "type": "string",
                                        "description": "Starting location (address or place name)"
                                    },
                                    "destination": {
                                        "type": "string",
                                        "description": "Ending location (address or place name)"
                                    },
                                    "detour_distance": {
                                        "type": "number",
                                        "description": "Maximum detour distance in meters from route (default: 2000)",
                                        "default": 2000
                                    },
                                    "max_results": {
                                        "type": "number",
                                        "description": "Maximum number of results to return (default: 10)",
                                        "default": 10
                                    },
                                    "min_rating": {
                                        "type": "number",
                                        "description": "Minimum rating filter (0-5, default: 0 for no filter)",
                                        "default": 0
                                    },
                                    "cuisine_type": {
                                        "type": "string",
                                        "description": "Filter by cuisine type (e.g., 'chinese', 'italian', 'mexican', 'japanese', 'american', 'indian', 'thai', 'greek', 'french', 'korean', 'vietnamese', 'mediterranean', 'latin', 'breakfast', 'lunch', 'dinner', 'brunch')"
                                    },
                                    "max_price_level": {
                                        "type": "number",
                                        "description": "Maximum price level (1=$ budget, 2=$$ moderate, 3=$$$ expensive, 4=$$$$ very expensive). Filters to show only restaurants at or below this price level."
                                    }
                                },
                                "required": ["origin", "destination"]
                            }
                        },
                        {
                            "name": "get_restaurant_details",
                            "description": "Get detailed information about a specific restaurant including categorized good and bad reviews",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "restaurant_name": {
                                        "type": "string",
                                        "description": "Name of the restaurant"
                                    },
                                    "location": {
                                        "type": "string",
                                        "description": "Location context (e.g., 'Wesley Chapel, FL') to help find the right restaurant"
                                    }
                                },
                                "required": ["restaurant_name", "location"]
                            }
                        },
                        {
                            "name": "compare_restaurants",
                            "description": "Compare 2-3 restaurants side by side with ratings, prices, reviews, and distance",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "restaurant_names": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "List of 2-3 restaurant names to compare"
                                    },
                                    "location": {
                                        "type": "string",
                                        "description": "Reference location for comparison (e.g., 'Wesley Chapel, FL')"
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
                                        "description": "Location context (e.g., 'Wesley Chapel, FL')"
                                    }
                                },
                                "required": ["restaurant_name", "location"]
                            }
                        },
                        {
                            "name": "get_directions",
                            "description": "Get detailed driving or walking directions to a restaurant",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "restaurant_name": {
                                        "type": "string",
                                        "description": "Name of the restaurant"
                                    },
                                    "location": {
                                        "type": "string",
                                        "description": "Location context (e.g., 'Wesley Chapel, FL')"
                                    },
                                    "origin": {
                                        "type": "string",
                                        "description": "Starting location (address or place name)"
                                    },
                                    "mode": {
                                        "type": "string",
                                        "description": "Travel mode: 'driving', 'walking', 'bicycling', or 'transit' (default: driving)",
                                        "default": "driving"
                                    }
                                },
                                "required": ["restaurant_name", "location", "origin"]
                            }
                        },
                        {
                            "name": "find_nearby_alternatives",
                            "description": "Find similar restaurants near a specific restaurant (useful if your first choice is full)",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "restaurant_name": {
                                        "type": "string",
                                        "description": "Name of the reference restaurant"
                                    },
                                    "location": {
                                        "type": "string",
                                        "description": "Location context (e.g., 'Wesley Chapel, FL')"
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
                            "name": "extract_popular_dishes",
                            "description": "Extract most-mentioned dishes from restaurant reviews",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "restaurant_name": {
                                        "type": "string",
                                        "description": "Name of the restaurant"
                                    },
                                    "location": {
                                        "type": "string",
                                        "description": "Location context (e.g., 'Wesley Chapel, FL')"
                                    }
                                },
                                "required": ["restaurant_name", "location"]
                            }
                        },
                        {
                            "name": "check_restaurant_features",
                            "description": "Check restaurant features including reservations, dietary options (vegetarian, vegan, gluten-free, halal, kosher), and ambiance (romantic, family-friendly, casual, upscale, outdoor seating)",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "restaurant_name": {
                                        "type": "string",
                                        "description": "Name of the restaurant"
                                    },
                                    "location": {
                                        "type": "string",
                                        "description": "Location context (e.g., 'Wesley Chapel, FL')"
                                    }
                                },
                                "required": ["restaurant_name", "location"]
                            }
                        },
                        {
                            "name": "get_peak_hours",
                            "description": "Get information about when a restaurant is typically busiest",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "restaurant_name": {
                                        "type": "string",
                                        "description": "Name of the restaurant"
                                    },
                                    "location": {
                                        "type": "string",
                                        "description": "Location context (e.g., 'Wesley Chapel, FL')"
                                    }
                                },
                                "required": ["restaurant_name", "location"]
                            }
                        },
                        {
                            "name": "recommend_restaurants",
                            "description": "Get AI-powered restaurant recommendations based on user preferences",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "location": {
                                        "type": "string",
                                        "description": "Location to search (e.g., 'Wesley Chapel, FL')"
                                    },
                                    "preferences": {
                                        "type": "object",
                                        "description": "User preferences object with optional fields: cuisine (string), min_rating (number 0-5), max_price_level (number 1-4), dietary (array of strings like ['vegetarian', 'gluten-free']), ambiance (array of strings like ['romantic', 'family-friendly'])"
                                    },
                                    "max_results": {
                                        "type": "number",
                                        "description": "Maximum number of recommendations (default: 5)",
                                        "default": 5
                                    }
                                },
                                "required": ["location", "preferences"]
                            }
                        },
                        {
                            "name": "get_review_link",
                            "description": "Get the direct link to leave a review for a restaurant on Google Maps",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "restaurant_name": {
                                        "type": "string",
                                        "description": "Name of the restaurant"
                                    },
                                    "location": {
                                        "type": "string",
                                        "description": "Location context (e.g., 'Wesley Chapel, FL')"
                                    }
                                },
                                "required": ["restaurant_name", "location"]
                            }
                        },
                        {
                            "name": "get_usage_stats",
                            "description": "Get API usage statistics, cache performance, and free tier status",
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
                    gmaps,
                    arguments.get("location"),
                    arguments.get("radius", 1500),
                    arguments.get("max_results", 10),
                    arguments.get("min_rating", 0),
                    arguments.get("cuisine_type"),
                    arguments.get("max_price_level")
                )
            elif tool_name == "find_restaurants_along_route":
                result = find_restaurants_along_route(
                    gmaps,
                    arguments.get("origin"),
                    arguments.get("destination"),
                    arguments.get("detour_distance", 2000),
                    arguments.get("max_results", 10),
                    arguments.get("min_rating", 0),
                    arguments.get("cuisine_type"),
                    arguments.get("max_price_level")
                )
            elif tool_name == "get_restaurant_details":
                result = get_restaurant_details(
                    gmaps,
                    arguments.get("restaurant_name"),
                    arguments.get("location")
                )
            elif tool_name == "compare_restaurants":
                result = compare_restaurants(
                    gmaps,
                    arguments.get("restaurant_names"),
                    arguments.get("location")
                )
            elif tool_name == "get_restaurant_hours":
                result = get_restaurant_hours(
                    gmaps,
                    arguments.get("restaurant_name"),
                    arguments.get("location")
                )
            elif tool_name == "get_directions":
                result = get_directions(
                    gmaps,
                    arguments.get("restaurant_name"),
                    arguments.get("location"),
                    arguments.get("origin"),
                    arguments.get("mode", "driving")
                )
            elif tool_name == "find_nearby_alternatives":
                result = find_nearby_alternatives(
                    gmaps,
                    arguments.get("restaurant_name"),
                    arguments.get("location"),
                    arguments.get("radius", 1000),
                    arguments.get("max_results", 5)
                )
            elif tool_name == "extract_popular_dishes":
                result = extract_popular_dishes(
                    gmaps,
                    arguments.get("restaurant_name"),
                    arguments.get("location")
                )
            elif tool_name == "check_restaurant_features":
                result = check_restaurant_features(
                    gmaps,
                    arguments.get("restaurant_name"),
                    arguments.get("location")
                )
            elif tool_name == "get_peak_hours":
                result = get_peak_hours(
                    gmaps,
                    arguments.get("restaurant_name"),
                    arguments.get("location")
                )
            elif tool_name == "recommend_restaurants":
                result = recommend_restaurants(
                    gmaps,
                    arguments.get("location"),
                    arguments.get("preferences", {}),
                    arguments.get("max_results", 5)
                )
            elif tool_name == "get_review_link":
                result = get_review_link(
                    gmaps,
                    arguments.get("restaurant_name"),
                    arguments.get("location")
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
