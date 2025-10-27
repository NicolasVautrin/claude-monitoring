#!/bin/bash

echo "========================================"
echo "Claude Code Monitoring - Startup"
echo "========================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "[ERROR] Docker is not running!"
    echo "Please start Docker and try again."
    exit 1
fi

echo "[1/3] Starting Docker containers..."
docker-compose up -d

if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to start containers!"
    exit 1
fi

echo ""
echo "[2/3] Waiting for services to be ready..."
sleep 5

echo ""
echo "[3/3] Checking container status..."
docker-compose ps

echo ""
echo "========================================"
echo "Services started successfully!"
echo "========================================"
echo ""
echo "Grafana:    http://localhost:3000"
echo "            (admin / admin)"
echo ""
echo "Prometheus: http://localhost:9090"
echo ""
echo "Configure Claude Code with:"
echo "  export CLAUDE_CODE_ENABLE_TELEMETRY=1"
echo "  export OTEL_METRICS_EXPORTER=otlp"
echo "  export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317"
echo ""
echo "Then restart Claude Code."
echo ""
