# Security Best Practices

This guide covers secure configuration and deployment of the LiteLLM Vector Store MCP Server.

## 🔒 API Key Security

### ⚠️ The Problem: Plaintext API Keys

**Bad Practice:**
```json
{
  "mcpServers": {
    "litellm-vector-store": {
      "args": [
        "-e", "LITELLM_API_KEY=sk-apikey"
      ]
    }
  }
}
```

**Issues:**
- ❌ API key visible in config file
- ❌ Could be accidentally committed to git
- ❌ Visible in process lists
- ❌ Could be leaked in backups/logs

---

## ✅ Secure Solutions

### Solution 1: Environment Variable Expansion (Recommended) ⭐

**Store API key in shell environment, reference it in config:**

**Step 1:** Add to your shell configuration

```bash
# Add to ~/.zshrc (for zsh) or ~/.bashrc (for bash)
export LITELLM_API_KEY=sk-apikey
export LITELLM_VECTOR_STORE_ID=
```

**Step 2:** Reload shell configuration

```bash
source ~/.zshrc  # or source ~/.bashrc
```

**Step 3:** Use variable expansion in MCP config

```bash
claude mcp add-json --scope user litellm-vector-store '{
  "type": "stdio",
  "command": "docker",
  "args": [
    "run", "-i", "--rm",
    "-e", "LITELLM_API_KEY=${LITELLM_API_KEY}",
    "-e", "LITELLM_VECTOR_STORE_ID=${LITELLM_VECTOR_STORE_ID:-}",
    "litellm-vector-store-mcp:latest"
  ]
}'
```

**Result in `~/.claude.json`:**
```json
{
  "args": [
    "-e", "LITELLM_API_KEY=${LITELLM_API_KEY}",
    ...
  ]
}
```

**Benefits:**
- ✅ No plaintext key in config file
- ✅ Key is in environment (more secure)
- ✅ Config can be safely shared
- ✅ Variable expansion happens at runtime

---

### Solution 2: Docker env-file (Most Secure) 🔐

**Store credentials in a separate file that Docker reads:**

**Step 1:** Create a credentials file

```bash
# Create outside of project directory
cat > ~/.litellm-mcp.env << 'EOF'
LITELLM_API_KEY=sk-apikey
LITELLM_VECTOR_STORE_ID=11111111111111111111
LITELLM_BASE_URL=https://litellm.psolabs.com
VERTEX_AI_PROJECT=ngfw-coe
VERTEX_AI_LOCATION=us-east4
EOF

# Restrict permissions (you only)
chmod 600 ~/.litellm-mcp.env
```

**Step 2:** Configure MCP server to use env-file

```bash
claude mcp add-json --scope user litellm-vector-store '{
  "type": "stdio",
  "command": "docker",
  "args": [
    "run", "-i", "--rm",
    "--env-file", "'$HOME'/.litellm-mcp.env",
    "litellm-vector-store-mcp:latest"
  ]
}'
```

**Benefits:**
- ✅✅ Most secure - credentials in separate file
- ✅ File permissions can be restricted (chmod 600)
- ✅ Config file has no secrets at all
- ✅ Easy to rotate credentials (just edit one file)

---

### Solution 3: macOS Keychain (Maximum Security) 🛡️

**Store API key in macOS Keychain, retrieve at runtime:**

**Step 1:** Add to keychain

```bash
# Add API key to keychain
security add-generic-password \
  -a "$USER" \
  -s "litellm-api-key" \
  -w "sk-apikey"
```

**Step 2:** Create wrapper script

```bash
cat > ~/bin/litellm-mcp-wrapper.sh << 'EOF'
#!/bin/bash

# Retrieve API key from keychain
export LITELLM_API_KEY=$(security find-generic-password -a "$USER" -s "litellm-api-key" -w)
export LITELLM_VECTOR_STORE_ID=11111111111111111111

# Run Docker container
docker run -i --rm \
  -e "LITELLM_API_KEY=$LITELLM_API_KEY" \
  -e "LITELLM_VECTOR_STORE_ID=$LITELLM_VECTOR_STORE_ID" \
  -e "LITELLM_BASE_URL=https://litellm.psolabs.com" \
  -e "VERTEX_AI_PROJECT=ngfw-coe" \
  -e "VERTEX_AI_LOCATION=us-east4" \
  litellm-vector-store-mcp:latest
EOF

chmod +x ~/bin/litellm-mcp-wrapper.sh
```

**Step 3:** Configure MCP to use wrapper

```bash
claude mcp add-json --scope user litellm-vector-store '{
  "type": "stdio",
  "command": "/Users/antoncoleman/bin/litellm-mcp-wrapper.sh",
  "args": []
}'
```

**Benefits:**
- ✅✅✅ Maximum security - key in macOS Keychain
- ✅ No plaintext anywhere in files
- ✅ Protected by macOS security
- ✅ Supports Touch ID/password unlock

---

## 📊 Security Comparison

| Method | Security Level | Ease of Use | Team Sharing |
|--------|---------------|-------------|--------------|
| **Plaintext in config** | ❌ Poor | ✅ Easy | ❌ Risky |
| **Env var expansion** | ✅ Good | ✅ Easy | ✅ Safe |
| **Docker env-file** | ✅✅ Better | ☑️ Medium | ✅ Safe |
| **macOS Keychain** | ✅✅✅ Best | ☑️ Medium | ✅ Safe |

---

## 🎯 Recommended Setup (Solution 1 + 2 Combined)

**Best balance of security and usability:**

**Step 1:** Set environment variables in shell

```bash
# Add to ~/.zshrc
cat >> ~/.zshrc << 'EOF'

# LiteLLM MCP Server credentials (DO NOT commit)
export LITELLM_API_KEY=sk-apikey
export LITELLM_VECTOR_STORE_ID=11111111111111111111
EOF

# Reload
source ~/.zshrc
```

**Step 2:** Use variable expansion in config

```bash
claude mcp add-json --scope user litellm-vector-store '{
  "type": "stdio",
  "command": "docker",
  "args": [
    "run", "-i", "--rm",
    "-e", "LITELLM_API_KEY=${LITELLM_API_KEY}",
    "-e", "LITELLM_VECTOR_STORE_ID=${LITELLM_VECTOR_STORE_ID:-11111111111111111111}",
    "-e", "LITELLM_BASE_URL=${LITELLM_BASE_URL:-https://litellm.psolabs.com}",
    "-e", "VERTEX_AI_PROJECT=${VERTEX_AI_PROJECT:-ngfw-coe}",
    "-e", "VERTEX_AI_LOCATION=${VERTEX_AI_LOCATION:-us-east4}",
    "litellm-vector-store-mcp:latest"
  ]
}'
```

**Result:** Config file has `${LITELLM_API_KEY}`, actual key is in shell environment.

---

## 🔍 Verification

### Check Config File (No Plaintext)

```bash
cat ~/.claude.json | grep LITELLM_API_KEY
```

Should show:
```
"LITELLM_API_KEY=${LITELLM_API_KEY}",
```

**NOT:**
```
"LITELLM_API_KEY=sk-a8d9e2b7...",  // ❌ This would be bad
```

### Check Environment Variables

```bash
echo $LITELLM_API_KEY | head -c 10
```

Should show:
```
sk-a8d9e2b
```

---

## 🛡️ Additional Security Measures

### 1. Restrict Shell Config Permissions

```bash
chmod 600 ~/.zshrc  # Only you can read/write
```

### 2. Use Separate Credentials File

```bash
# Create credentials file
cat > ~/.litellm-credentials << 'EOF'
export LITELLM_API_KEY=sk-apikey
export LITELLM_VECTOR_STORE_ID=11111111111111111111
EOF

chmod 600 ~/.litellm-credentials

# Source from .zshrc
echo "source ~/.litellm-credentials" >> ~/.zshrc
```

**Benefits:**
- ✅ Credentials isolated in separate file
- ✅ Easier to rotate (update one file)
- ✅ Can exclude from backups

### 3. Restrict Docker env-file Permissions

```bash
chmod 600 ~/.litellm-mcp.env
```

### 4. Never Commit Credentials

**Verify .gitignore:**

```bash
# Check .gitignore includes these
cat .gitignore | grep -E '(\.env|\.credentials)'
```

Should include:
```
.env
.env.local
*.credentials
```

---

## 🚨 Security Checklist

Before deploying:

- [ ] ✅ API keys use environment variable expansion
- [ ] ✅ Shell config files have restricted permissions (600)
- [ ] ✅ .env files are in .gitignore
- [ ] ✅ No plaintext keys in MCP config files
- [ ] ✅ Docker runs as non-root user
- [ ] ✅ Credentials file has chmod 600

---

## 🔄 Credential Rotation

**When rotating API keys:**

**Method 1 (Env Vars):**
```bash
# Update in .zshrc
nano ~/.zshrc
# Change LITELLM_API_KEY value

# Reload
source ~/.zshrc

# Restart Claude Code (env vars are read on startup)
```

**Method 2 (env-file):**
```bash
# Update credentials file
nano ~/.litellm-mcp.env

# Restart Claude Code
```

**No config file changes needed!** The MCP server will automatically use the new key.

---

## 👥 Team Collaboration

**For .mcp.json (team projects):**

```json
{
  "mcpServers": {
    "litellm-vector-store": {
      "type": "stdio",
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "LITELLM_API_KEY=${LITELLM_API_KEY}",
        "-e", "LITELLM_VECTOR_STORE_ID=${LITELLM_VECTOR_STORE_ID}",
        "litellm-vector-store-mcp:latest"
      ]
    }
  }
}
```

**Team members each set their own credentials:**

```bash
# Each developer adds to their ~/.zshrc
export LITELLM_API_KEY=their-own-api-key
export LITELLM_VECTOR_STORE_ID=11111111111111111111
```

**Benefits:**
- ✅ .mcp.json can be committed (no secrets)
- ✅ Each team member uses their own credentials
- ✅ No shared API keys
- ✅ Individual access control

---

## 🎓 Security Levels

### Level 1: Basic (Don't Do This)
```json
"-e", "LITELLM_API_KEY=sk-plaintext-key"
```
Security: ❌ Poor - Key in plaintext

### Level 2: Environment Variables
```json
"-e", "LITELLM_API_KEY=${LITELLM_API_KEY}"
```
```bash
# In ~/.zshrc
export LITELLM_API_KEY=sk-...
```
Security: ✅ Good - Key in shell environment

### Level 3: Separate Credentials File
```json
"--env-file", "/Users/antoncoleman/.litellm-mcp.env"
```
```bash
chmod 600 ~/.litellm-mcp.env
```
Security: ✅✅ Better - Isolated credentials file

### Level 4: macOS Keychain
```bash
security add-generic-password -s "litellm-api-key" -w "sk-..."
```
Security: ✅✅✅ Best - OS-level encryption

---

## 📝 Current Setup Status

**Your current configuration:**

✅ **Config file location:** `~/.claude.json` (user scope)
✅ **API key storage:** Environment variable (`${LITELLM_API_KEY}`)
✅ **Shell config:** `~/.zshrc` with credentials
✅ **Security level:** Good (Level 2)

**What's in your files:**

`~/.claude.json`:
```json
"-e", "LITELLM_API_KEY=${LITELLM_API_KEY}"  // ✅ Variable reference
```

`~/.zshrc`:
```bash
export LITELLM_API_KEY=sk-a8d9e2b...  // ✅ Actual key
```

---

## 🔐 Upgrading Security

### To Level 3 (Separate File)

```bash
# 1. Create credentials file
cat > ~/.litellm-mcp.env << 'EOF'
LITELLM_API_KEY=sk-apikey
LITELLM_VECTOR_STORE_ID=11111111111111111111
LITELLM_BASE_URL=https://litellm.psolabs.com
VERTEX_AI_PROJECT=ngfw-coe
VERTEX_AI_LOCATION=us-east4
EOF

# 2. Restrict permissions
chmod 600 ~/.litellm-mcp.env

# 3. Update MCP config
claude mcp remove litellm-vector-store
claude mcp add-json --scope user litellm-vector-store '{
  "type": "stdio",
  "command": "docker",
  "args": [
    "run", "-i", "--rm",
    "--env-file", "'$HOME'/.litellm-mcp.env",
    "litellm-vector-store-mcp:latest"
  ]
}'

# 4. Remove from .zshrc
nano ~/.zshrc
# Delete the LITELLM_* export lines
```

### To Level 4 (Keychain)

Follow the macOS Keychain solution above.

---

## 🚨 Security Incidents

### If API Key is Compromised

**Immediate steps:**

1. **Rotate the key** in LiteLLM:
   ```bash
   # Get new key from LiteLLM admin
   ```

2. **Update shell config:**
   ```bash
   nano ~/.zshrc
   # Update LITELLM_API_KEY value
   source ~/.zshrc
   ```

3. **Restart Claude Code:**
   ```bash
   # Completely quit and reopen
   ```

4. **Revoke old key** in LiteLLM admin panel

---

## ✅ Security Best Practices Summary

**Do:**
- ✅ Use environment variable expansion (`${VAR}`)
- ✅ Store credentials in shell config or separate file
- ✅ Restrict file permissions (chmod 600)
- ✅ Use different keys per environment (dev/prod)
- ✅ Rotate keys periodically
- ✅ Use .gitignore for credential files

**Don't:**
- ❌ Put plaintext keys in MCP config files
- ❌ Commit .env files to git
- ❌ Share API keys across team members
- ❌ Use production keys in development
- ❌ Store keys in plaintext without restrictions

---

## 📚 References

- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [Claude Code MCP Documentation](https://docs.claude.com/en/docs/claude-code/mcp)
- [Environment Variable Security](https://12factor.net/config)

---

**Your setup is now secure! The API key is referenced via `${LITELLM_API_KEY}`, not stored in plaintext in the config file. 🔒**
