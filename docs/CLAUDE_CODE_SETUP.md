# Claude Code / Claude Desktop Setup Guide

Complete guide for connecting the LiteLLM Vector Store MCP Server to Claude Desktop and Claude Code over stdio transport.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Configuration Methods](#configuration-methods)
3. [Docker Setup](#docker-setup-recommended)
4. [Python Setup](#python-setup)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Prerequisites

- Claude Desktop installed
- Docker installed (for Docker method) OR Python 3.10+ (for Python method)
- Your LiteLLM API credentials

### 3-Step Setup

1. **Choose deployment method**: Docker (recommended) or Python
2. **Add MCP server config** to Claude Desktop
3. **Restart Claude Desktop**

---

## Configuration Methods

Claude Desktop uses a JSON configuration file to define available MCP servers.

### Config File Location

**MacOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**Linux**: `~/.config/Claude/claude_desktop_config.json`

### Creating the Config File

If the file doesn't exist, create it:

```bash
# MacOS
mkdir -p ~/Library/Application\ Support/Claude
touch ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Linux
mkdir -p ~/.config/Claude
touch ~/.config/Claude/claude_desktop_config.json
```

---

## Docker Setup (Recommended)

### Advantages

- ✅ No Python environment conflicts
- ✅ Easy to distribute and update
- ✅ Consistent across all platforms
- ✅ Isolated from system packages

### Step 1: Build Docker Image

```bash
cd /Users/antoncoleman/Documents/repos/ai_development_environment/litellm-vector-store-mcp

# Build the image
docker build -t litellm-vector-store-mcp:latest .

# Verify it built successfully
docker images | grep litellm-vector-store-mcp
```

### Step 2: Configure .env File

Create or verify your `.env` file in the project directory:

```env
LITELLM_API_KEY=sk-your-api-key-here
LITELLM_VECTOR_STORE_ID=2341871806232657920
LITELLM_BASE_URL=https://litellm.psolabs.com
VERTEX_AI_PROJECT=ngfw-coe
VERTEX_AI_LOCATION=us-east4
```

### Step 3: Add to Claude Desktop Config

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

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

**Important**:
- Use **absolute paths** for the `--env-file` argument
- Update the path to match your actual project location
- Ensure `.env` file exists at that path

### Step 4: Restart Claude Desktop

1. Quit Claude Desktop completely (Cmd+Q on Mac)
2. Reopen Claude Desktop
3. The MCP server should now be available

---

## Python Setup

### Advantages

- ✅ Direct access to source code
- ✅ Easier to debug
- ✅ No Docker required

### Step 1: Install Dependencies

```bash
cd /Users/antoncoleman/Documents/repos/ai_development_environment/litellm-vector-store-mcp

# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Test Configuration

```bash
# Verify .env file exists
cat .env

# Test the server
python test_config.py
```

You should see:
```
✓ SUCCESS! Vector store is accessible
```

### Step 3: Add to Claude Desktop Config

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "litellm-vector-store": {
      "command": "python3",
      "args": [
        "/Users/antoncoleman/Documents/repos/ai_development_environment/litellm-vector-store-mcp/server.py"
      ],
      "cwd": "/Users/antoncoleman/Documents/repos/ai_development_environment/litellm-vector-store-mcp"
    }
  }
}
```

**Important**:
- Use **absolute paths** for the `args` value
- The `cwd` (current working directory) should point to the project directory
- This ensures the `.env` file is loaded correctly

### Alternative: Using Virtual Environment

If using a virtual environment:

```json
{
  "mcpServers": {
    "litellm-vector-store": {
      "command": "/Users/antoncoleman/Documents/repos/ai_development_environment/litellm-vector-store-mcp/venv/bin/python",
      "args": [
        "/Users/antoncoleman/Documents/repos/ai_development_environment/litellm-vector-store-mcp/server.py"
      ]
    }
  }
}
```

### Step 4: Restart Claude Desktop

1. Quit Claude Desktop completely (Cmd+Q on Mac)
2. Reopen Claude Desktop
3. The MCP server should now be available

---

## Verification

### 1. Check MCP Server is Loaded

After restarting Claude Desktop:

1. Open Claude Desktop
2. Start a new conversation
3. Type: **"What tools are available?"**
4. You should see `litellm_search_vector_store` in the list

### 2. Test the Tool

Ask Claude:

```
Search the vector store for "Redis configuration"
```

Claude should:
1. Use the `litellm_search_vector_store` tool
2. Return search results with file paths and content

### 3. Verify Results Format

Results should look like:

```markdown
# Vector Store Search Results

**Query:** Redis configuration
**Results Found:** 5

## Result 1: redis-stack.yaml.txt

- **Relevance Score:** 0.3118
- **File Path:** `gs://ngfw-coe-rag-corpora/.rag/.../redis-stack.yaml.txt`

### Content:
[Redis configuration content...]
```

---

## Troubleshooting

### MCP Server Not Appearing

**Check 1: Verify JSON Syntax**
```bash
# Validate JSON
python3 -c "import json; json.load(open('~/Library/Application Support/Claude/claude_desktop_config.json'))"
```

Common JSON errors:
- ❌ Trailing commas: `"key": "value",}`
- ❌ Missing quotes: `{command: "docker"}`
- ❌ Wrong quote types: `{'command': 'docker'}`

**Check 2: Verify Paths are Absolute**
```bash
# Test Docker image exists
docker images | grep litellm-vector-store-mcp

# Test Python script exists
ls -la /Users/antoncoleman/Documents/repos/ai_development_environment/litellm-vector-store-mcp/server.py

# Test .env file exists
ls -la /Users/antoncoleman/Documents/repos/ai_development_environment/litellm-vector-store-mcp/.env
```

**Check 3: Restart Claude Desktop Properly**
- Don't just close the window - **fully quit** the app (Cmd+Q)
- Wait 5 seconds
- Reopen Claude Desktop

### Tool Execution Fails

**Check 1: Test Server Manually**

For Docker:
```bash
docker run -it --rm \
  --env-file /Users/antoncoleman/Documents/repos/ai_development_environment/litellm-vector-store-mcp/.env \
  litellm-vector-store-mcp:latest
```

For Python:
```bash
cd /Users/antoncoleman/Documents/repos/ai_development_environment/litellm-vector-store-mcp
python server.py
```

Both should run without errors. Press Ctrl+C to exit.

**Check 2: Verify Environment Variables**

```bash
# Check .env file contents
cat /Users/antoncoleman/Documents/repos/ai_development_environment/litellm-vector-store-mcp/.env

# Ensure required vars are set
grep LITELLM_API_KEY .env
grep LITELLM_VECTOR_STORE_ID .env
```

**Check 3: Test Vector Store Access**

```bash
python test_config.py
```

Should show:
```
✓ SUCCESS! Vector store is accessible
```

### Permission Errors

**Docker Permission Denied**
```bash
# Add user to docker group (Linux/Mac)
sudo usermod -aG docker $USER

# Or run docker with sudo (not recommended)
sudo docker run ...
```

**Python Permission Denied**
```bash
# Make server.py executable
chmod +x server.py

# Check file permissions
ls -la server.py
```

### Network/Connection Errors

**Check 1: Test Network Connectivity**
```bash
curl https://litellm.psolabs.com
```

**Check 2: Verify API Key**
```bash
# Test with curl
curl -H "Authorization: Bearer sk-your-key" \
  https://litellm.psolabs.com/v1/models
```

**Check 3: Check Firewall/Proxy**
- Ensure outbound HTTPS (port 443) is allowed
- Configure proxy if needed (add `HTTP_PROXY` to .env)

### Claude Desktop Logs

View Claude Desktop logs for detailed error information:

**MacOS**:
```bash
# View logs
tail -f ~/Library/Logs/Claude/mcp*.log

# Or use Console.app and filter for "Claude"
```

**Linux**:
```bash
tail -f ~/.config/Claude/logs/mcp*.log
```

---

## Advanced Configuration

### Multiple MCP Servers

You can configure multiple MCP servers:

```json
{
  "mcpServers": {
    "litellm-vector-store": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "--env-file", "/path/to/.env", "litellm-vector-store-mcp:latest"]
    },
    "another-mcp-server": {
      "command": "python3",
      "args": ["/path/to/another_server.py"]
    }
  }
}
```

### Custom Environment Variables

Override specific variables:

```json
{
  "mcpServers": {
    "litellm-vector-store": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-e", "LITELLM_VECTOR_STORE_ID=different-store-id",
        "--env-file", "/path/to/.env",
        "litellm-vector-store-mcp:latest"
      ]
    }
  }
}
```

### Using Different Docker Images

Switch between versions:

```json
{
  "mcpServers": {
    "litellm-vector-store-prod": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "--env-file", "/path/.env", "litellm-vector-store-mcp:1.0.0"]
    },
    "litellm-vector-store-dev": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "--env-file", "/path/.env", "litellm-vector-store-mcp:dev"]
    }
  }
}
```

---

## Best Practices

### Security

1. ✅ **Never commit your `.env` file** to version control
2. ✅ **Use absolute paths** in Claude Desktop config
3. ✅ **Keep API keys in `.env`**, not in the JSON config
4. ✅ **Restrict .env file permissions**:
   ```bash
   chmod 600 .env
   ```

### Performance

1. ✅ **Use Docker method** for better isolation
2. ✅ **Restart Claude Desktop** after config changes
3. ✅ **Monitor resource usage** if running multiple MCP servers

### Maintenance

1. ✅ **Keep dependencies updated**:
   ```bash
   pip install --upgrade -r requirements.txt
   ```

2. ✅ **Rebuild Docker images** periodically:
   ```bash
   docker build --no-cache -t litellm-vector-store-mcp:latest .
   ```

3. ✅ **Test after updates**:
   ```bash
   python test_config.py
   ```

---

## Getting Help

If you're still having issues:

1. Check the [TROUBLESHOOTING section](#troubleshooting) above
2. Review [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) for Docker-specific issues
3. Check [README.md](README.md) for general documentation
4. Verify your configuration matches the examples exactly

---

## Summary

### Docker Method (Recommended)

```bash
# 1. Build image
docker build -t litellm-vector-store-mcp:latest .

# 2. Create .env with credentials

# 3. Add to Claude config:
{
  "mcpServers": {
    "litellm-vector-store": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "--env-file", "/absolute/path/.env", "litellm-vector-store-mcp:latest"]
    }
  }
}

# 4. Restart Claude Desktop
```

### Python Method

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Test config
python test_config.py

# 3. Add to Claude config:
{
  "mcpServers": {
    "litellm-vector-store": {
      "command": "python3",
      "args": ["/absolute/path/server.py"],
      "cwd": "/absolute/path/to/project"
    }
  }
}

# 4. Restart Claude Desktop
```

You're now ready to use the LiteLLM Vector Store MCP Server with Claude! 🚀
