#!/bin/bash

echo "🚀 Setting up Restaurant Finder MCP with optimization..."
echo ""

# Create cache directory
mkdir -p .cache
echo "✅ Created cache directory"

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "📦 Python version: $python_version"

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip3 install -e . --user

echo ""
echo "✅ Setup complete!"
echo ""
echo "📊 Optimization features enabled:"
echo "  - 24-hour response caching"
echo "  - API usage tracking"
echo "  - Free tier monitoring"
echo ""
echo "💡 Tips:"
echo "  - Check usage: Ask 'Get usage stats'"
echo "  - Cache location: .cache/"
echo "  - Read OPTIMIZATION_GUIDE.md for best practices"
echo ""
echo "🎉 Ready to use! Restart your MCP server to activate caching."
