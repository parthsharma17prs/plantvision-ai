#!/bin/bash
# ─────────────────────────────────────────────
#  PlantVision AI Dashboard Startup Script
# ─────────────────────────────────────────────
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo "🌿 PlantVision AI Dashboard"
echo "──────────────────────────────────────"

# Check Python
if ! command -v python3 &>/dev/null; then
  echo "❌ python3 not found. Please install Python 3.9+"
  exit 1
fi

echo "🐍 Python: $(python3 --version)"

# Install deps if needed
echo "📦 Checking dependencies..."
python3 -m pip install -q -r "$DIR/requirements.txt"

# Verify token.json exists somewhere accessible
TOKEN_LOCATIONS=(
  "$DIR/../pi_to_drive/token.json"
  "$DIR/token.json"
  "$DIR/../token.json"
)
TOKEN_FOUND=false
for tp in "${TOKEN_LOCATIONS[@]}"; do
  if [ -f "$tp" ]; then
    echo "🔑 Auth token found: $tp"
    TOKEN_FOUND=true
    break
  fi
done

if [ "$TOKEN_FOUND" = false ]; then
  echo ""
  echo "⚠️  WARNING: token.json not found."
  echo "   Run 'python3 ../pi_to_drive/upload_to_drive.py' once on this Mac"
  echo "   to authenticate with Google Drive, then try again."
  echo ""
fi

echo ""
echo "🚀 Starting server at http://localhost:5050"
echo "   Press Ctrl+C to stop."
echo ""

cd "$DIR"
python3 server.py
