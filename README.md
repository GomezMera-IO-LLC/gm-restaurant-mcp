# Restaurant Finder MCP Server

An MCP server that helps you find restaurants using Google Maps API. Search by location or along a route with detailed information including reviews, cuisine types, pricing, and direct Google Maps links.

## Features

- **Find restaurants by location**: Search for restaurants near any address, city, or coordinates
- **Find restaurants along route**: Discover dining options along your travel route
- **Detailed information**: Get ratings, reviews, cuisine types, price levels, and Google Maps links
- **Customizable search**: Adjust search radius, detour distance, and result limits

## Setup

### 1. Get a Google Maps API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Places API
   - Directions API
   - Geocoding API
4. Create credentials (API Key)
5. Copy your API key

### 2. Install the MCP Server

```bash
# Install using uv (recommended)
uv pip install -e .

# Or using pip
pip install -e .
```

### 3. Configure in Kiro

Add to your `.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "restaurant-finder": {
      "command": "python",
      "args": ["-m", "restaurant_finder_mcp.server"],
      "env": {
        "GOOGLE_MAPS_API_KEY": "YOUR_API_KEY_HERE"
      }
    }
  }
}
```

Or if using uvx:

```json
{
  "mcpServers": {
    "restaurant-finder": {
      "command": "uvx",
      "args": ["restaurant-finder-mcp"],
      "env": {
        "GOOGLE_MAPS_API_KEY": "YOUR_API_KEY_HERE"
      }
    }
  }
}
```

## Usage

### Find Restaurants by Location

```
Find restaurants near Times Square, New York
```

### Find Restaurants Along Route

```
Find restaurants along the route from Boston to New York City
```

## 🚀 Optimization & Free Tier

This MCP includes built-in optimization to help you stay within Google's $200/month free tier:

### Automatic Features
- **24-hour caching**: Repeated searches are free
- **Usage tracking**: Monitor API calls and costs
- **Smart batching**: Efficient request handling

### Check Your Usage
```
Get usage stats
```

Returns:
- Total API calls this month
- Estimated cost
- Remaining free credit
- Cache hit rate
- Cost savings

### Quick Setup
```bash
chmod +x setup_optimization.sh
./setup_optimization.sh
```

### Stay Within Free Tier
- ✅ Typical personal use: ~$15/month (92.5% under limit)
- ✅ Caching reduces costs by ~50%
- ✅ $200 credit = ~28,500 restaurant searches/month

**Read [OPTIMIZATION_GUIDE.md](OPTIMIZATION_GUIDE.md) for detailed tips and best practices.**

## Tools

### `find_restaurants_by_location`

Search for restaurants near a specific location.

**Parameters:**
- `location` (required): Address, city, or coordinates
- `radius` (optional): Search radius in meters (default: 1500)
- `max_results` (optional): Maximum results to return (default: 10)

### `find_restaurants_along_route`

Find restaurants along a route between two locations.

**Parameters:**
- `origin` (required): Starting location
- `destination` (required): Ending location
- `detour_distance` (optional): Max detour from route in meters (default: 2000)
- `max_results` (optional): Maximum results to return (default: 10)

## Response Format

Each restaurant includes:
- Name and address
- Rating and total number of ratings
- Price level ($ to $$$$)
- Cuisine types
- Top 3 reviews with ratings and excerpts
- Direct Google Maps URL

## Notes

- Requires a valid Google Maps API key with Places and Directions APIs enabled
- API usage may incur costs based on Google's pricing
- Review text is truncated to 200 characters for readability
