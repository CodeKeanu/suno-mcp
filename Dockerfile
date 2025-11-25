# Suno MCP Server - Docker Image
# Multi-stage build for optimal security and size

# Use official Python 3.12 slim image as base
FROM python:3.12-slim

# Set environment variables for Python optimization
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing pyc files
# PYTHONUNBUFFERED: Ensures logs aren't buffered (prevents silent crashes)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Create a non-root user for security
# Running as non-root minimizes security risks
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Copy requirements first for better layer caching
# This allows Docker to reuse this layer when only code changes
COPY --chown=appuser:appuser requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=appuser:appuser server.py .
COPY --chown=appuser:appuser suno_client.py .
COPY --chown=appuser:appuser healthcheck.py .

# Switch to non-root user
USER appuser

# Add healthcheck to monitor container status
# Checks every 30s, with 5s timeout, 3 retries before unhealthy
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python healthcheck.py || exit 1

# Set the entrypoint to run the MCP server
# The server communicates via stdio (stdin/stdout)
ENTRYPOINT ["python", "server.py"]
