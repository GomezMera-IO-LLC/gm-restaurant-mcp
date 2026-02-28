#!/bin/bash

# Setup script for Yelp API key (macOS/Linux)

echo "=== Yelp API Key Setup ==="
echo ""
echo "This script will help you set up your Yelp Fusion API key."
echo ""
echo "To get your API key:"
echo "1. Go to https://www.yelp.com/developers/v3/manage_app"
echo "2. Sign in or create a Yelp account (free)"
echo "3. Create a new app or use an existing one"
echo "4. Copy your API Key"
echo ""
read -p "Enter your Yelp API key: " api_key

if [ -z "$api_key" ]; then
    echo "Error: API key cannot be empty"
    exit 1
fi

# Save to ~/.env.yelpapi
echo "$api_key" > ~/.env.yelpapi
chmod 600 ~/.env.yelpapi

echo ""
echo "✓ API key saved to ~/.env.yelpapi"
echo "✓ File permissions set to 600 (read/write for owner only)"
echo ""
echo "You're all set! The Yelp Finder MCP server will now use this API key."
echo ""
echo "Note: Yelp Fusion API free tier includes:"
echo "  - 500 API calls per day"
echo "  - No credit card required"
echo "  - Access to business search, details, and reviews"
