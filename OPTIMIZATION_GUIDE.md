# API Optimization Guide

This guide helps you stay within Google Maps Platform's free tier ($200/month credit).

## Optimization Features

### 1. Automatic Caching (24-hour TTL)
All API responses are cached for 24 hours, dramatically reducing redundant calls.

**What's cached:**
- Restaurant searches
- Place details
- Directions
- Geocoding results
- Distance calculations

**Benefits:**
- Repeated searches return instantly
- No API cost for cached data
- Automatic cache expiration

### 2. Usage Tracking
Monitor your API usage in real-time to avoid surprises.

**Check your usage:**
```
Get usage stats
```

**What you'll see:**
- Total API calls this month
- Estimated cost
- Remaining free credit
- Cache hit rate
- Cost savings from caching

### 3. Smart Request Optimization

#### Reduce Search Radius
```
# Instead of:
Find restaurants within 5000m

# Use:
Find restaurants within 1500m  # Default, more efficient
```

#### Limit Results
```
# Instead of:
Find 20 restaurants

# Use:
Find 5-10 restaurants  # Usually sufficient
```

#### Use Specific Searches
```
# Instead of:
Find all restaurants in Tampa

# Use:
Find Italian restaurants near downtown Tampa  # More targeted
```

## Free Tier Breakdown

### Monthly Free Credit: $200

**Approximate free usage per month:**
- **28,500** Places Nearby searches
- **11,700** Place Details requests
- **40,000** Directions requests
- **40,000** Geocoding requests
- **40,000** Distance Matrix elements

### Cost Per Request (after free credit)

| API | Cost per 1,000 | Example Usage |
|-----|----------------|---------------|
| Places Nearby | $32 | Finding restaurants |
| Place Details | $17 | Getting reviews, hours |
| Directions | $5 | Turn-by-turn navigation |
| Geocoding | $5 | Converting addresses |
| Distance Matrix | $5 | Calculating distances |

## Best Practices

### 1. Batch Your Searches
Instead of multiple small searches, combine them:
```
# Good: One search with filters
Find Italian restaurants with 4+ rating under $$ in Wesley Chapel

# Avoid: Multiple separate searches
Find Italian restaurants
Find 4+ rated restaurants
Find cheap restaurants
```

### 2. Use Comparison Tool
Compare multiple restaurants in one call instead of getting details separately:
```
# Efficient:
Compare China Wok, Latin Twist, and Vallarta's

# Less efficient:
Get details for China Wok
Get details for Latin Twist
Get details for Vallarta's
```

### 3. Leverage Cache
Searching for the same restaurant within 24 hours? It's free!
```
# First call: Uses API
Get details for Barcelona Wine Bar in Tampa

# Within 24 hours: Uses cache (free)
Get details for Barcelona Wine Bar in Tampa
```

### 4. Be Specific with Locations
```
# Good:
Wesley Chapel, FL

# Avoid:
Florida  # Too broad, returns too many results
```

### 5. Use Appropriate Tools
Choose the right tool for your need:

- **Quick search**: `find_restaurants_by_location`
- **Detailed info**: `get_restaurant_details` (only when needed)
- **Multiple options**: `compare_restaurants` (efficient for 2-3)
- **Navigation**: `get_directions` (only when actually going)

## Monitoring Your Usage

### Check Stats Regularly
```
Get usage stats
```

### Warning Levels
- **75% used**: Caution - monitor usage
- **90% used**: Warning - reduce usage or expect charges
- **100% used**: Charges will apply for additional requests

### Monthly Reset
Usage resets on the 1st of each month. Plan accordingly!

## Cost Optimization Tips

### 1. Cache Management
The system automatically caches for 24 hours. For even better optimization:
- Searches for the same location/restaurant are free (cached)
- Popular restaurants get cached from other users' searches
- Cache clears automatically after 24 hours

### 2. Reduce Unnecessary Details
```
# If you just need basic info:
Find restaurants by location  # Returns basic info

# Only get full details when needed:
Get restaurant details  # More expensive, use selectively
```

### 3. Use Filters Effectively
```
# Efficient - filters before API call:
Find restaurants with min_rating=4, max_price=2

# Less efficient - gets all, filters after:
Find all restaurants, then manually filter
```

### 4. Avoid Redundant Calls
```
# Good:
Get restaurant details (includes hours, reviews, etc.)

# Avoid:
Get restaurant details
Get restaurant hours  # Already included above
Get restaurant reviews  # Already included above
```

## Example: Staying Under Free Tier

### Typical Personal Usage (Well Within Free Tier)
- 10 restaurant searches per day = 300/month
- 5 detail lookups per day = 150/month
- 3 direction requests per day = 90/month
- **Estimated cost**: ~$15/month (92.5% under free tier)

### Heavy Usage (Approaching Limit)
- 50 searches per day = 1,500/month
- 30 detail lookups per day = 900/month
- 10 direction requests per day = 300/month
- **Estimated cost**: ~$180/month (10% buffer remaining)

### With Caching (50% hit rate)
- Same heavy usage as above
- 50% served from cache (free)
- **Estimated cost**: ~$90/month (55% under free tier)

## Troubleshooting

### "Approaching free tier limit" warning
1. Check usage stats
2. Review which APIs you're using most
3. Reduce search radius
4. Limit max_results
5. Wait for monthly reset

### High costs
1. Check for repeated searches (should be cached)
2. Reduce search frequency
3. Use more specific queries
4. Consider if you need all the data

### Cache not working
1. Restart MCP server
2. Check `.cache` directory exists
3. Verify optimized client is loaded

## Advanced: Manual Cache Management

### Clear old cache (7+ days)
The system automatically manages cache, but you can manually clear if needed.

### View cache statistics
```
Get usage stats
```

Shows:
- Cache hit rate
- API calls saved
- Estimated cost savings

## Summary

**Key Takeaways:**
1. ✅ Caching saves ~50% of API costs automatically
2. ✅ $200/month free credit covers most personal use
3. ✅ Monitor usage with `get_usage_stats`
4. ✅ Be specific with searches
5. ✅ Use appropriate tools for each task
6. ✅ Batch operations when possible

**You're likely fine if:**
- Using for personal restaurant discovery
- Searching 10-20 times per day
- Not running automated/bulk operations

**Watch out if:**
- Making 100+ searches per day
- Running automated scripts
- Approaching 75% of free tier

Need help? Check usage stats regularly and adjust your search patterns accordingly!
