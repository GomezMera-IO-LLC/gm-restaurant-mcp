# Yelp Finder MCP - Quick Start Guide

## Installation

1. **Install dependencies:**
   ```bash
   pip install requests
   ```

2. **Get your Yelp API key:**
   - Visit: https://www.yelp.com/developers/v3/manage_app
   - Create a free account and app
   - Copy your API key

3. **Setup API key:**
   ```bash
   # macOS/Linux
   ./setup_yelp_key.sh
   
   # Windows
   setup_yelp_key.bat
   ```

## Available Tools

### 1. Find Restaurants by Location
Search for restaurants near a specific location.

```python
find_restaurants_by_location(
    location="New York, NY",
    radius=1500,           # meters
    max_results=10,
    min_rating=4.0,
    cuisine_type="italian",
    max_price=3,           # 1-4 scale
    open_now=True
)
```

### 2. Get Restaurant Details
Get detailed information including reviews.

```python
get_restaurant_details(
    restaurant_name="Joe's Pizza",
    location="New York, NY"
)
```

### 3. Compare Restaurants
Compare 2-3 restaurants side by side.

```python
compare_restaurants(
    restaurant_names=["Joe's Pizza", "John's Pizza", "Lombardi's"],
    location="New York, NY"
)
```

### 4. Get Restaurant Hours
Check if a restaurant is open now.

```python
get_restaurant_hours(
    restaurant_name="Joe's Pizza",
    location="New York, NY"
)
```

### 5. Find Nearby Alternatives
Find similar restaurants nearby.

```python
find_nearby_alternatives(
    restaurant_name="Joe's Pizza",
    location="New York, NY",
    radius=1000,
    max_results=5
)
```

### 6. Get Recommendations
Get personalized restaurant recommendations.

```python
recommend_restaurants(
    location="New York, NY",
    preferences={
        "cuisine": "italian",
        "min_rating": 4.0,
        "max_price_level": 3,
        "open_now": True,
        "attributes": ["hot_and_new", "reservation"]
    },
    max_results=5
)
```

### 7. Get Usage Stats
Monitor your API usage and cache performance.

```python
get_usage_stats()
```

## Running the Server

```bash
# Run directly
python -m yelp_finder_mcp.server

# Or if installed as package
yelp-finder-mcp
```

## Key Differences from Google Maps

| Feature | Yelp | Google Maps |
|---------|------|-------------|
| Free Tier | 500 calls/day | $200 credit/month |
| Credit Card | Not required | Required |
| Reviews | 3 per business | 5 per place |
| Photos | More user photos | Street view + photos |
| Business Info | More detailed | More locations |

## Tips for Staying Within Free Tier

1. **Use caching** - Results cached for 24 hours
2. **Limit results** - Request only what you need
3. **Monitor usage** - Check `get_usage_stats` regularly
4. **Batch operations** - Compare multiple restaurants at once

## Example Usage

```python
# Find top-rated Italian restaurants open now
results = find_restaurants_by_location(
    location="San Francisco, CA",
    cuisine_type="italian",
    min_rating=4.5,
    max_price=3,
    open_now=True,
    max_results=5
)

# Get details for a specific restaurant
details = get_restaurant_details(
    restaurant_name="Tony's Pizza Napoletana",
    location="San Francisco, CA"
)

# Compare your top choices
comparison = compare_restaurants(
    restaurant_names=[
        "Tony's Pizza Napoletana",
        "Flour + Water",
        "SPQR"
    ],
    location="San Francisco, CA"
)
```

## Troubleshooting

**API key not found:**
```bash
echo "YOUR_API_KEY" > ~/.env.yelpapi
```

**Daily limit exceeded:**
- Wait until midnight UTC
- Check cache settings
- Optimize queries

**No results found:**
- Try broader search radius
- Remove strict filters
- Check location spelling

## Next Steps

- Read [YELP_API_GUIDE.md](YELP_API_GUIDE.md) for detailed API information
- Check Yelp's [official documentation](https://www.yelp.com/developers/documentation/v3)
- Monitor your usage with `get_usage_stats`

## Support

- Yelp Developer Support: https://www.yelp.com/developers/support
- API Documentation: https://www.yelp.com/developers/documentation/v3
