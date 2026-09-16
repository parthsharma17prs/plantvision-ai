#!/usr/bin/env bash
# ==============================================================================
# 🌿 PlantVision AI — Complete 1-Click Laptop Demo
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

echo "============================================================"
echo "  🌿 PlantVision AI — Starting Live Laptop Demo"
echo "============================================================"

# 1. Start Dashboard Server (if not already running)
if lsof -Pi :5050 -sTCP:LISTEN -t >/dev/null ; then
    echo "✅ Dashboard Server already running on port 5050."
else
    echo "🚀 Starting Dashboard Server (Backend & Frontend)..."
    conda run -n plantvision python plant_dashboard/server.py > server.log 2>&1 &
    SERVER_PID=$!
    sleep 3
fi

# 2. Start Google Drive Uploader (if not already running)
if pgrep -f "raspberry_pi/upload_to_drive.py" >/dev/null ; then
    echo "✅ Google Drive Uploader already running."
else
    echo "🚀 Starting Google Drive Uploader in background..."
    conda run -n plantvision python raspberry_pi/upload_to_drive.py > uploader.log 2>&1 &
    UPLOADER_PID=$!
    sleep 2
fi

# 3. Open Browser
echo "🌐 Opening Dashboard in browser: http://localhost:5050"
open "http://localhost:5050"

# 4. Run the Live Feeder
echo ""
echo "============================================================"
echo "  📸 Starting Live Image Feed for the Demo!"
echo "  (Watch your browser at http://localhost:5050 update live)"
echo "============================================================"
echo "Press Ctrl+C anytime to stop."
echo ""

conda run -n plantvision python feeder.py
