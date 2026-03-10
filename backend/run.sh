#!/bin/bash
# Run MBP Backend v2.0 with proper venv activation

cd "$(dirname "$0")"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate venv
source venv/bin/activate

# Clear Python cache to avoid stale imports
echo "🧹 Clearing cache..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null

echo "🚀 Starting MBP Backend v2.0..."
echo "📚 API Docs: http://localhost:8000/docs"
echo ""

# Run server
exec python3 main.py
