#!/bin/sh
echo "=== Starting BarberFlow Bot ==="

echo "Starting API server..."
python3 /app/api_server.py &
API_PID=$!

echo "Waiting 5s for API to start..."
sleep 5

echo "Checking API health..."
curl -s http://127.0.0.1:$PORT/health || echo "API not ready yet"

echo ""
echo "Starting WhatsApp Bridge..."
cd /app/whatsapp-bridge && node index.js &
BRIDGE_PID=$!

echo "API PID: $API_PID"
echo "Bridge PID: $BRIDGE_PID"

wait
