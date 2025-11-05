# LiteLLM Vector Store MCP Server

A production-ready [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that enables Claude to semantically search your LiteLLM vector stores for relevant code, documentation, and configuration files.

[![MCP Compliant](https://img.shields.io/badge/MCP-Compliant-green)]( https://modelcontextprotocol.io)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

## ✨ Features

- 🔍 **Semantic Search**: Search your entire codebase using natural language queries
- 📚 **Multi-Vector Store**: Search across 7+ different framework codebases dynamically
- 🔄 **Auto-Discovery**: Lists available vector stores automatically from LiteLLM API
- 📊 **Multiple Formats**: Get results as Markdown (human-readable) or JSON (programmatic)
- 📄 **Full Citations**: File paths, relevance scores, and content snippets with every result
- 🔒 **Secure**: Environment variable expansion, no plaintext API keys in configs
- 🐳 **Docker Ready**: Production-grade containerization for easy deployment
- 🚀 **MCP Compliant**: Follows all official MCP best practices with FastMCP
- 💬 **Claude Code Integration**: Native CLI commands and .mcp.json support
- ⚡ **Async I/O**: Non-blocking HTTP requests with httpx
- ✅ **Input Validation**: Pydantic V2 models ensure type safety
- 🎯 **Actionable Errors**: Clear, helpful error messages that guide you to solutions

## 🚀 Quick Start

**Get running in 5 minutes:** See **[QUICKSTART.md](QUICKSTART.md)** for complete setup guide.

### 🐳 Docker Image

**Pre-built image available in GCP Artifact Registry:**
```
us-central1-docker.pkg.dev/ngfw-coe/litellm-vector-store-mcp/litellm-vector-store-mcp:latest
```

**No build required!** Just pull and configure.

### One-Command Setup (Secure Method)

```bash
# 1. Configure Docker for GCP and pull image
gcloud auth configure-docker us-central1-docker.pkg.dev --quiet
docker pull us-central1-docker.pkg.dev/ngfw-coe/litellm-vector-store-mcp/litellm-vector-store-mcp:latest

# 2. Add credentials to shell (SECURE - not in config files)
cat >> ~/.zshrc << 'EOF'
export LITELLM_API_KEY=sk-your-api-key
export LITELLM_VECTOR_STORE_ID=2341871806232657920
EOF
source ~/.zshrc

# 3. Add MCP server with environment variable expansion
claude mcp add-json --scope user litellm-vector-store '{
  "type": "stdio",
  "command": "docker",
  "args": [
    "run", "-i", "--rm",
    "-e", "LITELLM_API_KEY=${LITELLM_API_KEY}",
    "-e", "LITELLM_VECTOR_STORE_ID=${LITELLM_VECTOR_STORE_ID:-2341871806232657920}",
    "-e", "LITELLM_BASE_URL=${LITELLM_BASE_URL:-https://litellm.psolabs.com}",
    "us-central1-docker.pkg.dev/ngfw-coe/litellm-vector-store-mcp/litellm-vector-store-mcp:latest"
  ]
}'

# 4. Restart Claude Code completely (Cmd+Q, then reopen)
```

🔒 **Security:** API key in shell environment, config uses `${LITELLM_API_KEY}` (no plaintext).

### Verify Setup

```bash
# Check server is loaded
claude mcp list

# Should show: litellm-vector-store (stdio) - user scope
```

### Test with Claude

Ask Claude:
```
What vector stores are available?
```

Should list all 7 of your vector stores!

---

## 📚 Documentation

### User Guides

| Guide | Purpose |
|-------|---------|
| **[QUICKSTART.md](QUICKSTART.md)** ⭐ | **START HERE** - 5-minute Claude Code setup with secure config |
| **[SECURITY.md](SECURITY.md)** 🔒 | Secure API key management and best practices |
| **[USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)** | How Claude interprets search results |
| **[CLAUDE_CODE_SETUP.md](CLAUDE_CODE_SETUP.md)** | Detailed Claude Desktop/Code integration guide |
| **[DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)** | Docker deployment and distribution |

### Developer Guides

| Guide | Purpose |
|-------|---------|
| **[IMPROVEMENTS_SUMMARY.md](IMPROVEMENTS_SUMMARY.md)** | All MCP best practices applied |
| **[docs/MULTI_STORE_USAGE.md](docs/MULTI_STORE_USAGE.md)** | Multi-vector store usage and examples |
| **[docs/](docs/)** | Technical documentation and architecture |
| `test_config.py` | Configuration validator |
| `test_multi_store.py` | Multi-store feature tests |

---

## 🎯 Available Tools

### `litellm_list_vector_stores`

Discover all available vector stores in your LiteLLM instance.

**Parameters:**
- `response_format` (string, optional): Output format - "markdown" or "json" (default: "markdown")

**Example Usage with Claude:**
```
What vector stores are available?
```

**Returns:** List of 7+ vector stores with IDs, names, and descriptions.

---

### `litellm_search_vector_store`

Search vector stores using natural language queries with full citations.

**Parameters:**
- `query` (string, required): Natural language search query (2-500 chars)
- `max_results` (integer, optional): Number of results to return (1-20, default: 5)
- `response_format` (string, optional): Output format - "markdown" or "json" (default: "markdown")
- `vector_store` (string, optional): Vector store name or ID to search (default: uses LITELLM_VECTOR_STORE_ID)

**Example:**

```json
{
  "query": "How is authentication implemented?",
  "max_results": 10,
  "response_format": "markdown",
  "vector_store": "panser-corpus"
}
```

**Example Usage with Claude:**
```
Search panser-corpus for authentication code
Find Redis configuration in internal-corpus
Compare Docker setups across all frameworks
```

**Returns:**

Markdown format (default):
```markdown
# Vector Store Search Results

**Query:** How is the GKE cluster configured?
**Results Found:** 5

## Result 1: main.tf.txt
- **Relevance Score:** 0.3948
- **File Path:** `gs://...`
### Content:
[Terraform code...]
```

JSON format:
```json
{
  "query": "How is the GKE cluster configured?",
  "total_results": 5,
  "truncated": false,
  "results": [
    {
      "score": 0.3948,
      "filename": "main.tf.txt",
      "file_id": "gs://...",
      "content": "...",
      "attributes": {}
    }
  ]
}
```

---

## 🐳 Docker Deployment

### Build & Run

```bash
# Build image
docker build -t litellm-vector-store-mcp:latest .

# Run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Distribution

Push to Docker Hub for easy sharing:

```bash
docker tag litellm-vector-store-mcp:latest yourusername/litellm-vector-store-mcp:latest
docker push yourusername/litellm-vector-store-mcp:latest
```

Others can then pull and use:

```bash
docker pull yourusername/litellm-vector-store-mcp:latest
```

See **[DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)** for complete Docker guide.

---

## 🔧 Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LITELLM_API_KEY` | ✅ Yes | - | Your LiteLLM API key |
| `LITELLM_VECTOR_STORE_ID` | ✅ Yes | - | Vector store ID to search |
| `LITELLM_BASE_URL` | No | `https://litellm.psolabs.com` | LiteLLM server URL<br>Or use: `http://localhost:5600` (gcloud proxy) |
| `VERTEX_AI_PROJECT` | No | - | Google Cloud project |
| `VERTEX_AI_LOCATION` | No | `us-east4` | Vertex AI region |

**Note:** For gcloud proxy setup, see [Advanced Configuration in QUICKSTART.md](QUICKSTART.md#using-gcloud-proxy-alternative-to-direct-connection)

### Test Configuration

```bash
python test_config.py
```

Expected output:
```
✓ SUCCESS! Vector store is accessible
  Found 10 results for test query
```

---

## 🎓 MCP Best Practices

This server follows all official MCP best practices:

✅ **FastMCP Framework**: Automatic schema generation from type hints
✅ **Pydantic V2 Validation**: Type-safe input validation
✅ **Tool Annotations**: `readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`
✅ **Response Formats**: Both JSON and Markdown supported
✅ **Character Limits**: 25,000 character limit with smart truncation
✅ **Actionable Errors**: Clear messages that guide users to solutions
✅ **Async I/O**: Non-blocking HTTP requests with httpx
✅ **Type Hints**: Complete type coverage throughout
✅ **Comprehensive Docs**: Detailed docstrings for all functions

See **[IMPROVEMENTS_SUMMARY.md](IMPROVEMENTS_SUMMARY.md)** for complete details.

---

## 📖 Usage Examples

### Basic Search

Ask Claude:
```
Search the vector store for how Redis is configured
```

Claude will:
1. Call `litellm_search_vector_store` with query="how Redis is configured"
2. Receive results with file paths and content
3. Interpret and explain the configuration

### Advanced Search

Ask Claude:
```
Find all Terraform modules related to GKE, return 10 results in JSON format
```

Claude will:
1. Call the tool with `max_results=10` and `response_format="json"`
2. Receive structured JSON data
3. Process and present the findings

### Follow-up Questions

```
Based on those results, how does the GKE module differ from the bastion module?
```

Claude will:
1. Search for both modules
2. Compare implementations
3. Explain key differences

See **[USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)** for more examples.

---

## 🔐 Security

**See [SECURITY.md](SECURITY.md) for complete security guide.**

### Recommended Setup (Secure)

✅ **Use environment variable expansion** - API keys in shell environment, not config files:

```bash
# In ~/.zshrc
export LITELLM_API_KEY=sk-your-key
export LITELLM_VECTOR_STORE_ID=2341871806232657920

# In MCP config
"-e", "LITELLM_API_KEY=${LITELLM_API_KEY}"  // References env var, not plaintext
```

### Best Practices

- ✅ **Environment variables**: Use `${VAR}` expansion in configs (no plaintext keys)
- ✅ **Shell environment**: Store credentials in `~/.zshrc` or separate file
- ✅ **Non-root container**: Runs as `mcp` user (UID 1000)
- ✅ **Input validation**: Pydantic validates all user inputs
- ✅ **Startup validation**: Checks API key exists before starting
- ✅ **Restart required**: Claude Code must restart after adding env vars

### Security Levels

| Method | Security | Setup |
|--------|----------|-------|
| **Plaintext in config** | ❌ Poor | Easy |
| **Environment variables** | ✅ Good | Easy |
| **Docker env-file** | ✅✅ Better | Medium |
| **macOS Keychain** | ✅✅✅ Best | Medium |

See **[SECURITY.md](SECURITY.md)** for detailed implementation of each method.

---

## 🛠️ Troubleshooting

### Authentication Failed Error

**Error:** `"Error: Authentication failed. Please check your LITELLM_API_KEY..."`

**Cause:** Environment variables not loaded in Claude Code session

**Solution:**
```bash
# 1. Verify env vars are in ~/.zshrc
tail -5 ~/.zshrc  # Should show export LITELLM_API_KEY=...

# 2. COMPLETELY RESTART Claude Code (Cmd+Q, then reopen)
# Environment variables are only loaded when Claude Code starts

# 3. Verify in new terminal
echo $LITELLM_API_KEY | head -c 10  # Should show: sk-a8d9e2b
```

### Server Won't Start

```bash
# Check environment variables
python test_config.py

# Test Docker manually
docker run -i --rm -e LITELLM_API_KEY=$LITELLM_API_KEY \
  -e LITELLM_VECTOR_STORE_ID=$LITELLM_VECTOR_STORE_ID \
  litellm-vector-store-mcp:latest
```

### Claude Can't See Tool

1. Verify config with: `claude mcp list`
2. Check JSON syntax in `.mcp.json` or `~/.claude.json`
3. Use absolute paths (not relative)
4. **Restart Claude Code completely** (Cmd+Q)

### Search Returns No Results

1. Use `litellm_list_vector_stores` to see available stores
2. Verify vector store ID or name is correct
3. Try broader search terms
4. Check API key has access to that specific vector store

See **[CLAUDE_CODE_SETUP.md](CLAUDE_CODE_SETUP.md#troubleshooting)** and **[SECURITY.md](SECURITY.md)** for complete guides.

---

## 🤝 Contributing

Contributions welcome! This server follows:

- **MCP Best Practices**: All official guidelines
- **Type Safety**: Pydantic models + type hints
- **Documentation**: Comprehensive docstrings
- **Testing**: Validate with `test_config.py`

---

## 📜 License

MIT License - feel free to modify and distribute

---

## 🔗 Resources

- [MCP Protocol Documentation](https://modelcontextprotocol.io)
- [LiteLLM Documentation](https://docs.litellm.ai)
- [FastMCP Framework](https://github.com/modelcontextprotocol/python-sdk)
- [Pydantic Documentation](https://docs.pydantic.dev/)

---

## 🚀 Quick Reference

### Docker Commands

```bash
# Configure Docker for GCP
gcloud auth configure-docker us-central1-docker.pkg.dev --quiet

# Pull image from Artifact Registry
docker pull us-central1-docker.pkg.dev/ngfw-coe/litellm-vector-store-mcp/litellm-vector-store-mcp:latest

# Run
docker run --rm -i \
  -e LITELLM_API_KEY=$LITELLM_API_KEY \
  -e LITELLM_VECTOR_STORE_ID=$LITELLM_VECTOR_STORE_ID \
  us-central1-docker.pkg.dev/ngfw-coe/litellm-vector-store-mcp/litellm-vector-store-mcp:latest

# Build locally (only if modifying)
docker build -t us-central1-docker.pkg.dev/ngfw-coe/litellm-vector-store-mcp/litellm-vector-store-mcp:latest .
docker push us-central1-docker.pkg.dev/ngfw-coe/litellm-vector-store-mcp/litellm-vector-store-mcp:latest
```

### Python Commands

```bash
# Install
pip install -r requirements.txt

# Test
python test_config.py

# Run
python server.py
```

### Claude Integration

```bash
# Edit config
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Restart Claude
killall Claude && open -a Claude
```

---

## 📈 Status

- ✅ MCP Protocol Compliant
- ✅ Production Ready
- ✅ Docker Containerized
- ✅ Fully Documented
- ✅ Type Safe
- ✅ Security Hardened

**Ready to deploy and distribute! 🎉**
