#!/bin/bash

# Thirsty's Value Finder Setup Script

set -e

echo "🚀 Thirsty's Value Finder Setup"
echo "=============================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    
    # Generate a random SECRET_KEY
    SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 64 | head -n 1)
    
    # Update SECRET_KEY in .env
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
    else
        # Linux
        sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
    fi
    
    echo "✅ .env file created with random SECRET_KEY"
else
    echo "✅ .env file already exists"
fi

echo ""

# Ask user what to do
echo "What would you like to do?"
echo "1) Start all services (Development mode)"
echo "2) Stop all services"
echo "3) View logs"
echo "4) Reset database (WARNING: This will delete all data)"
echo "5) Run tests"
echo "6) Exit"
echo ""
read -p "Enter your choice (1-6): " choice

case $choice in
    1)
        echo ""
        echo "🚀 Starting all services..."
        docker-compose up -d
        echo ""
        echo "✅ Services started successfully!"
        echo ""
        echo "📍 Access points:"
        echo "   Frontend:  http://localhost:5173"
        echo "   Backend:   http://localhost:8000"
        echo "   API Docs:  http://localhost:8000/docs"
        echo "   RabbitMQ:  http://localhost:15672 (user: analyzer, pass: analyzer_pass)"
        echo "   MinIO:     http://localhost:9001 (user: analyzer, pass: analyzer_pass)"
        echo ""
        echo "📊 View logs with: ./setup.sh (choose option 3)"
        echo "🛑 Stop services with: ./setup.sh (choose option 2)"
        ;;
    2)
        echo ""
        echo "🛑 Stopping all services..."
        docker-compose down
        echo "✅ Services stopped"
        ;;
    3)
        echo ""
        echo "📊 Showing logs (Ctrl+C to exit)..."
        docker-compose logs -f
        ;;
    4)
        echo ""
        read -p "⚠️  This will delete ALL data. Are you sure? (yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
            echo "🗑️  Resetting database..."
            docker-compose down -v
            echo "🚀 Starting services with fresh database..."
            docker-compose up -d
            echo "✅ Database reset complete"
        else
            echo "❌ Cancelled"
        fi
        ;;
    5)
        echo ""
        echo "🧪 Running tests..."
        docker-compose exec backend pytest tests/ -v
        ;;
    6)
        echo ""
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
