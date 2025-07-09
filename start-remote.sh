#!/bin/bash

echo "🚀 Starting Job Application Tracker with Remote Temporal Cloud"
echo "=============================================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please ensure .env file exists with required environment variables:"
    echo "- GEMINI_API_KEY"
    echo "- TEMPORAL_API_KEY" 
    echo "- TEMPORAL_ADDRESS"
    echo "- TEMPORAL_NAMESPACE"
    exit 1
fi

echo "✅ Environment file found"

# Load environment variables
set -a
source .env
set +a

echo "🔧 Configuration:"
echo "- Temporal Address: $TEMPORAL_ADDRESS"
echo "- Temporal Namespace: $TEMPORAL_NAMESPACE"
echo "- App Name: $APP_NAME"

echo ""
echo "🏗️  Building and starting services..."

# Start services with remote configuration
docker-compose -f docker-compose.remote.yml up --build

echo ""
echo "🌐 Application URLs:"
echo "- Frontend: http://localhost:3000"
echo "- Backend API: http://localhost:8000"
echo "- API Documentation: http://localhost:8000/docs"