# Claude Code Quick Start Guide

Get the LiteLLM Vector Store MCP Server running with Claude Code in 5 minutes.

## 🎯 Docker Image Location

**Pre-built image available in GCP Artifact Registry:**
```
us-central1-docker.pkg.dev/ngfw-coe/litellm-vector-store-mcp/litellm-vector-store-mcp:latest
```

**No need to build locally!** Just pull and run (see below).

## 📋 Prerequisites

- **Claude Code** installed
- **Docker** installed (recommended) OR **Python 3.10+**
- **GCP access** to ngfw-coe project (for Docker image)
- Your **LiteLLM API credentials**

---

## 🚀 Quick Start (3 Methods)

Choose the method that best fits your workflow:

### Method 1: CLI with env-file (Most Secure) 🔒

**Best for:** Maximum security - no secrets visible in process args

```bash
# Configure Docker for GCP Artifact Registry
gcloud auth configure-docker us-central1-docker.pkg.dev --quiet

# Pull the pre-built Docker image from GCP
docker pull us-central1-docker.pkg.dev/ngfw-coe/litellm-vector-store-mcp/litellm-vector-store-mcp:latest

# Verify .env file exists with your credentials
cd /Users/antoncoleman/Documents/repos/ai_development_environment/litellm-vector-store-mcp
cat .env  # Should show your LITELLM_API_KEY and LITELLM_VECTOR_STORE_ID

# Restrict .env permissions (recommended)
chmod 600 .env

# Add MCP server using --env-file (no secrets in command args)
claude mcp add-json --scope user litellm-vector-store '{
  "type": "stdio",
  "command": "docker",
  "args": [
    "run",
    "-i",
    "--rm",
    "--env-file",
    "/Users/antoncoleman/Documents/repos/ai_development_environment/litellm-vector-store-mcp/.env",
    "us-central1-docker.pkg.dev/ngfw-coe/litellm-vector-store-mcp/litellm-vector-store-mcp:latest"
  ]
}'

# No restart needed (env-file is read at runtime, not from shell)
```

**Done!** The server is now available in all your Claude Code sessions.

🔒 **Security:** API key in `.env` file. When you run `/mcp`, args show only:
```
Args: run -i --rm --env-file /Users/.../. env us-central1-docker.pkg.dev/...
```
**No API key visible!** ✅

⚠️ **Critical:** Use absolute path for `--env-file` argument.

---

### Method 2: Project Config File (Team Sharing) 👥

**Best for:** Team collaboration, version-controlled projects

**Step 1:** Create `.mcp.json` in your project root

```bash
cd /path/to/your/project
touch .mcp.json
```

**Step 2:** Add configuration with environment variable expansion

```json
{
  "mcpServers": {
    "litellm-vector-store": {
      "type": "stdio",
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "LITELLM_API_KEY=${LITELLM_API_KEY}",
        "-e", "LITELLM_VECTOR_STORE_ID=${LITELLM_VECTOR_STORE_ID:-1111111111111111}",
        "-e", "LITELLM_BASE_URL=${LITELLM_BASE_URL:-https://litellm.psolabs.com}",
        "-e", "VERTEX_AI_PROJECT=${VERTEX_AI_PROJECT:-ngfw-coe}",
        "-e", "VERTEX_AI_LOCATION=${VERTEX_AI_LOCATION:-us-east4}",
        "us-central1-docker.pkg.dev/ngfw-coe/litellm-vector-store-mcp/litellm-vector-store-mcp:latest"
      ]
    }
  }
}
```

**Step 3:** Set environment variables in your shell

```bash
# Add to ~/.zshrc or ~/.bashrc
export LITELLM_API_KEY=sk-apikey
export LITELLM_VECTOR_STORE_ID=1111111111111111
```

**Step 4:** Commit `.mcp.json` to version control

```bash
git add .mcp.json
git commit -m "Add LiteLLM vector store MCP server"
```

**Benefits:**
- ✅ Team members automatically get the server
- ✅ Version controlled configuration
- ✅ Environment variables stay private (not in git)

---

### Method 3: User-Wide Config (All Projects) 🌍

**Best for:** Using the server across all your projects

**Step 1:** Add via CLI with user scope

```bash
claude mcp add --transport stdio litellm-vector-store \
  --env LITELLM_API_KEY=sk-your-key \
  --env LITELLM_VECTOR_STORE_ID=1111111111111111 \
  --scope user \
  -- docker run -i --rm litellm-vector-store-mcp:latest
```

**OR manually edit:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "litellm-vector-store": {
      "type": "stdio",
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "LITELLM_API_KEY=sk-apikey",
        "-e", "LITELLM_VECTOR_STORE_ID=1111111111111111",
        "-e", "LITELLM_BASE_URL=https://litellm.psolabs.com",
        "-e", "VERTEX_AI_PROJECT=ngfw-coe",
        "-e", "VERTEX_AI_LOCATION=us-east4",
        "us-central1-docker.pkg.dev/ngfw-coe/litellm-vector-store-mcp/litellm-vector-store-mcp:latest"
      ]
    }
  }
}
```

**Benefits:**
- ✅ Available in ALL projects
- ✅ Private to you only
- ✅ No per-project setup needed

---

## 🔧 Configuration Scopes Explained

### User Scope (Cross-Project)

**Location:** `~/Library/Application Support/Claude/claude_desktop_config.json`

**Use case:** Tools you use across all projects (personal utilities)

**Add via CLI:**
```bash
claude mcp add --scope user <name> ...
```

**Visibility:** Private to you, available in all projects

### Local Scope (Project-Specific, Private)

**Location:** User settings (project-specific, not in git)

**Use case:** Project-specific tools with sensitive credentials

**Add via CLI:**
```bash
claude mcp add --scope local <name> ...
```

**Visibility:** Private to you, only in this project

### Project Scope (Team-Shared)

**Location:** `.mcp.json` in project root (committed to git)

**Use case:** Required tools for team collaboration

**Add via CLI:**
```bash
claude mcp add --scope project <name> ...
```

**Visibility:** Shared with team via version control

**Precedence:** Local > Project > User (local overrides everything)

---

## 🐳 Docker-Specific Setup

### Option A: Using env-file (More Secure)

**Step 1:** Ensure `.env` file exists

```bash
cd /path/to/litellm-vector-store-mcp
ls -la .env  # Should exist with your credentials
```

**Step 2:** Add to .mcp.json with volume mount

```json
{
  "mcpServers": {
    "litellm-vector-store": {
      "type": "stdio",
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--env-file",
        "/Users/antoncoleman/Documents/repos/ai_development_environment/litellm-vector-store-mcp/.env",
        "us-central1-docker.pkg.dev/ngfw-coe/litellm-vector-store-mcp/litellm-vector-store-mcp:latest"
      ]
    }
  }
}
```

⚠️ **Important:** Use absolute paths, not relative!

### Option B: Environment Variable Expansion

**Step 1:** Set environment variables in your shell

```bash
# Add to ~/.zshrc or ~/.bashrc
export LITELLM_API_KEY=sk-apikey
export LITELLM_VECTOR_STORE_ID=1111111111111111
```

**Step 2:** Use variable expansion in .mcp.json

```json
{
  "mcpServers": {
    "litellm-vector-store": {
      "type": "stdio",
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "LITELLM_API_KEY=${LITELLM_API_KEY}",
        "-e", "LITELLM_VECTOR_STORE_ID=${LITELLM_VECTOR_STORE_ID}",
        "-e", "LITELLM_BASE_URL=${LITELLM_BASE_URL:-https://litellm.psolabs.com}",
        "us-central1-docker.pkg.dev/ngfw-coe/litellm-vector-store-mcp/litellm-vector-store-mcp:latest"
      ]
    }
  }
}
```

**Benefits:**
- ✅ Credentials in environment, not config file
- ✅ Can commit .mcp.json safely
- ✅ Default values with `${VAR:-default}` syntax

---

## 🐍 Python Setup (No Docker)

### Option A: Direct Python

**Add to .mcp.json:**

```json
{
  "mcpServers": {
    "litellm-vector-store": {
      "type": "stdio",
      "command": "python3",
      "args": [
        "/Users/antoncoleman/Documents/repos/ai_development_environment/litellm-vector-store-mcp/server.py"
      ],
      "env": {
        "LITELLM_API_KEY": "sk-apikey",
        "LITELLM_VECTOR_STORE_ID": "1111111111111111"
      }
    }
  }
}
```

### Option B: With Virtual Environment

```json
{
  "mcpServers": {
    "litellm-vector-store": {
      "type": "stdio",
      "command": "/Users/antoncoleman/Documents/repos/ai_development_environment/litellm-vector-store-mcp/venv/bin/python",
      "args": [
        "/Users/antoncoleman/Documents/repos/ai_development_environment/litellm-vector-store-mcp/server.py"
      ]
    }
  }
}
```

---

## 📋 Step-by-Step: Complete Setup

### 1. Build the Docker Image

```bash
cd /Users/antoncoleman/Documents/repos/ai_development_environment/litellm-vector-store-mcp

# Build
docker build -t litellm-vector-store-mcp:latest .

# Verify
docker images | grep litellm-vector-store-mcp
```

### 2. Test Configuration

```bash
# Verify .env file has credentials
cat .env

# Test the server
python test_config.py
```

Expected output:
```
✓ SUCCESS! Vector store is accessible
  Found 10 results for test query
```

### 3. Choose Configuration Method

Pick one:
- **A)** CLI command (fastest, user-scope)
- **B)** `.mcp.json` in project root (team sharing)
- **C)** `claude_desktop_config.json` (user-wide)

### 4. Add the Server

**Method A: CLI (Recommended)**

```bash
claude mcp add --transport stdio litellm-vector-store \
  --env LITELLM_API_KEY=sk-apikey \
  --env LITELLM_VECTOR_STORE_ID=1111111111111111 \
  --scope user \
  -- docker run -i --rm litellm-vector-store-mcp:latest
```

**Method B: .mcp.json (Team)**

```bash
# In your project root
cat > .mcp.json << 'EOF'
{
  "mcpServers": {
    "litellm-vector-store": {
      "type": "stdio",
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "--env-file", "/Users/antoncoleman/Documents/repos/ai_development_environment/litellm-vector-store-mcp/.env",
        "us-central1-docker.pkg.dev/ngfw-coe/litellm-vector-store-mcp/litellm-vector-store-mcp:latest"
      ]
    }
  }
}
EOF
```

**Method C: Manual Edit**

```bash
# Edit config file
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Add the server (see examples above)
```

### 5. Verify in Claude Code

```bash
# List configured servers
claude mcp list
```

Should show:
```
litellm-vector-store (stdio) - user scope
```

### 6. Test with Claude

Open Claude Code and ask:
```
What vector stores are available?
```

Claude should use the `litellm_list_vector_stores` tool and show your 7 vector stores!

---

## 🎯 Recommended Approach by Use Case

### Solo Developer Working on Multiple Projects

**Use:** User scope with CLI
```bash
claude mcp add --scope user litellm-vector-store --env LITELLM_API_KEY=... -- docker run -i --rm litellm-vector-store-mcp:latest
```

**Why:** Available everywhere, no per-project setup

### Team Project with Shared Codebases

**Use:** Project scope with `.mcp.json`
```json
// .mcp.json in project root
{
  "mcpServers": {
    "litellm-vector-store": {
      "type": "stdio",
      "command": "docker",
      "args": ["run", "-i", "--rm", "--env-file", "${HOME}/.litellm-mcp.env", "us-central1-docker.pkg.dev/ngfw-coe/litellm-vector-store-mcp/litellm-vector-store-mcp:latest"]
    }
  }
}
```

**Why:** Team gets the config, but credentials stay private

### Experimenting with Different Stores

**Use:** Local scope
```bash
claude mcp add --scope local litellm-vector-store --env LITELLM_VECTOR_STORE_ID=different-id ...
```

**Why:** Project-specific without affecting team config

---

## 📁 Configuration File Locations

### For Reference

| Scope | File Location | Visibility |
|-------|--------------|------------|
| **Project** | `.mcp.json` in project root | Team (committed to git) |
| **User** | `~/Library/Application Support/Claude/claude_desktop_config.json` | Personal (all projects) |
| **Local** | Claude Code internal storage | Personal (this project only) |

**Precedence:** Local > Project > User

---

## 🔍 Verification Steps

### 1. Check Server is Loaded

```bash
claude mcp list
```

Should show:
```
MCP Servers:
  litellm-vector-store (stdio) - user scope
    Status: ✓ Connected
```

### 2. Test in Claude Code

Ask Claude:
```
Use the litellm_list_vector_stores tool
```

Expected response:
```
🔧 Using tool: litellm_list_vector_stores

# Available Vector Stores

**Total Stores:** 7

1. panser-corpus
2. migrationmanager-corpus
3. companion-corpus
...
```

### 3. Test Search

Ask Claude:
```
Search the internal-corpus for Redis configuration
```

Expected response:
```
🔧 Using tool: litellm_search_vector_store

# Vector Store Search Results

**Query:** Redis configuration
**Results Found:** 5

## Result 1: redis-stack.yaml.txt
- **Relevance Score:** 0.3118
...
```

---

## 🐛 Troubleshooting

### Server Not Showing in `claude mcp list`

**Check 1: Verify Docker image exists**
```bash
docker images | grep litellm-vector-store-mcp
```

**Check 2: Test Docker run manually**
```bash
docker run -i --rm \
  -e LITELLM_API_KEY=sk-... \
  -e LITELLM_VECTOR_STORE_ID=1111111111111111 \
  litellm-vector-store-mcp:latest
```

Should run without errors (Ctrl+C to exit)

**Check 3: Verify config file syntax**
```bash
# For .mcp.json
python3 -c "import json; print(json.load(open('.mcp.json')))"

# For claude_desktop_config.json
python3 -c "import json; print(json.load(open('~/Library/Application Support/Claude/claude_desktop_config.json')))"
```

### Tool Calls Fail

**Check 1: Environment variables are set**
```bash
# If using expansion
echo $LITELLM_API_KEY
echo $LITELLM_VECTOR_STORE_ID
```

**Check 2: Test configuration**
```bash
cd /path/to/litellm-vector-store-mcp
python test_config.py
```

Should show:
```
✓ SUCCESS! Vector store is accessible
```

### Claude Can't Find Tools

**Solution 1: Restart Claude Code**

Completely quit and restart Claude Code, not just close the window.

**Solution 2: Check server status**
```bash
claude mcp get litellm-vector-store
```

**Solution 3: Remove and re-add**
```bash
claude mcp remove litellm-vector-store
claude mcp add --scope user litellm-vector-store --env ... -- docker run ...
```

---

## 🎓 Advanced Configuration

### Using gcloud Proxy (Alternative to Direct Connection)

**If you need to access LiteLLM via gcloud IAP tunnel:**

**Step 1:** Start gcloud proxy tunnel

```bash
# Start IAP tunnel to LiteLLM proxy
gcloud compute start-iap-tunnel litellm-proxy 443 \
  --local-host-port=localhost:5600 \
  --zone=your-zone \
  --project=ngfw-coe
```

**Step 2:** Update .env to use proxy

```env
# Use local proxy instead of direct connection
LITELLM_BASE_URL=http://localhost:5600
```

**Step 3:** Add MCP server (same as Method 1)

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

⚠️ **Note:** Added `--network host` so Docker container can access localhost proxy.

**Use cases:**
- Secure access via IAP tunnel
- Local development/testing
- When direct connection is blocked by firewall

### Using env-file Instead of Inline Variables

**More secure for sensitive credentials:**

```json
{
  "mcpServers": {
    "litellm-vector-store": {
      "type": "stdio",
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "--env-file", "/Users/antoncoleman/Documents/repos/ai_development_environment/litellm-vector-store-mcp/.env",
        "us-central1-docker.pkg.dev/ngfw-coe/litellm-vector-store-mcp/litellm-vector-store-mcp:latest"
      ]
    }
  }
}
```

### Multiple Configurations for Different Environments

**Development:**
```json
{
  "mcpServers": {
    "litellm-dev": {
      "type": "stdio",
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "LITELLM_VECTOR_STORE_ID=dev-store-id",
        "--env-file", "~/.litellm-dev.env",
        "us-central1-docker.pkg.dev/ngfw-coe/litellm-vector-store-mcp/litellm-vector-store-mcp:latest"
      ]
    }
  }
}
```

**Production:**
```json
{
  "mcpServers": {
    "litellm-prod": {
      "type": "stdio",
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "LITELLM_VECTOR_STORE_ID=prod-store-id",
        "--env-file", "~/.litellm-prod.env",
        "us-central1-docker.pkg.dev/ngfw-coe/litellm-vector-store-mcp/litellm-vector-store-mcp:latest"
      ]
    }
  }
}
```

---

## 📊 Configuration Comparison

| Method | Setup Time | Scope | Team Sharing | Security |
|--------|-----------|-------|--------------|----------|
| **CLI** | 1 min | User/Local/Project | Via .mcp.json | Good (env vars) |
| **.mcp.json** | 2 min | Project | ✅ Yes | ✅ Best (expansion) |
| **Manual Edit** | 3 min | User | No | Medium (inline) |

**Recommendation:**
- **Solo dev:** Use CLI with `--scope user`
- **Team project:** Use `.mcp.json` with env expansion
- **Experimenting:** Use CLI with `--scope local`

---

## 🎯 Example Workflows

### Workflow 1: Solo Developer

```bash
# One-time setup
claude mcp add --scope user litellm-vector-store \
  --env LITELLM_API_KEY=$LITELLM_API_KEY \
  --env LITELLM_VECTOR_STORE_ID=1111111111111111 \
  -- docker run -i --rm litellm-vector-store-mcp:latest

# Now available in ALL projects forever
# Just ask Claude to search vector stores!
```

### Workflow 2: Team Project

```bash
# Team lead creates .mcp.json
cat > .mcp.json << 'EOF'
{
  "mcpServers": {
    "litellm-vector-store": {
      "type": "stdio",
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "LITELLM_API_KEY=${LITELLM_API_KEY}",
        "-e", "LITELLM_VECTOR_STORE_ID=${LITELLM_VECTOR_STORE_ID}",
        "us-central1-docker.pkg.dev/ngfw-coe/litellm-vector-store-mcp/litellm-vector-store-mcp:latest"
      ]
    }
  }
}
EOF

# Commit to git
git add .mcp.json
git commit -m "Add vector store MCP server"

# Team members:
# 1. Pull the repo
# 2. Set their environment variables
# 3. MCP server works automatically!
```

### Workflow 3: Different Stores per Project

```bash
# Project A: Search internal framework
cd ~/projects/internal-tools
claude mcp add --scope local litellm-internal \
  --env LITELLM_VECTOR_STORE_ID=1111111111111111 \
  -- docker run -i --rm litellm-vector-store-mcp:latest

# Project B: Search Panser framework
cd ~/projects/panser-work
claude mcp add --scope local litellm-panser \
  --env LITELLM_VECTOR_STORE_ID=612489549322387456 \
  -- docker run -i --rm litellm-vector-store-mcp:latest
```

Each project gets a different default vector store!

---

## 💡 Pro Tips

### 1. Use Environment Variable Expansion

```json
"args": [
  "-e", "LITELLM_API_KEY=${LITELLM_API_KEY}",
  "-e", "LITELLM_VECTOR_STORE_ID=${LITELLM_VECTOR_STORE_ID:-1111111111111111}"
]
```

**Benefits:**
- Credentials stay in environment, not config
- Can commit .mcp.json safely
- Supports default values with `:-`

### 2. Set Defaults in Shell Config

```bash
# Add to ~/.zshrc
export LITELLM_API_KEY=sk-apikey
export LITELLM_VECTOR_STORE_ID=1111111111111111
export LITELLM_BASE_URL=https://litellm.psolabs.com
```

Then configs just use `${VAR}` expansion.

### 3. Use Absolute Paths

```json
// ✅ Good
"--env-file", "/Users/antoncoleman/Documents/repos/.../litellm-vector-store-mcp/.env"

// ❌ Bad (won't work)
"--env-file", "../litellm-vector-store-mcp/.env"
```

### 4. Test Before Adding

```bash
# Always test first
docker run -i --rm --env-file .env litellm-vector-store-mcp:latest
# (Ctrl+C to exit if it runs without error)

# Then add to Claude
claude mcp add ...
```

---

## 🎉 You're Ready!

After setup, you can ask Claude:

```
"What vector stores are available?"
→ Lists all 7 stores

"Search panser-corpus for authentication code"
→ Searches Panser framework

"Find Docker configs across all frameworks"
→ Searches all 7 stores

"Which framework has the best Redis examples?"
→ Compares implementations
```

**Claude will automatically use the MCP tools to search your codebases and provide cited answers! 🚀**

---

## 📚 Next Steps

- **Learn more:** See [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) for advanced usage
- **Docker details:** See [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) for deployment guide
- **Multi-store:** See [docs/MULTI_STORE_USAGE.md](docs/MULTI_STORE_USAGE.md) for cross-store search
- **Troubleshooting:** See [CLAUDE_CODE_SETUP.md](CLAUDE_CODE_SETUP.md) for detailed help
