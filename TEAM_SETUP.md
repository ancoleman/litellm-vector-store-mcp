# Team Setup Guide

Quick setup guide for team members to use the LiteLLM Vector Store MCP Server.

## 🎯 For Team Members

If your team lead has already published the Docker image, you can get up and running in **2 minutes**.

---

## ⚡ Quick Setup (2 Steps)

### Step 1: Configure Docker & Pull Image

```bash
# Configure Docker authentication for GCP Artifact Registry
gcloud auth configure-docker us-central1-docker.pkg.dev --quiet

# Pull the pre-built image
docker pull us-central1-docker.pkg.dev/ngfw-coe/litellm-vector-store-mcp/litellm-vector-store-mcp:latest
```

### Step 2: Add Your Credentials & Configure MCP

```bash
# Add credentials to your shell environment
cat >> ~/.zshrc << 'EOF'

# LiteLLM MCP Server credentials
export LITELLM_API_KEY=sk-your-api-key-here
export LITELLM_VECTOR_STORE_ID=1111111111111111111
EOF

# Reload shell
source ~/.zshrc

# Add MCP server to Claude Code
claude mcp add-json --scope user litellm-vector-store '{
  "type": "stdio",
  "command": "docker",
  "args": [
    "run", "-i", "--rm",
    "-e", "LITELLM_API_KEY=${LITELLM_API_KEY}",
    "-e", "LITELLM_VECTOR_STORE_ID=${LITELLM_VECTOR_STORE_ID:-1111111111111111111}",
    "-e", "LITELLM_BASE_URL=${LITELLM_BASE_URL:-https://litellm.psolabs.com}",
    "-e", "VERTEX_AI_PROJECT=${VERTEX_AI_PROJECT:-ngfw-coe}",
    "-e", "VERTEX_AI_LOCATION=${VERTEX_AI_LOCATION:-us-east4}",
    "us-central1-docker.pkg.dev/ngfw-coe/litellm-vector-store-mcp/litellm-vector-store-mcp:latest"
  ]
}'

# Restart Claude Code (Cmd+Q, then reopen)
```

**Done!** You can now search all 7 framework vector stores.

---

## 🔑 Getting Your API Key

Ask your team lead for:
1. **LITELLM_API_KEY** - Your personal LiteLLM API key
2. **LITELLM_VECTOR_STORE_ID** (optional) - Default vector store ID (or use 1111111111111111111)
3. **LITELLM_BASE_URL** (optional) - LiteLLM server URL
   - Direct: `https://litellm.psolabs.com` (default)
   - Via proxy: `http://localhost:5600` (if using gcloud IAP tunnel)

---

## ✅ Verification

### Check MCP Server is Loaded

```bash
claude mcp list
```

Should show:
```
litellm-vector-store (stdio) - user scope
  Status: ✓ Connected
```

### Test with Claude

Open Claude Code and ask:
```
What vector stores are available?
```

Should list:
```
1. panser-corpus - Panser framework
2. migrationmanager-corpus - Migration Manager
3. companion-corpus - Companion framework
4. mcp-servers-corpus - MCP Servers
5. prismaautomation-corpus - Prisma Automation
6. internal-corpus - Internal/LiteLLM deployment
7. gcsai-corpus - GCSAI framework
```

---

## 🎓 Usage Examples

Once set up, you can ask Claude:

### Discover Vector Stores
```
What vector stores can I search?
```

### Search Specific Framework
```
Search panser-corpus for authentication code
Find deployment scripts in internal-corpus
Show me MCP server examples in mcp-servers-corpus
```

### Cross-Framework Comparison
```
How do different frameworks handle authentication?
Compare Docker setups across all frameworks
Find the best Redis configuration examples
```

### Multi-Store Search
```
Search all frameworks for Terraform modules
Which codebase has the best API documentation?
```

---

## 🐛 Troubleshooting

### Authentication Failed Error

**Error:** `"Error: Authentication failed. Please check your LITELLM_API_KEY..."`

**Cause:** Environment variables not loaded

**Solution:**
```bash
# 1. Verify env vars are set
echo $LITELLM_API_KEY | head -c 10  # Should show: sk-...

# 2. If empty, check ~/.zshrc
tail -5 ~/.zshrc  # Should show export LITELLM_API_KEY=...

# 3. Reload if needed
source ~/.zshrc

# 4. COMPLETELY RESTART Claude Code (Cmd+Q, then reopen)
```

### Docker Pull Failed

**Error:** `denied: Permission "artifactregistry.repositories.downloadArtifacts" denied`

**Solution:**
```bash
# Ensure you're authenticated with GCP
gcloud auth login

# Configure Docker for Artifact Registry
gcloud auth configure-docker us-central1-docker.pkg.dev --quiet

# Try pull again
docker pull us-central1-docker.pkg.dev/ngfw-coe/litellm-vector-store-mcp/litellm-vector-store-mcp:latest
```

### MCP Server Not Listed

**Solution:**
```bash
# Verify Docker image exists
docker images | grep litellm-vector-store-mcp

# Check MCP configuration
claude mcp get litellm-vector-store

# If broken, remove and re-add
claude mcp remove litellm-vector-store
# Then run Step 2 again
```

---

## 🔄 Updating to New Version

When a new version is released:

```bash
# Pull latest version
docker pull us-central1-docker.pkg.dev/ngfw-coe/litellm-vector-store-mcp/litellm-vector-store-mcp:latest

# Restart Claude Code (Cmd+Q, then reopen)
```

No configuration changes needed!

---

## 📦 What You DON'T Need

**You don't need:**
- ❌ Source code repository
- ❌ Python environment
- ❌ To build Docker image locally
- ❌ requirements.txt or dependencies
- ❌ To worry about your CPU architecture (multi-platform support!)

**You only need:**
- ✅ Docker installed (Windows WSL2, macOS, or Linux)
- ✅ GCP access to ngfw-coe project
- ✅ Your LiteLLM API credentials
- ✅ Claude Code installed

**Platform Support:**
- ✅ Windows (WSL2) - linux/amd64
- ✅ macOS Intel - linux/amd64
- ✅ macOS Apple Silicon (M1/M2/M3) - linux/arm64
- ✅ Linux x86_64 - linux/amd64
- ✅ Linux ARM64 - linux/arm64

Docker automatically downloads the correct image for your system!

---

## 🔐 Security Notes

### Your API Key

- ✅ Stored in `~/.zshrc` (private shell config)
- ✅ Config uses `${LITELLM_API_KEY}` (no plaintext)
- ✅ Never commit your API key
- ✅ Each team member has their own key

### File Permissions

```bash
# Restrict your shell config (recommended)
chmod 600 ~/.zshrc
```

---

## 🌐 Alternative: Using gcloud Proxy

**If your organization requires gcloud IAP tunnel access:**

### Setup gcloud Proxy

```bash
# Start IAP tunnel in a separate terminal (keep running)
gcloud compute start-iap-tunnel litellm-proxy 443 \
  --local-host-port=localhost:5600 \
  --zone=your-zone \
  --project=ngfw-coe
```

### Update Your .env or Shell Config

```bash
# Instead of direct URL, use localhost proxy
export LITELLM_BASE_URL=http://localhost:5600

# Or in .env file:
# LITELLM_BASE_URL=http://localhost:5600
```

### Important: Docker Networking

When using localhost proxy, add `--network host` to Docker args:

```bash
claude mcp add-json --scope user litellm-vector-store '{
  "type": "stdio",
  "command": "docker",
  "args": [
    "run", "-i", "--rm",
    "--network", "host",
    "--env-file", "/path/to/.env",
    "us-central1-docker.pkg.dev/ngfw-coe/litellm-vector-store-mcp/litellm-vector-store-mcp:latest"
  ]
}'
```

**The `--network host` allows the Docker container to access localhost:5600 on your machine.**

---

## 📞 Getting Help

### If Something Doesn't Work

1. Check this troubleshooting section first
2. Verify prerequisites are installed
3. Ask your team lead for support
4. See [SECURITY.md](SECURITY.md) for credential issues

### For Advanced Usage

- [QUICKSTART.md](QUICKSTART.md) - Detailed setup options (including proxy setup)
- [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) - Query patterns with Claude
- [docs/MULTI_STORE_USAGE.md](docs/MULTI_STORE_USAGE.md) - Multi-store features
- [SECURITY.md](SECURITY.md) - Security best practices

---

## 🎉 You're Ready!

After setup, you can immediately start asking Claude to search your company's codebases:

```
"Search panser-corpus for OAuth implementation"
"Find Redis configs in internal-corpus"
"Compare authentication across all frameworks"
"Which framework has the best Docker examples?"
```

**Claude will automatically search the right vector stores and give you cited answers from your actual code! 🚀**

---

## 📊 Quick Reference

### Your Configuration

```bash
# Docker image
us-central1-docker.pkg.dev/ngfw-coe/litellm-vector-store-mcp/litellm-vector-store-mcp:latest

# MCP server name
litellm-vector-store

# Available vector stores
panser-corpus, migrationmanager-corpus, companion-corpus,
mcp-servers-corpus, prismaautomation-corpus, internal-corpus, gcsai-corpus
```

### Useful Commands

```bash
# List MCP servers
claude mcp list

# Check specific server
claude mcp get litellm-vector-store

# Remove server
claude mcp remove litellm-vector-store

# Pull latest image
docker pull us-central1-docker.pkg.dev/ngfw-coe/litellm-vector-store-mcp/litellm-vector-store-mcp:latest
```

---

**Setup time:** ~2 minutes
**Maintenance:** Pull updates when notified
**Support:** See troubleshooting or ask team lead
