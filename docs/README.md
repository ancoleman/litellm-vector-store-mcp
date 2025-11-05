# Documentation Index

This directory contains technical documentation, architecture decisions, and implementation guides for the LiteLLM Vector Store MCP Server.

## 📚 Documentation

### Architecture & Design

- **[MULTI_VECTOR_STORE_SUPPORT.md](MULTI_VECTOR_STORE_SUPPORT.md)** - Analysis and recommendations for supporting multiple vector stores

---

## 🔍 Quick Links

### User Documentation
- [Main README](../README.md) - Overview and quick start
- [Claude Code Setup](../CLAUDE_CODE_SETUP.md) - Complete Claude Desktop/Code integration
- [Docker Deployment](../DOCKER_DEPLOYMENT.md) - Docker deployment and distribution
- [Quick Start](../QUICKSTART.md) - 5-minute setup guide
- [Usage Examples](../USAGE_EXAMPLES.md) - How Claude interprets results

### Developer Documentation
- [Improvements Summary](../IMPROVEMENTS_SUMMARY.md) - All MCP best practices applied
- [Multi-Vector Store Support](MULTI_VECTOR_STORE_SUPPORT.md) - Architecture analysis and design
- [Multi-Store Usage](MULTI_STORE_USAGE.md) - Usage guide with Claude examples
- [Multi-Platform Support](MULTI_PLATFORM_SUPPORT.md) - Platform compatibility (amd64/arm64)
- [Implementation Complete](IMPLEMENTATION_COMPLETE.md) - Multi-store feature delivery summary

---

## 📝 Document Purpose

### User-Facing Guides

**[Main README](../README.md)**
- First point of entry for all users
- Features, installation, quick start
- Links to all other documentation

**[CLAUDE_CODE_SETUP.md](../CLAUDE_CODE_SETUP.md)**
- Complete guide for connecting MCP server to Claude
- Step-by-step configuration instructions
- Troubleshooting common issues

**[DOCKER_DEPLOYMENT.md](../DOCKER_DEPLOYMENT.md)**
- Docker build, run, and distribution
- Security best practices
- Performance tuning

**[QUICKSTART.md](../QUICKSTART.md)**
- Get running in 5 minutes
- Minimal steps to success
- Quick reference commands

**[USAGE_EXAMPLES.md](../USAGE_EXAMPLES.md)**
- Real-world usage patterns
- How Claude interprets search results
- Advanced query techniques

### Technical Documentation

**[IMPROVEMENTS_SUMMARY.md](../IMPROVEMENTS_SUMMARY.md)**
- All improvements made to the server
- MCP best practices compliance
- Before/after comparisons

**[MULTI_VECTOR_STORE_SUPPORT.md](MULTI_VECTOR_STORE_SUPPORT.md)** ⭐ NEW
- Analysis of multi-store support options
- Recommended implementation approach
- Migration path for existing users

---

## 🎯 Document Categories

### By Role

**End Users:**
1. [Main README](../README.md) → Overview
2. [QUICKSTART.md](../QUICKSTART.md) → Setup
3. [CLAUDE_CODE_SETUP.md](../CLAUDE_CODE_SETUP.md) → Integration
4. [USAGE_EXAMPLES.md](../USAGE_EXAMPLES.md) → Usage

**DevOps/SRE:**
1. [DOCKER_DEPLOYMENT.md](../DOCKER_DEPLOYMENT.md) → Deployment
2. [CLAUDE_CODE_SETUP.md](../CLAUDE_CODE_SETUP.md) → Configuration

**Developers/Contributors:**
1. [IMPROVEMENTS_SUMMARY.md](../IMPROVEMENTS_SUMMARY.md) → Architecture
2. [MULTI_VECTOR_STORE_SUPPORT.md](MULTI_VECTOR_STORE_SUPPORT.md) → Design decisions
3. [Server.py](../server.py) → Source code

### By Topic

**Setup & Configuration:**
- [QUICKSTART.md](../QUICKSTART.md)
- [CLAUDE_CODE_SETUP.md](../CLAUDE_CODE_SETUP.md)
- [.env.example](../.env.example)

**Deployment:**
- [DOCKER_DEPLOYMENT.md](../DOCKER_DEPLOYMENT.md)
- [Dockerfile](../Dockerfile)
- [docker-compose.yml](../docker-compose.yml)

**Usage:**
- [Main README](../README.md)
- [USAGE_EXAMPLES.md](../USAGE_EXAMPLES.md)

**Technical:**
- [IMPROVEMENTS_SUMMARY.md](../IMPROVEMENTS_SUMMARY.md)
- [MULTI_VECTOR_STORE_SUPPORT.md](MULTI_VECTOR_STORE_SUPPORT.md)

---

## 🚀 Adding New Documentation

When adding new technical documentation:

1. Create the document in `/docs`
2. Add entry to this index
3. Link from relevant user-facing docs if applicable
4. Use clear, descriptive filenames (UPPER_SNAKE_CASE.md)

### Documentation Standards

- Use clear, descriptive headings
- Include code examples
- Provide both overview and details
- Link to related documents
- Keep table of contents updated

---

## 📮 Contributing

If you have questions not covered by existing docs:

1. Check the appropriate guide above
2. Review related documents
3. Create an issue for missing documentation
4. Submit a PR with new documentation

---

**Last Updated:** 2025-01-05
