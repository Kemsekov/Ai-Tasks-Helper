#!/bin/bash

echo "Testing the AI Task Manager API..."

# Test the health endpoint
echo "1. Testing health endpoint:"
curl -s -w "\n%{http_code}\n" http://localhost:8001/health

echo ""
echo "2. Testing root endpoint:"
curl -s -w "\n%{http_code}\n" http://localhost:8001/

echo ""
echo "3. Testing docs endpoint:"
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8001/docs

echo ""
echo "If the server is running properly, you should see the API documentation at http://localhost:8001/docs"