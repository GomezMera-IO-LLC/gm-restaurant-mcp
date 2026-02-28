# MCP Configuration Guide

This guide explains how to configure both restaurant finder MCP servers in Kiro.

## Quick Setup

The MCP configuration file has been created at `.kiro/settings/mcp.json` with both servers pre-configured.

## Configuration File

Location: `.kiro/settings/mcp.json`

```json
{
  "mcpServers": {
    "restaurant-finder": {
      "command": "python3",
      "args": [
        "-m",
        "restaurant_finder_mcp.server"
      ],
      "disabled": false,
      "autoApprove": [],
      "description": "Find restaurants using Google Maps API with caching and usage tracking",
      "env": {}
    },
    "yelp-finder": {
      "command": "python3",
      "args": [
        "-m",
        "yelp_finder_mcp.server"
      ],
      "disabled": false,
      "autoApprove": [],
      "description": "Find restaurants using Yelp Fusion API - 500 free calls/day, no credit card required",
      "env": {}
    }
  }
}
```

## Prerequisites

### 1. Install Python Dependencies

```bash
pip install googlemaps requests
```

### 2. Setup API Keys

#### Google Maps API Key (for restaurant-finder)
```bash
# macOS/Linux
./setup_api_key.sh

# Windows
setup_api_key.bat
```

#### Yelp API Key (for yelp-finder)
```bash
# macOS/Linux
./setup_yelp_key.sh

# Windows
setup_yelp_key.bat
```

## Server Descriptions

### restaurant-finder (Google Maps)

**Provider:** Google Maps Places API

**Features:**
- Comprehensive restaurant search
- Directions and routing
- Distance calculations
- Geocoding
- Global coverage
- 14 tools available

**Cost:**
- $200 monthly credit (requires credit card)
- Pay-per-use after credit exhausted
- ~$17-32 per 1,000 calls

**Best For:**
- High-traffic applications
- Need directions/routing
- Global coverage required
- Comprehensive POI data

### yelp-finder (Yelp Fusion)

**Provider:** Yelp Fusion API

**Features:**
- Restaurant-focused search
- Detailed reviews (3 per business)
- Business hours and details
- Recommendations
- 7 tools available

**Cost:**
- **$0 - Completely free**
- 500 API calls per day
- No credit card required
- Never expires

**Best For:**
- Personal projects
- Restaurant-specific apps
- Budget-conscious developers
- Prototypes and MVPs

## Using the Servers in Kiro

### Activating Servers

1. Open Kiro
2. The servers will automatically connect if:
   - Python dependencies are installed
   - API keys are configured
   - Servers are not disabled in mcp.json

### Checking Server Status

In Kiro, you can view the MCP Server panel to see:
- Connected servers
- Available tools
- Server status

### Available Tools

#### restaurant-finder Tools (14 total)

1. `find_restaurants_by_location` - Search near location
2. `find_restaurants_along_route` - Search along route
3. `get_restaurant_details` - Detailed info with reviews
4. `compare_restaurants` - Compare 2-3 restaurants
5. `get_restaurant_hours` - Check hours and open status
6. `get_directions` - Get directions to restaurant
7. `find_nearby_alternatives` - Find similar restaurants
8. `extract_popular_dishes` - Extract dish mentions from reviews
9. `check_restaurant_features` - Check dietary options, ambiance
10. `get_peak_hours` - Get busy times info
11. `recommend_restaurants` - Personalized recommendations
12. `get_review_link` - Get link to leave review
13. `get_usage_stats` - Monitor API usage
14. Additional geocoding and routing tools

#### yelp-finder Tools (7 total)

1. `find_restaurants_by_location` - Search near location
2. `get_restaurant_details` - Detailed info with reviews
3. `compare_restaurants` - Compare 2-3 restaurants
4. `get_restaurant_hours` - Check hours and open status
5. `find_nearby_alternatives` - Find similar restaurants
6. `recommend_restaurants` - Personalized recommendations
7. `get_usage_stats` - Monitor API usage

## Configuration Options

### Disabling a Server

To disable a server, set `"disabled": true`:

```json
{
  "mcpServers": {
    "yelp-finder": {
      "command": "python3",
      "args": ["-m", "yelp_finder_mcp.server"],
      "disabled": true,
      "autoApprove": []
    }
  }
}
```

### Auto-Approving Tools

To auto-approve specific tools (skip confirmation prompts):

```json
{
  "mcpServers": {
    "yelp-finder": {
      "command": "python3",
      "args": ["-m", "yelp_finder_mcp.server"],
      "disabled": false,
      "autoApprove": [
        "find_restaurants_by_location",
        "get_restaurant_details"
      ]
    }
  }
}
```

### Environment Variables

You can pass environment variables to the servers:

```json
{
  "mcpServers": {
    "yelp-finder": {
      "command": "python3",
      "args": ["-m", "yelp_finder_mcp.server"],
      "disabled": false,
      "autoApprove": [],
      "env": {
        "YELP_API_KEY": "your-api-key-here",
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

**Note:** It's recommended to use the API key files (`~/.env.yelpapi` and `~/.env.googleapi`) instead of environment variables for better security.

### Custom Python Path

If you need to use a specific Python installation:

```json
{
  "mcpServers": {
    "yelp-finder": {
      "command": "/usr/local/bin/python3.11",
      "args": ["-m", "yelp_finder_mcp.server"],
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

### Using Virtual Environment

If you're using a virtual environment:

```json
{
  "mcpServers": {
    "yelp-finder": {
      "command": "/path/to/venv/bin/python",
      "args": ["-m", "yelp_finder_mcp.server"],
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

## Troubleshooting

### Server Not Connecting

1. **Check Python installation:**
   ```bash
   python3 --version
   ```

2. **Check dependencies:**
   ```bash
   pip list | grep -E "googlemaps|requests"
   ```

3. **Check API keys:**
   ```bash
   # Google Maps
   cat ~/.env.googleapi
   
   # Yelp
   cat ~/.env.yelpapi
   ```

4. **Test server manually:**
   ```bash
   # Test Google Maps server
   python3 -m restaurant_finder_mcp.server
   
   # Test Yelp server
   python3 -m yelp_finder_mcp.server
   ```

### Server Crashes on Startup

Check the Kiro logs for error messages. Common issues:

- **Missing API key:** Run the setup scripts
- **Missing dependencies:** Run `pip install googlemaps requests`
- **Wrong Python version:** Requires Python 3.9+

### Tools Not Appearing

1. Verify server is enabled (`"disabled": false`)
2. Check server status in Kiro MCP panel
3. Restart Kiro
4. Check for error messages in logs

### API Key Errors

**Google Maps:**
```bash
# Verify key exists
cat ~/.env.googleapi

# Re-run setup if needed
./setup_api_key.sh
```

**Yelp:**
```bash
# Verify key exists
cat ~/.env.yelpapi

# Re-run setup if needed
./setup_yelp_key.sh
```

## Advanced Configuration

### Running Both Servers

You can use both servers simultaneously:
- Use Yelp for restaurant discovery (free)
- Use Google Maps for directions (within $200 credit)
- Optimize costs by choosing the right server for each task

### Server Selection Strategy

**Use yelp-finder when:**
- Searching for restaurants
- Getting restaurant details
- Comparing restaurants
- Checking hours
- Getting recommendations

**Use restaurant-finder when:**
- Need directions to restaurant
- Planning routes with restaurant stops
- Need distance calculations
- Need geocoding
- Working with international locations

### Monitoring Usage

Both servers include usage tracking:

```
# Check Google Maps usage
Use tool: get_usage_stats (restaurant-finder)

# Check Yelp usage
Use tool: get_usage_stats (yelp-finder)
```

## Configuration Precedence

MCP configurations are merged with the following precedence:

1. User config: `~/.kiro/settings/mcp.json` (global)
2. Workspace config: `.kiro/settings/mcp.json` (this file)

Workspace settings override user settings for the same server name.

## Example Workflows

### Workflow 1: Find and Navigate to Restaurant

1. Use `yelp-finder` → `find_restaurants_by_location` (free)
2. Use `yelp-finder` → `get_restaurant_details` (free)
3. Use `restaurant-finder` → `get_directions` (uses Google credit)

**Cost:** 2 free Yelp calls + 1 Google Maps call

### Workflow 2: Compare and Choose

1. Use `yelp-finder` → `compare_restaurants` (free)
2. Use `yelp-finder` → `get_restaurant_hours` (free)
3. Use `yelp-finder` → `find_nearby_alternatives` (free)

**Cost:** 3 free Yelp calls, $0

### Workflow 3: Route Planning

1. Use `restaurant-finder` → `find_restaurants_along_route`
2. Use `restaurant-finder` → `get_directions`

**Cost:** Uses Google Maps credit

## Security Best Practices

1. **Never commit mcp.json with API keys** to version control
2. **Use API key files** (`~/.env.googleapi`, `~/.env.yelpapi`)
3. **Set file permissions:**
   ```bash
   chmod 600 ~/.env.googleapi
   chmod 600 ~/.env.yelpapi
   ```
4. **Rotate keys** if compromised
5. **Use separate keys** for development and production

## Updating Configuration

After modifying `mcp.json`:

1. Save the file
2. Servers will automatically reconnect
3. Or restart Kiro to reload configuration

You can also use the Kiro command palette:
- "MCP: Reconnect Servers"
- "MCP: Reload Configuration"

## Getting Help

- **Google Maps Issues:** See `README.md` and `OPTIMIZATION_GUIDE.md`
- **Yelp Issues:** See `README_YELP.md` and `YELP_API_GUIDE.md`
- **MCP Configuration:** Check Kiro documentation
- **Server Logs:** Check Kiro output panel for error messages

## Summary

Both servers are now configured and ready to use:

✅ **restaurant-finder** - Google Maps (comprehensive, paid after credit)
✅ **yelp-finder** - Yelp Fusion (restaurant-focused, free forever)

Choose the right server for your needs, or use both strategically to optimize costs and functionality!
