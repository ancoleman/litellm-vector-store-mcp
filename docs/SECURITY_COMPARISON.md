# MCP Server Security Configuration Comparison

This document compares different methods of configuring the MCP server and their security implications, especially regarding API key visibility in Claude's `/mcp` status display.

## 🔍 The Issue: API Key Visibility in `/mcp` Display

When you run `/mcp` in Claude Code, it shows the **actual running command** with environment variables expanded. This can expose sensitive data.

---

## 📊 Configuration Methods Compared

### Method 1: Plaintext in Args (INSECURE) ❌

**Configuration:**
```json
{
  "args": [
    "run", "-i", "--rm",
    "-e", "LITELLM_API_KEY=sk-your-api-key-here",
    "..."
  ]
}
```

**What `/mcp` shows:**
```
Args: run -i --rm -e LITELLM_API_KEY=sk-your-api-key-here ...
```

**Security:**
- ❌ API key visible in config file
- ❌ API key visible in `/mcp` display
- ❌ API key in process args
- ❌ Could be accidentally shared/screenshot

**Never use this method!**

---

### Method 2: Environment Variable Expansion (MEDIUM) ⚠️

**Configuration:**
```json
{
  "args": [
    "run", "-i", "--rm",
    "-e", "LITELLM_API_KEY=${LITELLM_API_KEY}",
    "..."
  ]
}
```

**Config file storage:**
```json
"-e", "LITELLM_API_KEY=${LITELLM_API_KEY}"  // ✅ Variable reference
```

**What `/mcp` shows:**
```
Args: run -i --rm -e LITELLM_API_KEY=sk-your-api-key-here ...
```

**Security:**
- ✅ Config file is secure (has variable, not value)
- ❌ API key visible in `/mcp` display (shows expanded value)
- ❌ API key in process args
- ⚠️ Could be accidentally screenshot

**Better than Method 1, but not ideal.**

---

### Method 3: Docker --env-file (SECURE) ✅

**Configuration:**
```json
{
  "args": [
    "run", "-i", "--rm",
    "--env-file", "/Users/antoncoleman/Documents/repos/.../. env",
    "..."
  ]
}
```

**Config file storage:**
```json
"--env-file", "/path/to/.env"  // ✅ Just a file path
```

**What `/mcp` shows:**
```
Args: run -i --rm --env-file /Users/antoncoleman/Documents/repos/.../. env us-central1-docker.pkg.dev/...
```

**Security:**
- ✅ Config file is secure (just file path)
- ✅ API key NOT visible in `/mcp` display
- ✅ API key NOT in process args (Docker reads it internally)
- ✅ Can't be accidentally screenshot
- ✅ File permissions can be restricted (chmod 600)

**Recommended method!** ⭐

---

## 🎯 Recommended Configuration

### Step 1: Ensure .env file has credentials

```bash
cd /path/to/litellm-vector-store-mcp

# Verify .env exists and has credentials
cat .env
```

Should show:
```env
LITELLM_API_KEY=sk-your-api-key-here
LITELLM_VECTOR_STORE_ID=2341871806232657920
...
```

### Step 2: Restrict .env file permissions

```bash
chmod 600 .env  # Only you can read
```

### Step 3: Add MCP server with --env-file

```bash
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
```

**Result when you run `/mcp`:**
```
Args: run -i --rm --env-file /Users/.../. env us-central1-docker.pkg.dev/...
```

**No secrets visible!** ✅

---

## 📋 Security Comparison Table

| Aspect | Plaintext | Env Expansion | --env-file |
|--------|-----------|---------------|------------|
| **Config file security** | ❌ Has API key | ✅ Has variable | ✅ Has path only |
| **`/mcp` display** | ❌ Shows key | ❌ Shows key | ✅ No key |
| **Process args** | ❌ Has key | ❌ Has key | ✅ No key |
| **Can be screenshot safely** | ❌ No | ❌ No | ✅ Yes |
| **File permissions** | N/A | ⚠️ Shell config | ✅ Can restrict .env |
| **Team sharing** | ❌ Dangerous | ☑️ Each sets own | ✅ Each has own .env |
| **Rotation ease** | ❌ Hard | ☑️ Update shell | ✅ Update one file |
| **Overall security** | ❌ Poor | ⚠️ Medium | ✅ Good |

---

## 🔄 Migration Guide

### If You're Using Method 2 (Env Expansion)

**Switch to Method 3 (--env-file):**

```bash
# 1. Remove current server
claude mcp remove litellm-vector-store -s user

# 2. Verify .env file exists
ls -la /path/to/litellm-vector-store-mcp/.env

# 3. Add with --env-file
claude mcp add-json --scope user litellm-vector-store '{
  "type": "stdio",
  "command": "docker",
  "args": [
    "run", "-i", "--rm",
    "--env-file", "/absolute/path/to/.env",
    "us-central1-docker.pkg.dev/ngfw-coe/litellm-vector-store-mcp/litellm-vector-store-mcp:latest"
  ]
}'

# 4. Verify - run /mcp in Claude Code
# Should NOT show API key in Args
```

---

## 👥 Team Collaboration Best Practices

### For .mcp.json (Project Scope)

**Use --env-file with relative path to user's home:**

```json
{
  "mcpServers": {
    "litellm-vector-store": {
      "type": "stdio",
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "--env-file", "${HOME}/.litellm-mcp.env",
        "us-central1-docker.pkg.dev/ngfw-coe/litellm-vector-store-mcp/litellm-vector-store-mcp:latest"
      ]
    }
  }
}
```

**Team members each create** `~/.litellm-mcp.env` with their own credentials:

```env
LITELLM_API_KEY=their-own-key
LITELLM_VECTOR_STORE_ID=2341871806232657920
```

**Benefits:**
- ✅ .mcp.json can be committed (no secrets)
- ✅ Each person has their own credentials
- ✅ No API keys visible in `/mcp` status
- ✅ Easy to rotate (update one file)

---

## 🔐 Why --env-file is Better

### Visibility Test

**Method 2 (Env Expansion):**
```bash
$ /mcp
Args: run -i --rm -e LITELLM_API_KEY=sk-your-api-key-here ...
                                     ^^^^^^^^^^^^ VISIBLE! ❌
```

**Method 3 (--env-file):**
```bash
$ /mcp
Args: run -i --rm --env-file /Users/antoncoleman/.../.env us-central1-docker.pkg.dev/...
                             ^^^^^^^^^^^ Just a file path ✅
```

### Process List Test

**Method 2:**
```bash
$ ps aux | grep docker
...run -i --rm -e LITELLM_API_KEY=sk-a8d9e2b75... ❌ Visible in process list
```

**Method 3:**
```bash
$ ps aux | grep docker
...run -i --rm --env-file /Users/.../. env ✅ No secrets in process args
```

---

## ✅ Current Recommended Setup

**Your current configuration (Method 3):**

```bash
# What's in ~/.claude.json
{
  "args": [
    "run", "-i", "--rm",
    "--env-file", "/Users/antoncoleman/Documents/repos/ai_development_environment/litellm-vector-store-mcp/.env",
    "us-central1-docker.pkg.dev/ngfw-coe/litellm-vector-store-mcp/litellm-vector-store-mcp:latest"
  ]
}

# What's in .env (chmod 600)
LITELLM_API_KEY=sk-your-api-key-here
LITELLM_VECTOR_STORE_ID=2341871806232657920
...

# What /mcp shows
Args: run -i --rm --env-file /Users/.../. env us-central1-docker.pkg.dev/...
```

**Security level:** ✅ Good - No secrets visible anywhere

---

## 📖 Summary

**Use --env-file method for:**
- ✅ Maximum privacy (no secrets in `/mcp` display)
- ✅ No secrets in process arguments
- ✅ File permission control
- ✅ Easy credential rotation
- ✅ Safe for screenshotsScreenshots/demos

**Your setup is now:** ✅ **Secure** using --env-file method!

---

**See also:**
- [SECURITY.md](../SECURITY.md) - Complete security guide
- [TEAM_SETUP.md](../TEAM_SETUP.md) - Team distribution guide
- [QUICKSTART.md](../QUICKSTART.md) - Setup instructions
