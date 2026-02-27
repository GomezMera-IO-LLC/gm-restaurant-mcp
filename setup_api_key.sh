#!/bin/bash

echo "🔑 Restaurant Finder MCP - API Key Setup"
echo "========================================"
echo ""

API_FILE="$HOME/.env.googleapi"

# Check if file already exists
if [ -f "$API_FILE" ]; then
    echo "⚠️  API key file already exists at: $API_FILE"
    echo ""
    read -p "Do you want to update it? (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Keeping existing API key."
        exit 0
    fi
fi

echo ""
echo "Please enter your Google Maps API key:"
echo "(Get one at: https://console.cloud.google.com/)"
echo ""
read -p "API Key: " api_key

if [ -z "$api_key" ]; then
    echo "❌ No API key provided. Exiting."
    exit 1
fi

# Save API key
echo "$api_key" > "$API_FILE"
chmod 600 "$API_FILE"  # Secure the file

echo ""
echo "✅ API key saved to: $API_FILE"
echo "🔒 File permissions set to 600 (owner read/write only)"
echo ""
echo "Next steps:"
echo "1. Restart your MCP server in Kiro"
echo "2. Test with: 'Find restaurants near me'"
echo ""
echo "🎉 Setup complete!"
