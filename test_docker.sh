#!/bin/bash
# Test script for Docker containerized MCP server

set -e

echo "=== Docker Container Test Suite ==="
echo ""

# Test 1: Verify image exists
echo "Test 1: Verifying Docker image exists..."
if docker images | grep -q "suno-mcp-server"; then
    echo "✓ Image found: suno-mcp-server:latest"
else
    echo "✗ Image not found!"
    exit 1
fi
echo ""

# Test 2: Health check
echo "Test 2: Running health check..."
if docker run --rm -i --env-file .env suno-mcp-server:latest python healthcheck.py; then
    echo "✓ Health check passed"
else
    echo "✗ Health check failed!"
    exit 1
fi
echo ""

# Test 3: Verify server can start (run for 2 seconds then stop)
echo "Test 3: Testing server startup..."
timeout 2 docker run --rm -i --env-file .env suno-mcp-server:latest 2>&1 | grep -q "Suno MCP Server initialized successfully"
TEST_EXIT=$?
if [ $TEST_EXIT -eq 0 ]; then
    echo "✓ Server started successfully"
else
    echo "✗ Server failed to start!"
    exit 1
fi
echo ""

# Test 4: Verify environment variables are loaded
echo "Test 4: Verifying environment variables..."
docker run --rm -i --env-file .env suno-mcp-server:latest python -c "import os; assert os.getenv('SUNO_API_KEY'), 'API key not loaded'; print('API Key loaded successfully')"
echo "✓ Environment variables loaded correctly"
echo ""

echo "=== All Docker tests passed! ==="
echo ""
echo "Container is ready for use with Claude Code MCP client."
