# Multi-Platform Docker Support

The LiteLLM Vector Store MCP Server Docker images are built for multiple platforms, ensuring compatibility across all major operating systems and CPU architectures.

## 🎯 Supported Platforms

### linux/amd64
**CPU:** Intel/AMD x86_64 processors

**Compatible with:**
- ✅ Windows 10/11 with WSL2
- ✅ macOS Intel (pre-2020 Macs)
- ✅ Linux x86_64 (most servers and desktops)
- ✅ Cloud VMs (GCP, AWS, Azure standard instances)

### linux/arm64
**CPU:** ARM 64-bit processors

**Compatible with:**
- ✅ macOS Apple Silicon (M1, M2, M3, M4 chips)
- ✅ Linux ARM64 (Raspberry Pi 4+, ARM servers)
- ✅ Cloud ARM instances (GCP Tau T2A, AWS Graviton)

---

## 🔄 How It Works

### Automatic Platform Selection

When you run:
```bash
docker pull us-central1-docker.pkg.dev/ngfw-coe/litellm-vector-store-mcp/litellm-vector-store-mcp:latest
```

**Docker automatically:**
1. Detects your system's architecture
2. Pulls the matching platform image
3. Uses the appropriate binary

**You don't need to specify the platform!**

### Multi-Platform Manifest

The `:latest` and `:v0.1.0` tags point to a **multi-platform manifest** that contains images for both architectures:

```bash
$ docker buildx imagetools inspect us-central1-docker.pkg.dev/.../litellm-vector-store-mcp:latest

Manifests:
  Platform: linux/amd64
  Platform: linux/arm64
```

Docker reads this manifest and selects the right one for you.

---

## 🏗️ Building Multi-Platform Images

### For Maintainers

**Build and push for all platforms:**

```bash
# Create/use buildx builder
docker buildx create --name multiplatform --use

# Build for both platforms and push
docker buildx build --platform linux/amd64,linux/arm64 \
  -t us-central1-docker.pkg.dev/ngfw-coe/litellm-vector-store-mcp/litellm-vector-store-mcp:latest \
  -t us-central1-docker.pkg.dev/ngfw-coe/litellm-vector-store-mcp/litellm-vector-store-mcp:v0.2.0 \
  --push \
  .
```

**Benefits of buildx:**
- Builds multiple architectures in parallel
- Automatically creates multi-platform manifest
- Pushes directly to registry
- Uses QEMU for cross-platform emulation

### Dockerfile Compatibility

Our Dockerfile is **platform-agnostic** - it works on both architectures without modification:

```dockerfile
FROM python:3.12-slim as base  # Available for both amd64 and arm64
RUN useradd --create-home --shell /bin/bash mcp
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY server.py .
USER mcp
ENTRYPOINT ["python", "-u", "server.py"]
```

**No architecture-specific commands needed!**

---

## 💡 Platform-Specific Considerations

### Windows Users (WSL2)

**Requirements:**
- Windows 10/11 with WSL2 enabled
- Docker Desktop for Windows

**Image pulled:** linux/amd64

**Setup:**
```bash
# In WSL2 terminal
docker pull us-central1-docker.pkg.dev/ngfw-coe/litellm-vector-store-mcp/litellm-vector-store-mcp:latest

# Configure Claude Code (same as Linux)
claude mcp add-json --scope user litellm-vector-store '{...}'
```

**Note:** Native Windows containers are not supported (MCP stdio requires Linux containers).

### macOS Users

**Intel Macs (pre-2020):**
- Pulls: linux/amd64
- Runs via Docker Desktop VM
- Performance: Good

**Apple Silicon (M1+):**
- Pulls: linux/arm64
- Native ARM64 execution
- Performance: Excellent (native architecture)

**Both work identically** - same commands, same configuration.

### Linux Users

**x86_64:**
- Pulls: linux/amd64
- Native execution
- Most common platform

**ARM64:**
- Pulls: linux/arm64
- Native execution
- Increasingly common (AWS Graviton, etc.)

---

## 🔍 Verifying Platform

### Check Which Platform You Pulled

```bash
docker inspect us-central1-docker.pkg.dev/ngfw-coe/litellm-vector-store-mcp/litellm-vector-store-mcp:latest \
  --format='{{.Architecture}}'
```

Returns:
- `amd64` - Intel/AMD x86_64
- `arm64` - ARM 64-bit

### Force Specific Platform (Advanced)

**If needed, you can force a specific platform:**

```bash
# Force amd64 (might be slower on ARM)
docker pull --platform linux/amd64 \
  us-central1-docker.pkg.dev/ngfw-coe/litellm-vector-store-mcp/litellm-vector-store-mcp:latest

# Force arm64 (might be slower on x86)
docker pull --platform linux/arm64 \
  us-central1-docker.pkg.dev/ngfw-coe/litellm-vector-store-mcp/litellm-vector-store-mcp:latest
```

**Generally not needed** - automatic selection is best.

---

## 📊 Performance Comparison

### Native vs Emulated

| Platform | Native | Emulated | Performance |
|----------|--------|----------|-------------|
| **M1 Mac** | arm64 | amd64 (via Rosetta) | Native: Fast<br>Emulated: Slower |
| **Intel Mac** | amd64 | arm64 (via QEMU) | Native: Fast<br>Emulated: Very Slow |
| **Windows WSL2** | amd64 | arm64 (no support) | Native: Good |
| **Linux x86** | amd64 | arm64 (via QEMU) | Native: Fast<br>Emulated: Slow |

**Always use native architecture for best performance!**

---

## 🚀 Image Size by Platform

**Both platforms have similar sizes:**

```bash
# AMD64
~200MB compressed
~550MB uncompressed

# ARM64
~195MB compressed
~540MB uncompressed
```

**Difference is negligible** - primarily due to different binary sizes for dependencies.

---

## 🔧 Troubleshooting Platform Issues

### Error: "exec format error"

**Cause:** Trying to run wrong architecture

**Solution:**
```bash
# Remove and re-pull (let Docker auto-select)
docker rmi us-central1-docker.pkg.dev/ngfw-coe/litellm-vector-store-mcp/litellm-vector-store-mcp:latest
docker pull us-central1-docker.pkg.dev/ngfw-coe/litellm-vector-store-mcp/litellm-vector-store-mcp:latest
```

### Slow Performance

**Check if running emulated:**
```bash
# Check your system architecture
uname -m
# Returns: x86_64 (amd64) or aarch64/arm64 (arm64)

# Check pulled image architecture
docker inspect ... --format='{{.Architecture}}'

# Should match! If not, re-pull to get correct architecture
```

### M1 Mac Running Slow

**If an M1 Mac is slow:**
- Check image architecture: `docker inspect ... --format='{{.Architecture}}'`
- Should show: `arm64`
- If shows `amd64`, re-pull to get ARM version

---

## 📝 Summary

**Multi-platform support means:**
- ✅ Works on Windows, macOS (Intel & Apple Silicon), Linux
- ✅ Automatic platform detection
- ✅ Optimal performance (native binaries)
- ✅ Single `docker pull` command works everywhere
- ✅ No manual platform selection needed

**Team members can use any platform without worrying about compatibility!**

---

## 🔗 Technical References

- [Docker Multi-Platform Images](https://docs.docker.com/build/building/multi-platform/)
- [Docker Buildx](https://docs.docker.com/buildx/working-with-buildx/)
- [OCI Image Manifest](https://github.com/opencontainers/image-spec/blob/main/manifest.md)

---

**Built with:** `docker buildx build --platform linux/amd64,linux/arm64`
**Status:** ✅ Production Ready for All Platforms
