#!/bin/bash
# Setup database for MBP Prototype

echo "🗄️  MBP Database Setup"
echo "======================"

# Check if Docker is available
if command -v docker &> /dev/null; then
    echo "✅ Docker found"
    
    # Start PostgreSQL container
    echo "🚀 Starting PostgreSQL container..."
    docker-compose up -d
    
    # Wait for PostgreSQL to be ready
    echo "⏳ Waiting for PostgreSQL to be ready..."
    sleep 5
    
    # Check if container is running
    if docker ps | grep -q mbp-postgres; then
        echo "✅ PostgreSQL container is running"
        
        # Get container IP
        DB_HOST=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' mbp-postgres)
        echo "📝 Database host: $DB_HOST"
        
        # Create .env file
        echo "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/mbp_prototype" > .env
        echo "✅ Created .env file with DATABASE_URL"
        
        # Run schema
        echo "🏗️  Creating database schema..."
        sleep 3
        docker exec -i mbp-postgres psql -U postgres -d mbp_prototype < schema.sql
        
        echo ""
        echo "✅ Database setup complete!"
        echo ""
        echo "Connection details:"
        echo "  Host: localhost"
        echo "  Port: 5432"
        echo "  Database: mbp_prototype"
        echo "  User: postgres"
        echo "  Password: postgres"
        echo ""
        echo "To stop: docker-compose down"
        echo "To view logs: docker-compose logs -f"
    else
        echo "❌ Failed to start PostgreSQL container"
        exit 1
    fi
else
    echo "❌ Docker not found"
    echo "Please install Docker or set up PostgreSQL manually"
    echo ""
    echo "For manual setup:"
    echo "1. Install PostgreSQL"
    echo "2. Create database: CREATE DATABASE mbp_prototype;"
    echo "3. Run: psql -d mbp_prototype -f schema.sql"
    echo "4. Set DATABASE_URL environment variable"
    exit 1
fi
