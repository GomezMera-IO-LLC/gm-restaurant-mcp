# Yelp Finder MCP Server

A Model Context Protocol (MCP) server for restaurant discovery using the Yelp Fusion API.

## Features

- 🔍 Search restaurants by location
- ⭐ Get detailed restaurant information with reviews
- 📊 Compare multiple restaurants side-by-side
- 🕐 Check restaurant hours and availability
- 🎯 Find nearby alternatives
- 💡 Get personalized recommendations
- 📈 Track API usage and cache performance

## Quick Start

### 1. Get Your Free Yelp API Key

Visit https://www.yelp.com/developers/v3/manage_app and create a free app to get your API key.

**It's completely free:**
- ✅ No credit card required
- ✅ 500 API calls per day
- ✅ Never expires

### 2. Setup

```bash
# Install dependencies
pip install requests

# Setup your API key (choose your platform)
./setup_yelp_key.sh          # macOS/Linux
setup_yelp_key.bat           # Windows CMD
setup_yelp_key.ps1           # Windows PowerShell
```

### 3. Configure in Kiro (Optional)

The MCP configuration is already set up in `.kiro/settings/mcp.json`. The server will automatically connect when you open Kiro.

To manually configure or modify, see [MCP_CONFIGURATION_GUIDE.md](MCP_CONFIGURATION_GUIDE.md).

### 4. Run the Server (Standalone)

```bash
python -m yelp_finder_mcp.server
```

Or use it directly in Kiro - it will connect automatically!

## Available Tools

### find_restaurants_by_location
Find restaurants near a specific location with filters for cuisine, rating, price, and more.

### get_restaurant_details
Get comprehensive information about a specific restaurant including categorized reviews.

### compare_restaurants
Compare 2-3 restaurants side by side with ratings, prices, and distances.

### get_restaurant_hours
Check if a restaurant is currently open and view its hours.

### find_nearby_alternatives
Find similar restaurants near a specific location.

### recommend_restaurants
Get personalized recommendations based on your preferences.

### get_usage_stats
Monitor your API usage and cache performance.

## API Costs

### Free Tier (Default)
- **500 API calls per day**
- **$0 cost** - completely free
- **No credit card required**
- Resets daily at midnight UTC

### What This Means
- ~15,000 API calls per month
- Perfect for personal projects
- Great for prototypes and MVPs
- Sufficient for small to medium apps

### Built-in Optimization
- **Caching**: Results cached for 24 hours
- **Usage Tracking**: Monitor your daily usage
- **Warnings**: Alerts at 90% usage
- **Smart Defaults**: Optimized query parameters

## Yelp vs Google Maps

| Feature | Yelp | Google Maps |
|---------|------|-------------|
| Free Tier | 500 calls/day | $200 credit/month |
| Credit Card | Not required | Required |
| Best For | Restaurants | Everything |
| Cost | $0 forever | Pay after credit |

**Choose Yelp when:**
- You want zero cost
- Focus is on restaurants
- Under 500 calls/day
- No credit card available

**Choose Google Maps when:**
- Need directions/routing
- Global coverage required
- High traffic (>500 calls/day)
- Need comprehensive POI data

See [COMPARISON_YELP_VS_GOOGLE.md](COMPARISON_YELP_VS_GOOGLE.md) for detailed comparison.

## Documentation

- **[YELP_API_GUIDE.md](YELP_API_GUIDE.md)** - Complete API access and cost guide
- **[YELP_QUICKSTART.md](YELP_QUICKSTART.md)** - Quick start guide with examples
- **[COMPARISON_YELP_VS_GOOGLE.md](COMPARISON_YELP_VS_GOOGLE.md)** - Detailed comparison

## Example Usage

```python
# Find top Italian restaurants
find_restaurants_by_location(
    location="San Francisco, CA",
    cuisine_type="italian",
    min_rating=4.5,
    max_price=3,
    open_now=True
)

# Get detailed information
get_restaurant_details(
    restaurant_name="Tony's Pizza",
    location="San Francisco, CA"
)

# Compare restaurants
compare_restaurants(
    restaurant_names=["Tony's Pizza", "Flour + Water", "SPQR"],
    location="San Francisco, CA"
)
```

## Staying Within Free Tier

1. **Use caching** - Automatic 24-hour cache
2. **Monitor usage** - Check `get_usage_stats` regularly
3. **Optimize queries** - Use filters to reduce follow-up calls
4. **Limit results** - Request only what you need

With caching, you can effectively handle much more than 500 user requests per day!

## Troubleshooting

### API Key Not Found
```bash
echo "YOUR_API_KEY" > ~/.env.yelpapi
chmod 600 ~/.env.yelpapi
```

### Daily Limit Exceeded
- Wait until midnight UTC for reset
- Check cache settings
- Review usage with `get_usage_stats`

### No Results Found
- Try broader search radius
- Remove strict filters
- Verify location spelling

## Support

- **Yelp Developer Portal**: https://www.yelp.com/developers
- **API Documentation**: https://www.yelp.com/developers/documentation/v3
- **Get API Key**: https://www.yelp.com/developers/v3/manage_app

## License

This MCP server implementation is provided as-is. Yelp API usage is subject to Yelp's Terms of Service.

## Summary

The Yelp Finder MCP provides a completely free, no-credit-card-required solution for restaurant discovery with 500 API calls per day. Perfect for personal projects, prototypes, and small to medium applications focused on restaurant search and reviews.
