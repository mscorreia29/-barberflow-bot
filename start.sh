#!/bin/bash
echo "=== Starting BarberFlow Bot ==="
echo "PORT=$PORT"

echo "Starting API server on port $PORT..."
python3 /app/api_server.py &
API_PID=$!

sleep 5

echo "Starting WhatsApp Bridge..."
cd /app/whatsapp-bridge
node index.js 2>&1 &
BRIDGE_PID=$!

echo "API PID=$API_PID, Bridge PID=$BRIDGE_PID"

wait $BRIDGE_PID
