# Changelog

All notable changes to the LiteLLM Vector Store MCP Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-05

### Added

#### Core Features
- **Multi-Vector Store Support**: Search across 7+ different framework codebases dynamically
- **Auto-Discovery**: Lists available vector stores automatically via `/vector_store/list` API
- **Two MCP Tools**:
  - `litellm_list_vector_stores` - Discover all available vector stores
  - `litellm_search_vector_store` - Search with full citations and multi-store support
- **Vector Store Resolution**: Automatically resolves friendly names to IDs
  - Use names: `"panser-corpus"`, `"internal-corpus"`
  - Use IDs: `"2341871806232657920"`
  - Use default: omit parameter
- **Multiple Response Formats**: Both Markdown (human-readable) and JSON (programmatic)
- **Character Limits**: 25,000 character limit with smart truncation
- **Full Citations**: File paths, relevance scores, content snippets with every result

#### MCP Compliance
- **FastMCP Framework**: Automatic schema generation from type hints
- **Pydantic V2 Validation**: Type-safe input validation with `model_config`
- **Tool Annotations**: Complete annotations (readOnlyHint, destructiveHint, idempotentHint, openWorldHint)
- **Comprehensive Docstrings**: 50+ line docstrings with examples, error handling, performance notes
- **Async I/O**: Non-blocking HTTP requests with httpx (replaced requests)
- **Actionable Error Messages**: Clear guidance on how to fix issues

#### Docker & Distribution
- **GCP Artifact Registry**: Pre-built images in `us-central1-docker.pkg.dev/ngfw-coe/litellm-vector-store-mcp`
- **Docker Containerization**: Production-grade multi-stage build
- **Non-root User**: Runs as `mcp` user (UID 1000) for security
- **docker-compose**: Easy orchestration with resource limits
- **Health Checks**: Container health monitoring

#### Security
- **Environment Variable Expansion**: Support for `${VAR}` in configs (no plaintext keys)
- **Docker --env-file**: Most secure method (no secrets in process args)
- **Multiple Security Levels**: 4 documented security approaches
- **Startup Validation**: Checks required env vars before starting
- **Input Validation**: Pydantic models prevent injection attacks

#### Documentation
- **9 Comprehensive Guides**: README, QUICKSTART, SECURITY, TEAM_SETUP, and more
- **3,400+ Lines of Docs**: Complete user and developer documentation
- **Claude Code Integration**: Native CLI commands and .mcp.json support
- **Usage Examples**: Real conversation examples with Claude
- **Troubleshooting**: Common issues with solutions

### Changed

#### API Integration
- **Switched from chat completions to direct vector store search**: Enables full citation support
- **HTTP Client**: Migrated from `requests` to `httpx` for async operations

#### Configuration
- **Security**: Changed from hardcoded credentials to environment-based configuration
- **Scopes**: Support for user, local, and project-level configurations
- **Registry**: All references updated to use GCP Artifact Registry instead of local builds

### Fixed

#### Security Issues
- **API Key Exposure**: Replaced all real API keys in documentation with placeholders
- **Plaintext Credentials**: Eliminated hardcoded secrets in all example configs
- **Process Visibility**: Using --env-file prevents key exposure in `/mcp` status

#### Error Handling
- **Authentication Errors**: Now provide specific guidance on checking API keys
- **Missing Stores**: Helpful error lists all available stores when name not found
- **Network Errors**: Specific messages for timeouts, connection failures, rate limits

### Technical Details

#### Dependencies
- `mcp>=1.1.2` - Model Context Protocol Python SDK
- `httpx>=0.27.0` - Async HTTP client
- `pydantic>=2.0.0` - Data validation
- `python-dotenv>=1.0.0` - Environment variable loading

#### MCP Server
- **Name**: `litellm_vector_store_mcp` (follows Python naming convention)
- **Tools**: 2 (list + search)
- **Transport**: Stdio (standard input/output)
- **Server Framework**: FastMCP

#### Docker Image
- **Base**: Python 3.12-slim
- **Size**: ~200MB
- **User**: Non-root (mcp:1000)
- **Registry**: `us-central1-docker.pkg.dev/ngfw-coe/litellm-vector-store-mcp/litellm-vector-store-mcp`
- **Tags**: `latest`, `v0.1.0`

### Performance

- **Search Response**: 2-5 seconds typical
- **List Stores**: 1-2 seconds
- **Character Limit**: 25,000 chars with smart truncation
- **Timeout**: 30 seconds for API requests

### Compatibility

- **Python**: 3.10+ required
- **Claude Code**: 2.0.33+ recommended
- **Docker**: Any recent version
- **Platform**: macOS, Linux, Windows (via Docker)

---

## [Unreleased]

### Planned Features

- Cache store list for improved performance
- Search multiple stores in single query
- Store-specific search parameters
- Advanced filtering options
- CI/CD pipeline for automatic builds

---

## Version History

- **v0.1.0** (2025-01-05) - Initial production release
  - Multi-vector store support
  - GCP Artifact Registry deployment
  - Complete documentation
  - Security hardening

---

## Migration Guide

### From Local Build to Registry

**Old setup:**
```bash
docker build -t litellm-vector-store-mcp:latest .
```

**New setup:**
```bash
docker pull us-central1-docker.pkg.dev/ngfw-coe/litellm-vector-store-mcp/litellm-vector-store-mcp:latest
```

### From Plaintext to Secure Config

**Old config:**
```json
"-e", "LITELLM_API_KEY=sk-plaintext-key"
```

**New config:**
```json
"--env-file", "/path/to/.env"
```

---

## Links

- **GCP Artifact Registry**: [us-central1-docker.pkg.dev/ngfw-coe/litellm-vector-store-mcp](https://console.cloud.google.com/artifacts/docker/ngfw-coe/us-central1/litellm-vector-store-mcp)
- **MCP Protocol**: [https://modelcontextprotocol.io](https://modelcontextprotocol.io)
- **LiteLLM Docs**: [https://docs.litellm.ai](https://docs.litellm.ai)

---

**Note:** This changelog documents changes from initial development to v0.1.0. Future releases will document incremental changes.
