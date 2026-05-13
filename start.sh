#!/bin/bash
# Start Claude Web Chat
echo "=================================="
echo "  Claude Web Chat"
echo "=================================="
echo ""

# Check API key
if [ -z "$ANTHROPIC_AUTH_TOKEN" ] && [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "[ERROR] ANTHROPIC_AUTH_TOKEN or ANTHROPIC_API_KEY not set"
    exit 1
fi

PROJECT_DIR="$(dirname "$0")"
cd "$PROJECT_DIR"

echo "[1/2] Starting Flask server on port 5000..."
python app.py &
FLASK_PID=$!
sleep 2

# Verify Flask is running
if ! kill -0 $FLASK_PID 2>/dev/null; then
    echo "[ERROR] Flask failed to start"
    exit 1
fi

echo "[2/2] Starting cloudflared tunnel..."
echo ""
echo "  Your public URL will appear below:"
echo "  ================================="
echo ""

cloudflared tunnel --url http://127.0.0.1:5000

# Cleanup on exit
kill $FLASK_PID 2>/dev/null
