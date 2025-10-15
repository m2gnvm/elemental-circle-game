@echo off
REM Elemental Circle Game - Local Docker Deployment Script (Windows)
REM This script deploys the backend service locally using Docker

echo 🐳 Elemental Circle Game - Local Docker Deployment
echo ==================================================

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    echo    Download from: https://www.docker.com/products/docker-desktop/
    pause
    exit /b 1
)

echo ✅ Docker is running

REM Check if docker-compose is available
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ docker-compose not found. Please install Docker Desktop with compose support.
    pause
    exit /b 1
)

echo ✅ docker-compose is available

REM Stop any existing containers
echo 🛑 Stopping existing containers...
docker-compose down --remove-orphans

REM Build and start services
echo 🔨 Building and starting services...
docker-compose up --build -d

REM Wait for services to be healthy
echo ⏳ Waiting for services to be healthy...
timeout /t 10 /nobreak >nul

REM Check service health
echo 🔍 Checking service health...

REM Check PostgreSQL
docker-compose exec -T postgres pg_isready -U gameuser -d elemental_circle >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ PostgreSQL is healthy
) else (
    echo ❌ PostgreSQL is not healthy
)

REM Check Redis
docker-compose exec -T redis redis-cli ping >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Redis is healthy
) else (
    echo ❌ Redis is not healthy
)

REM Check FastAPI app
timeout /t 5 /nobreak >nul
curl -f http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ FastAPI app is healthy
) else (
    echo ❌ FastAPI app is not healthy
)

echo.
echo 🎉 Deployment completed!
echo ========================
echo 📊 Services:
echo    • PostgreSQL: localhost:5432
echo    • Redis: localhost:6379
echo    • FastAPI: http://localhost:8000
echo.
echo 📚 Useful commands:
echo    • View logs: docker-compose logs -f
echo    • Stop services: docker-compose down
echo    • Restart services: docker-compose restart
echo    • View service status: docker-compose ps
echo.
echo 🎮 Test the API:
echo    • Health check: curl http://localhost:8000/health
echo    • API docs: http://localhost:8000/docs
echo    • Interactive game: python test_scripts/interactive_game.py
echo.
pause
