#!/bin/bash

# Docker Health Check Script for Elemental Circle Game

echo "🔍 Docker Health Check"
echo "====================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running"
    exit 1
fi

echo "✅ Docker is running"

# Check if containers are running
echo ""
echo "📊 Container Status:"
docker-compose ps

echo ""
echo "🔍 Service Health Checks:"

# Check PostgreSQL
if docker-compose exec -T postgres pg_isready -U gameuser -d elemental_circle > /dev/null 2>&1; then
    echo "✅ PostgreSQL: Healthy"
else
    echo "❌ PostgreSQL: Unhealthy"
fi

# Check Redis
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis: Healthy"
else
    echo "❌ Redis: Unhealthy"
fi

# Check FastAPI app
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ FastAPI: Healthy"
    echo ""
    echo "🎮 API Endpoints:"
    echo "   • Health: http://localhost:8000/health"
    echo "   • Docs: http://localhost:8000/docs"
    echo "   • OpenAPI: http://localhost:8000/openapi.json"
else
    echo "❌ FastAPI: Unhealthy"
fi

echo ""
echo "📋 Container Logs (last 10 lines):"
echo "-----------------------------------"
docker-compose logs --tail=10
