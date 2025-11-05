# Multi-stage build for optimal image size
FROM python:3.12-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash mcp

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY server.py .

# Switch to non-root user
USER mcp

# Set up stdio transport for MCP
# MCP servers communicate via stdin/stdout
ENTRYPOINT ["python", "-u", "server.py"]

# Metadata
LABEL org.opencontainers.image.title="LiteLLM Vector Store MCP Server" \
      org.opencontainers.image.description="MCP server for searching LiteLLM vector stores" \
      org.opencontainers.image.vendor="Your Organization" \
      org.opencontainers.image.version="0.1.0"
