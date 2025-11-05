# Docker Deployment Guide

This guide covers how to deploy the LiteLLM Vector Store MCP Server using Docker for maximum portability and ease of distribution.

## Why Docker?

Docker provides several benefits for MCP server deployment:

- ✅ **Portability**: Works identically on any system with Docker installed
- ✅ **Isolation**: No conflicts with system Python or other packages
- ✅ **Easy Distribution**: Share via Docker Hub or private registry
- ✅ **Reproducibility**: Same environment every time
- ✅ **Security**: Runs as non-root user in isolated container

## Quick Start

### 1. Prerequisites

Install Docker Desktop:
- **MacOS**: [Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/)
- **Windows**: [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
- **Linux**: [Docker Engine](https://docs.docker.com/engine/install/)

### 2. Build the Docker Image

```bash
cd /Users/antoncoleman/Documents/repos/ai_development_environment/litellm-vector-store-mcp

# Build the image
docker build -t litellm-vector-store-mcp:latest .
```

### 3. Configure Environment Variables

Create or verify your `.env` file:

```bash
# Copy example if needed
cp .env.example .env

# Edit with your credentials
nano .env
```

Ensure these variables are set:
```env
LITELLM_API_KEY=sk-your-api-key
LITELLM_VECTOR_STORE_ID=2341871806232657920
LITELLM_BASE_URL=https://litellm.psolabs.com
VERTEX_AI_PROJECT=ngfw-coe
VERTEX_AI_LOCATION=us-east4
```

### 4. Run with Docker Compose

```bash
# Start the server
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the server
docker-compose down
```

### 5. Connect to Claude Code

See the **Claude Code Integration** section below.

---

## Docker Image Details

### Image Structure

The Docker image is built with:
- **Base**: Python 3.12 slim (minimal footprint)
- **User**: Non-root `mcp` user for security
- **Size**: ~200MB (optimized with multi-stage build)
- **Transport**: Stdio (standard input/output)

### Environment Variables

The container needs these environment variables (passed via `.env` file or docker-compose):

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LITELLM_API_KEY` | ✅ Yes | - | Your LiteLLM API key |
| `LITELLM_VECTOR_STORE_ID` | ✅ Yes | - | Vector store ID to search |
| `LITELLM_BASE_URL` | No | `https://litellm.psolabs.com` | LiteLLM server URL |
| `VERTEX_AI_PROJECT` | No | - | Google Cloud project |
| `VERTEX_AI_LOCATION` | No | `us-east4` | Vertex AI region |

---

## Claude Code Integration

### Method 1: Docker with Stdio (Recommended)

Add this configuration to your Claude Desktop config:

**MacOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "litellm-vector-store": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "--env-file",
        "/Users/antoncoleman/Documents/repos/ai_development_environment/litellm-vector-store-mcp/.env",
        "litellm-vector-store-mcp:latest"
      ]
    }
  }
}
```

**Key flags explained:**
- `--rm`: Automatically remove container when it stops
- `-i`: Keep stdin open (required for MCP stdio transport)
- `--env-file`: Load environment variables from your .env file
- Update the `--env-file` path to match your actual `.env` location

### Method 2: Docker Compose with Named Container

If you're running the server with docker-compose:

```json
{
  "mcpServers": {
    "litellm-vector-store": {
      "command": "docker",
      "args": [
        "exec",
        "-i",
        "litellm-vector-store-mcp",
        "python",
        "-u",
        "server.py"
      ]
    }
  }
}
```

**Prerequisites:**
- Container must be running: `docker-compose up -d`
- Container name must match: `litellm-vector-store-mcp`

### Method 3: Environment Variables Inline

Pass environment variables directly in the config:

```json
{
  "mcpServers": {
    "litellm-vector-store": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-e", "LITELLM_API_KEY=sk-your-key",
        "-e", "LITELLM_VECTOR_STORE_ID=2341871806232657920",
        "-e", "LITELLM_BASE_URL=https://litellm.psolabs.com",
        "-e", "VERTEX_AI_PROJECT=ngfw-coe",
        "-e", "VERTEX_AI_LOCATION=us-east4",
        "litellm-vector-store-mcp:latest"
      ]
    }
  }
}
```

⚠️ **Security Warning**: This exposes your API key in the config file. Method 1 (env-file) is more secure.

---

## Advanced Docker Usage

### Running Manually

Test the server manually:

```bash
# Run interactively
docker run -it --rm \
  --env-file .env \
  litellm-vector-store-mcp:latest

# Check logs
docker logs litellm-vector-store-mcp

# Execute commands in running container
docker exec -it litellm-vector-store-mcp /bin/bash
```

### Custom Docker Build

Build with specific Python version:

```bash
# Edit Dockerfile to change FROM line
# FROM python:3.11-slim as base

docker build -t litellm-vector-store-mcp:3.11 .
```

### Resource Limits

Adjust in `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'      # 2 CPU cores max
      memory: 1024M    # 1GB RAM max
    reservations:
      cpus: '1.0'      # 1 CPU core guaranteed
      memory: 512M     # 512MB RAM guaranteed
```

### Persistent Logging

Configure log rotation in `docker-compose.yml`:

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "50m"    # Max log file size
    max-file: "5"      # Keep 5 rotated files
```

---

## Distribution

### Pushing to Docker Hub

```bash
# Tag for Docker Hub
docker tag litellm-vector-store-mcp:latest yourusername/litellm-vector-store-mcp:latest

# Login to Docker Hub
docker login

# Push image
docker push yourusername/litellm-vector-store-mcp:latest
```

### Pulling from Docker Hub

Other developers can pull your image:

```bash
docker pull yourusername/litellm-vector-store-mcp:latest
```

### Private Registry

For internal distribution:

```bash
# Tag for private registry
docker tag litellm-vector-store-mcp:latest registry.company.com/litellm-vector-store-mcp:latest

# Push to private registry
docker push registry.company.com/litellm-vector-store-mcp:latest
```

---

## Troubleshooting

### Container Won't Start

Check logs:
```bash
docker logs litellm-vector-store-mcp
```

Common issues:
- ❌ **Missing environment variables**: Verify `.env` file exists and has required variables
- ❌ **Wrong .env path**: Ensure `--env-file` path is absolute, not relative
- ❌ **Port conflicts**: Not applicable for stdio transport (no ports used)

### Claude Can't Connect

1. **Verify image exists**:
   ```bash
   docker images | grep litellm-vector-store-mcp
   ```

2. **Test manually**:
   ```bash
   docker run -it --rm --env-file .env litellm-vector-store-mcp:latest
   ```

   Should show no errors. Press Ctrl+C to exit.

3. **Check Claude config**:
   - JSON must be valid (no trailing commas)
   - Paths must be absolute
   - Restart Claude Desktop after changes

### Permission Errors

If you see permission errors:

```bash
# Rebuild with correct user
docker build --no-cache -t litellm-vector-store-mcp:latest .

# Or run as root (not recommended)
docker run --user root ...
```

### Image Size Too Large

Optimize:

```bash
# Remove unused images
docker system prune -a

# Use slim base image (already done)
# Use multi-stage build (already done)
# Check .dockerignore includes test files
```

---

## Security Best Practices

### 1. Never Commit Secrets

Ensure `.env` is in `.gitignore`:
```bash
echo ".env" >> .gitignore
```

### 2. Use Docker Secrets

For production, use Docker secrets instead of env files:

```yaml
# docker-compose.yml
services:
  litellm-vector-store-mcp:
    secrets:
      - litellm_api_key

secrets:
  litellm_api_key:
    file: ./secrets/api_key.txt
```

### 3. Run as Non-Root

Our Dockerfile already does this:
```dockerfile
USER mcp
```

### 4. Scan for Vulnerabilities

```bash
# Use Docker Scout (built into Docker Desktop)
docker scout cves litellm-vector-store-mcp:latest

# Or use Trivy
docker run aquasec/trivy image litellm-vector-store-mcp:latest
```

---

## Performance Tuning

### Memory Optimization

Reduce image size:
- ✅ Using slim Python base image
- ✅ Multi-stage build
- ✅ .dockerignore excludes unnecessary files

### CPU Optimization

MCP servers are I/O bound, not CPU bound. Default limits are sufficient.

### Network Optimization

For remote Docker hosts, use HTTP transport instead of stdio:

```dockerfile
# Expose port for HTTP transport
EXPOSE 8080

# Use HTTP server
CMD ["python", "-u", "server_http.py"]
```

(Note: HTTP transport implementation not included in this version)

---

## Next Steps

1. ✅ Build the Docker image
2. ✅ Test locally with docker-compose
3. ✅ Configure Claude Desktop
4. ✅ Test search functionality
5. 📦 Optionally push to Docker Hub for easy distribution

For usage examples and advanced features, see [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md).
