# Yelp Finder MCP - API Access & Cost Guide

## Overview

The `yelp_finder_mcp` module provides restaurant search and discovery tools using the Yelp Fusion API. This guide explains how to get API access and understand the costs.

## Getting Your Yelp API Key

### Step-by-Step Process

1. **Visit the Yelp Developers Portal**
   - Go to: https://www.yelp.com/developers/v3/manage_app
   - You'll need to sign in or create a Yelp account (completely free)

2. **Create a New App**
   - Click "Create New App" button
   - Fill in the required information:
     - **App Name**: Choose any name (e.g., "My Restaurant Finder")
     - **Industry**: Select relevant category
     - **Contact Email**: Your email address
     - **Description**: Brief description of your use case
     - **Terms of Service**: Accept Yelp's API Terms of Service

3. **Get Your API Key**
   - Once created, you'll see your app details page
   - Your **API Key** will be displayed prominently
   - Copy this key - you'll need it for setup

4. **Setup the API Key**
   
   Run the appropriate setup script for your operating system:
   
   **macOS/Linux:**
   ```bash
   chmod +x setup_yelp_key.sh
   ./setup_yelp_key.sh
   ```
   
   **Windows (PowerShell):**
   ```powershell
   .\setup_yelp_key.ps1
   ```
   
   **Windows (Command Prompt):**
   ```cmd
   setup_yelp_key.bat
   ```

## API Costs & Limits

### Free Tier (Default)

The Yelp Fusion API offers a **completely free tier** with the following limits:

- **500 API calls per day**
- **No credit card required**
- **No expiration** - free forever
- Resets daily at midnight UTC

### What's Included (Free)

✅ Business Search
✅ Business Details
✅ Business Reviews (up to 3 per business)
✅ Business Match
✅ Phone Search
✅ Transaction Search
✅ Autocomplete

### What Counts as an API Call?

Each of these operations counts as 1 API call:
- Searching for restaurants (`find_restaurants_by_location`)
- Getting restaurant details (`get_restaurant_details`)
- Getting reviews for a restaurant
- Comparing restaurants (1 call per restaurant)
- Finding alternatives

### Cost Breakdown

| Tier | Daily Limit | Monthly Equivalent | Cost |
|------|-------------|-------------------|------|
| Free | 500 calls/day | ~15,000 calls/month | **$0** |

### Optimization Features

The `yelp_finder_mcp` module includes built-in optimization to help you stay within the free tier:

1. **Caching System**
   - Results are cached for 24 hours by default
   - Repeated queries use cached data (no API call)
   - Saves API calls and improves response time

2. **Usage Tracking**
   - Monitors daily API usage
   - Warns when approaching the 500 call limit
   - Shows cache hit rate and calls saved

3. **Smart Defaults**
   - Reasonable result limits (10 restaurants by default)
   - Efficient query parameters
   - Automatic cache cleanup

### Monitoring Your Usage

Use the `get_usage_stats` tool to check:
- Total API calls made today
- Remaining calls for the day
- Cache performance
- Estimated calls saved

Example output:
```json
{
  "usage": {
    "date": "2024-02-27",
    "total_api_calls": 45,
    "daily_limit": 500,
    "remaining_calls": 455,
    "usage_percentage": "9.0%"
  },
  "cache": {
    "api_calls_saved": 23,
    "cache_hit_rate": "33.8%"
  }
}
```

## Comparison: Yelp vs Google Maps

| Feature | Yelp Fusion API | Google Maps API |
|---------|----------------|-----------------|
| **Free Tier** | 500 calls/day | $200 credit/month |
| **Credit Card** | Not required | Required |
| **Cost After Free** | N/A (hard limit) | Pay per use |
| **Reviews** | 3 per business | 5 per place |
| **Photos** | Yes | Yes |
| **Business Hours** | Yes | Yes |
| **Pricing Info** | Yes (1-4 scale) | Yes (1-4 scale) |
| **Ratings** | Yes (1-5 stars) | Yes (1-5 stars) |

## Best Practices

### Staying Within Free Tier

1. **Use Caching Effectively**
   - Don't clear cache unnecessarily
   - Default 24-hour TTL is optimal for most use cases

2. **Batch Operations**
   - Compare multiple restaurants in one request
   - Use search filters to reduce follow-up calls

3. **Monitor Usage**
   - Check `get_usage_stats` regularly
   - Watch for warnings at 90% usage

4. **Optimize Queries**
   - Use specific location searches
   - Apply filters (rating, price) in initial search
   - Limit results to what you actually need

### When You Might Hit Limits

- **High-traffic applications**: 500 calls/day = ~20 calls/hour
- **Frequent comparisons**: Each restaurant in comparison = 1 call
- **Detailed reviews**: Getting reviews for many restaurants

### Solutions if You Need More

If you consistently need more than 500 calls/day:

1. **Contact Yelp**: Request increased limits for legitimate use cases
2. **Optimize caching**: Increase cache TTL for less time-sensitive data
3. **Combine with Google Maps**: Use both APIs strategically
4. **Rate limiting**: Implement user-level rate limits in your application

## API Key Security

### Best Practices

✅ **DO:**
- Store API key in `~/.env.yelpapi` file
- Keep file permissions restricted (600 on Unix)
- Never commit API keys to version control
- Use environment variables in production

❌ **DON'T:**
- Share your API key publicly
- Commit `.env.yelpapi` to git
- Expose API key in client-side code
- Use the same key across multiple projects

### Key Rotation

If your API key is compromised:
1. Go to https://www.yelp.com/developers/v3/manage_app
2. Regenerate your API key
3. Run the setup script again with the new key

## Troubleshooting

### "API key not found" Error

```bash
# Run the setup script
./setup_yelp_key.sh

# Or manually create the file
echo "YOUR_API_KEY" > ~/.env.yelpapi
chmod 600 ~/.env.yelpapi
```

### "Daily limit exceeded" Error

- Wait until midnight UTC for reset
- Check usage with `get_usage_stats`
- Review cache settings
- Consider optimizing your queries

### "Invalid API key" Error

- Verify key is correct in `~/.env.yelpapi`
- Check for extra spaces or newlines
- Regenerate key if necessary

## Additional Resources

- **Yelp Fusion API Documentation**: https://www.yelp.com/developers/documentation/v3
- **API Terms of Service**: https://www.yelp.com/developers/api_terms
- **Developer Support**: https://www.yelp.com/developers/support
- **API Status**: Check Yelp's status page for outages

## Summary

✅ **Free forever** - No credit card needed
✅ **500 calls/day** - Sufficient for most personal/small projects
✅ **Built-in caching** - Reduces API usage automatically
✅ **Easy setup** - Get started in minutes
✅ **No surprise charges** - Hard limit, not pay-per-use

The Yelp Fusion API is an excellent choice for restaurant discovery applications, especially for personal projects, prototypes, and small-scale applications where the 500 daily call limit is sufficient.
