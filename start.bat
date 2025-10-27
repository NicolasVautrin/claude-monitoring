@echo off
echo ========================================
echo Claude Code Monitoring - Startup
echo ========================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo [1/3] Starting Docker containers...
docker-compose up -d

if %errorlevel% neq 0 (
    echo [ERROR] Failed to start containers!
    pause
    exit /b 1
)

echo.
echo [2/3] Waiting for services to be ready...
timeout /t 5 /nobreak >nul

echo.
echo [3/3] Checking container status...
docker-compose ps

echo.
echo ========================================
echo Services started successfully!
echo ========================================
echo.
echo Grafana:    http://localhost:3000
echo            (admin / admin)
echo.
echo Prometheus: http://localhost:9090
echo.
echo Configure Claude Code with:
echo   $env:CLAUDE_CODE_ENABLE_TELEMETRY="1"
echo   $env:OTEL_METRICS_EXPORTER="otlp"
echo   $env:OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"
echo.
echo Then restart Claude Code.
echo.
pause
