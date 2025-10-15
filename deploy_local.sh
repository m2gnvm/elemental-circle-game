#!/bin/bash

# Elemental Circle Game - WSL Docker Deployment Script
# This script deploys the backend service locally using Docker in WSL

set -e  # Exit on any error

echo "🐳 Elemental Circle Game - WSL Docker Deployment"
echo "================================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    echo "   Download from: https://www.docker.com/products/docker-desktop/"
    echo "   Make sure WSL 2 integration is enabled in Docker Desktop settings"
    exit 1
fi

echo "✅ Docker is running"

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found. Please install Docker Desktop with compose support."
    exit 1
fi

echo "✅ docker-compose is available"

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down --remove-orphans

# Build and start services
echo "🔨 Building and starting services..."
docker-compose up --build -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check service health
echo "🔍 Checking service health..."

# Check PostgreSQL
if docker-compose exec -T postgres pg_isready -U gameuser -d elemental_circle > /dev/null 2>&1; then
    echo "✅ PostgreSQL is healthy"
else
    echo "❌ PostgreSQL is not healthy"
fi

# Check Redis
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is healthy"
else
    echo "❌ Redis is not healthy"
fi

# Check FastAPI app
sleep 5
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ FastAPI app is healthy"
else
    echo "❌ FastAPI app is not healthy"
fi

echo ""
echo "🎉 Deployment completed!"
echo "========================"
echo "📊 Services:"
echo "   • PostgreSQL: localhost:5432"
echo "   • Redis: localhost:6379"
echo "   • FastAPI: http://localhost:8000"
echo ""
echo "📚 Useful commands:"
echo "   • View logs: docker-compose logs -f"
echo "   • Stop services: docker-compose down"
echo "   • Restart services: docker-compose restart"
echo "   • View service status: docker-compose ps"
echo ""
echo "🎮 Test the API:"
echo "   • Health check: curl http://localhost:8000/health"
echo "   • API docs: http://localhost:8000/docs"
echo "   • Interactive game: python test_scripts/interactive_game.py"
echo ""
