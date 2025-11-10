#!/bin/bash

# CrisisGuard AI - Quick Start Script
# This script sets up and launches the complete platform

set -e

echo "🛡️  CrisisGuard AI - Quick Start"
echo "================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your API keys!"
    echo "   Required: OPENAI_API_KEY"
    echo "   Optional: NEWS_API_KEY, GOOGLE_FACTCHECK_API_KEY"
    echo ""
    echo "Press Enter after editing .env to continue..."
    read
fi

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker Desktop first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install it first."
    exit 1
fi

echo "✅ Docker is installed"
echo ""

# Build and start services
echo "🚀 Building and starting services..."
echo "   This may take 5-10 minutes on first run..."
echo ""

docker-compose up --build -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check health
echo "🏥 Checking service health..."

BACKEND_HEALTH=$(curl -s http://localhost:8000/health | grep -o "healthy" || echo "unhealthy")

if [ "$BACKEND_HEALTH" = "healthy" ]; then
    echo "✅ Backend is healthy"
else
    echo "⚠️  Backend might still be starting... check logs if it doesn't work"
fi

echo ""
echo "✨ CrisisGuard AI is running!"
echo ""
echo "🌐 Access the platform:"
echo "   Frontend:  http://localhost:5173"
echo "   API Docs:  http://localhost:8000/docs"
echo "   Health:    http://localhost:8000/health"
echo ""
echo "📊 View logs:"
echo "   All logs:     docker-compose logs -f"
echo "   Backend only: docker-compose logs -f backend"
echo "   Frontend only: docker-compose logs -f frontend"
echo ""
echo "🛑 To stop:"
echo "   docker-compose down"
echo ""
echo "🔄 To restart:"
echo "   docker-compose restart"
echo ""
echo "Happy fact-checking! 🎉"
