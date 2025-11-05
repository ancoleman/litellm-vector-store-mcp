# Multi-Vector Store Support Analysis

This document analyzes different approaches for supporting multiple LiteLLM vector stores in the MCP server and provides implementation recommendations.

## Current Limitation

**Status:** The MCP server currently supports only **ONE vector store** per instance.

**Implementation:**
```python
# In server.py
VECTOR_STORE_ID = os.getenv("LITELLM_VECTOR_STORE_ID")  # Single store only

# All searches go to this single store
url = f"{API_BASE_URL}/v1/vector_stores/{VECTOR_STORE_ID}/search"
```

**Limitations:**
- ❌ Can only search ONE vector store per MCP server instance
- ❌ Users cannot choose which store to search at query time
- ❌ Cannot search across multiple stores
- ❌ Requires multiple MCP server instances for multiple stores

---

## Solution Options

### Option 1: Add `vector_store_id` Parameter ⭐ Recommended

**Description:** Make the vector store selectable per query by adding an optional parameter.

**Implementation:**

```python
class VectorStoreSearchInput(BaseModel):
    query: str = Field(...)
    max_results: int = Field(default=5, ge=1, le=20)
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)

    # NEW: Optional parameter to override default vector store
    vector_store_id: Optional[str] = Field(
        default=None,
        description=(
            "Vector store ID to search (optional). If not provided, uses the "
            "default from LITELLM_VECTOR_STORE_ID. "
            "Examples: '2341871806232657920', 'production-docs', 'dev-codebase'"
        )
    )
```

**Search function update:**
```python
async def _make_vector_store_request(
    query: str,
    max_results: int,
    vector_store_id: Optional[str] = None
) -> Dict[str, Any]:
    # Use provided ID or fall back to default
    store_id = vector_store_id or VECTOR_STORE_ID

    url = f"{API_BASE_URL}/v1/vector_stores/{store_id}/search"
    # ... rest of the code
```

**User Experience:**

```
# Search default vector store
User: "Search for Redis configuration"
Claude: [Uses default LITELLM_VECTOR_STORE_ID]

# Search specific vector store
User: "Search vector store '2341871806232657920' for Redis configuration"
Claude: [Uses specified vector_store_id parameter]
```

**Pros:**
- ✅ Simple implementation (minimal code changes)
- ✅ Backward compatible (defaults to env var)
- ✅ Single MCP server instance needed
- ✅ Flexible - supports any vector store ID

**Cons:**
- ⚠️ Users must know/remember vector store IDs
- ⚠️ IDs are not human-friendly (long numbers)

---

### Option 2: Multiple MCP Server Instances

**Description:** Run separate MCP server instances, one per vector store.

**Claude Desktop Configuration:**

```json
{
  "mcpServers": {
    "litellm-production": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-e", "LITELLM_VECTOR_STORE_ID=production-store-id",
        "--env-file", "/path/.env",
        "litellm-vector-store-mcp:latest"
      ]
    },
    "litellm-development": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-e", "LITELLM_VECTOR_STORE_ID=dev-store-id",
        "--env-file", "/path/.env",
        "litellm-vector-store-mcp:latest"
      ]
    },
    "litellm-documentation": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-e", "LITELLM_VECTOR_STORE_ID=docs-store-id",
        "--env-file", "/path/.env",
        "litellm-vector-store-mcp:latest"
      ]
    }
  }
}
```

**User Experience:**

```
# Claude sees multiple separate tools:
- litellm-production___search_vector_store
- litellm-development___search_vector_store
- litellm-documentation___search_vector_store

# User specifies which to use:
User: "Search the production vector store for Redis config"
Claude: [Calls litellm-production___search_vector_store]

User: "Search the development vector store for the same thing"
Claude: [Calls litellm-development___search_vector_store]
```

**Pros:**
- ✅ No code changes required
- ✅ Clear separation between stores
- ✅ Can use different configurations per store

**Cons:**
- ❌ Multiple Docker containers running
- ❌ More complex Claude Desktop configuration
- ❌ Higher resource usage (multiple server instances)
- ❌ Tool names become verbose with prefixes

---

### Option 3: List + Search Pattern

**Description:** Add a tool to list available vector stores, then allow searching by ID.

**Implementation:**

```python
@mcp.tool(name="litellm_list_vector_stores")
async def litellm_list_vector_stores() -> str:
    """List all available vector stores.

    Returns a list of vector store IDs and their descriptions to help
    users choose which store to search.

    Returns:
        str: JSON-formatted list of available vector stores
    """
    # Could be hardcoded config or fetched from LiteLLM API
    stores = {
        "2341871806232657920": {
            "name": "Production Codebase",
            "description": "Main production code (frameworks/internal)",
            "size": "~500 files",
            "last_updated": "2024-01-15"
        },
        "1234567890123456789": {
            "name": "Development Codebase",
            "description": "Active development code",
            "size": "~300 files",
            "last_updated": "2024-01-20"
        },
        "9876543210987654321": {
            "name": "Documentation",
            "description": "API docs, guides, and README files",
            "size": "~150 files",
            "last_updated": "2024-01-18"
        }
    }

    return json.dumps(stores, indent=2)

@mcp.tool(name="litellm_search_vector_store")
async def litellm_search_vector_store(params: VectorStoreSearchInput) -> str:
    # Include vector_store_id parameter as in Option 1
    pass
```

**User Experience:**

```
User: "What vector stores are available?"

Claude: [Calls litellm_list_vector_stores]
You have access to these vector stores:

1. **Production Codebase** (ID: 2341871806232657920)
   - Main production code (frameworks/internal)
   - ~500 files
   - Last updated: 2024-01-15

2. **Development Codebase** (ID: 1234567890123456789)
   - Active development code
   - ~300 files
   - Last updated: 2024-01-20

3. **Documentation** (ID: 9876543210987654321)
   - API docs, guides, and README files
   - ~150 files
   - Last updated: 2024-01-18

User: "Search the documentation store for API examples"

Claude: [Calls search with vector_store_id="9876543210987654321"]
[Returns results from docs-only store]
```

**Pros:**
- ✅ Discoverable - users can see available stores
- ✅ Single MCP server instance
- ✅ Provides context about each store

**Cons:**
- ⚠️ Two-step process (list, then search)
- ⚠️ Requires maintaining store metadata
- ⚠️ Store list could become outdated

---

### Option 4: Named Vector Stores in Configuration

**Description:** Configure multiple stores with friendly names in environment variables.

**Configuration (.env):**

```env
# Default vector store
LITELLM_VECTOR_STORE_ID=2341871806232657920

# Named vector stores (optional)
LITELLM_VECTOR_STORE_PRODUCTION=2341871806232657920
LITELLM_VECTOR_STORE_DEVELOPMENT=1234567890123456789
LITELLM_VECTOR_STORE_DOCS=9876543210987654321

# Store descriptions (optional, for documentation)
LITELLM_VECTOR_STORE_PRODUCTION_DESC="Production codebase"
LITELLM_VECTOR_STORE_DEVELOPMENT_DESC="Development codebase"
LITELLM_VECTOR_STORE_DOCS_DESC="Documentation only"
```

**Implementation:**

```python
# Configuration at top of server.py
DEFAULT_VECTOR_STORE_ID = os.getenv("LITELLM_VECTOR_STORE_ID")

# Named vector stores (optional, for convenience)
VECTOR_STORES = {
    "default": os.getenv("LITELLM_VECTOR_STORE_ID"),
    "production": os.getenv("LITELLM_VECTOR_STORE_PRODUCTION", DEFAULT_VECTOR_STORE_ID),
    "development": os.getenv("LITELLM_VECTOR_STORE_DEVELOPMENT"),
    "docs": os.getenv("LITELLM_VECTOR_STORE_DOCS"),
}

# Filter out None values
VECTOR_STORES = {k: v for k, v in VECTOR_STORES.items() if v}

class VectorStoreSearchInput(BaseModel):
    query: str = Field(...)
    vector_store: str = Field(
        default="default",
        description=(
            "Vector store to search. Can be a named store like 'production', "
            "'development', 'docs', or 'default'. "
            "Available stores depend on configuration."
        )
    )
```

**User Experience:**

```
User: "Search the development vector store for Redis config"
Claude: [Calls search with vector_store="development"]

User: "Search the docs vector store for API examples"
Claude: [Calls search with vector_store="docs"]

User: "Search production for deployment scripts"
Claude: [Calls search with vector_store="production"]
```

**Pros:**
- ✅ Human-friendly names ("production" vs "2341871806232657920")
- ✅ Single MCP server instance
- ✅ Easy to configure in .env file

**Cons:**
- ⚠️ Requires pre-configuration of named stores
- ⚠️ Less flexible for ad-hoc searches
- ⚠️ Cannot search arbitrary vector store IDs

---

## Recommended Solution: Hybrid Approach (Option 1 + 4)

**Combine named stores with direct ID support for maximum flexibility.**

### Implementation

```python
# Configuration at top of server.py
DEFAULT_VECTOR_STORE_ID = os.getenv("LITELLM_VECTOR_STORE_ID")

# Named vector stores (optional, for convenience)
VECTOR_STORES = {
    "default": os.getenv("LITELLM_VECTOR_STORE_ID"),
    "production": os.getenv("LITELLM_VECTOR_STORE_PRODUCTION", DEFAULT_VECTOR_STORE_ID),
    "development": os.getenv("LITELLM_VECTOR_STORE_DEVELOPMENT"),
    "docs": os.getenv("LITELLM_VECTOR_STORE_DOCS"),
}

# Filter out None values
VECTOR_STORES = {k: v for k, v in VECTOR_STORES.items() if v}

class VectorStoreSearchInput(BaseModel):
    """Input model for vector store search operations."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    query: str = Field(...)
    max_results: int = Field(default=5, ge=1, le=20)
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)

    vector_store: Optional[str] = Field(
        default=None,
        description=(
            "Vector store to search. Can be:\n"
            "- A named store: 'production', 'development', 'docs'\n"
            "- A direct ID: '2341871806232657920'\n"
            "- Omit to use default vector store\n\n"
            f"Available named stores: {', '.join(VECTOR_STORES.keys())}\n\n"
            "Examples:\n"
            "  - 'production' (uses named store)\n"
            "  - '2341871806232657920' (uses direct ID)\n"
            "  - null/omit (uses default)"
        )
    )

async def _make_vector_store_request(
    query: str,
    max_results: int,
    vector_store: Optional[str] = None
) -> Dict[str, Any]:
    """Make an async request to the LiteLLM vector store search endpoint.

    Args:
        query: Search query string
        max_results: Maximum number of results to return
        vector_store: Named store or direct ID (optional)

    Returns:
        Dict containing search results or error information

    Raises:
        ValueError: If named store is not configured
        httpx.HTTPStatusError: If the API request fails
        httpx.TimeoutException: If the request times out
    """
    # Resolve vector store ID
    if vector_store is None:
        # Use default from env
        store_id = DEFAULT_VECTOR_STORE_ID
    elif vector_store in VECTOR_STORES:
        # Named store
        store_id = VECTOR_STORES[vector_store]
        if not store_id:
            available = ', '.join(k for k, v in VECTOR_STORES.items() if v)
            raise ValueError(
                f"Vector store '{vector_store}' is not configured. "
                f"Available stores: {available}"
            )
    else:
        # Assume it's a direct ID
        store_id = vector_store

    url = f"{API_BASE_URL}/v1/vector_stores/{store_id}/search"

    # ... rest of the implementation
```

### Configuration Example

**.env file:**
```env
# Default vector store (required)
LITELLM_VECTOR_STORE_ID=2341871806232657920
LITELLM_API_KEY=sk-your-key

# Optional: Named vector stores for convenience
LITELLM_VECTOR_STORE_PRODUCTION=2341871806232657920
LITELLM_VECTOR_STORE_DEVELOPMENT=1234567890123456789
LITELLM_VECTOR_STORE_DOCS=9876543210987654321
```

### User Experience

```
# Use default (no specification needed)
User: "Search for Redis configuration"
Claude: [Uses default LITELLM_VECTOR_STORE_ID]

# Use named store (friendly names)
User: "Search the development vector store for Redis config"
Claude: [Uses LITELLM_VECTOR_STORE_DEVELOPMENT]

User: "Search the docs store for API examples"
Claude: [Uses LITELLM_VECTOR_STORE_DOCS]

# Use direct ID (for ad-hoc searches)
User: "Search vector store 9999999999999999999 for examples"
Claude: [Uses direct ID 9999999999999999999]
```

### Benefits

**Maximum Flexibility:**
- ✅ Named stores for common use cases (production, dev, docs)
- ✅ Direct IDs for one-off searches
- ✅ Default fallback for simple queries

**User-Friendly:**
- ✅ Natural language: "search the dev store"
- ✅ No need to remember long IDs for common stores
- ✅ Still supports arbitrary store IDs when needed

**Simple Configuration:**
- ✅ Optional named stores in .env
- ✅ Backward compatible (works with just default ID)
- ✅ Single MCP server instance

**Robust:**
- ✅ Validates named stores exist
- ✅ Clear error messages when store not configured
- ✅ Lists available stores in error messages

---

## Comparison Table

| Feature | Option 1 | Option 2 | Option 3 | Option 4 | Hybrid |
|---------|----------|----------|----------|----------|--------|
| **Complexity** | Low | Medium | Medium | Low | Low |
| **Flexibility** | High | Medium | High | Medium | Very High |
| **User-Friendly** | Medium | Low | Medium | High | Very High |
| **Resource Usage** | Low | High | Low | Low | Low |
| **Config Complexity** | Low | High | Medium | Medium | Medium |
| **Backward Compatible** | Yes | Yes | Yes | Yes | Yes |
| **Discoverable** | No | No | Yes | No | Partially |
| **Single Instance** | Yes | No | Yes | Yes | Yes |

**Legend:**
- ✅ Excellent
- ☑️ Good
- ⚠️ Fair
- ❌ Poor

---

## Implementation Steps

### Minimal Implementation (Quick Win)

**Just add `vector_store_id` parameter:**

```python
# 1. Update input model
class VectorStoreSearchInput(BaseModel):
    # ... existing fields
    vector_store_id: Optional[str] = Field(
        default=None,
        description="Vector store ID to search (optional, uses default if not provided)"
    )

# 2. Update request function
async def _make_vector_store_request(query: str, max_results: int, vector_store_id: Optional[str] = None):
    store_id = vector_store_id or VECTOR_STORE_ID
    url = f"{API_BASE_URL}/v1/vector_stores/{store_id}/search"
    # ... rest of code

# 3. Pass parameter through
results = await _make_vector_store_request(params.query, params.max_results, params.vector_store_id)
```

**Done!** Users can now optionally specify which store to search.

### Full Implementation (Recommended)

**Add named stores + direct ID support:**

1. **Update configuration section** (top of server.py)
2. **Update `VectorStoreSearchInput`** with `vector_store` parameter
3. **Update `_make_vector_store_request`** with ID resolution logic
4. **Update `.env.example`** with named store examples
5. **Update documentation** to explain usage

See code examples in **Recommended Solution** section above.

---

## Migration Path

### For Existing Users

**No breaking changes:**
- ✅ Existing configs continue to work
- ✅ Default vector store unchanged
- ✅ New parameter is optional

**To enable multi-store support:**
1. Update to new server version
2. Add named stores to `.env` (optional)
3. Restart MCP server
4. Use named stores or direct IDs in queries

### For New Users

**Recommended setup:**
```env
# Always required
LITELLM_API_KEY=sk-your-key
LITELLM_VECTOR_STORE_ID=your-default-store-id

# Optional: Add named stores if you have multiple
LITELLM_VECTOR_STORE_PRODUCTION=production-store-id
LITELLM_VECTOR_STORE_DEVELOPMENT=dev-store-id
```

---

## Future Enhancements

### Potential Additions

1. **Auto-discovery**: Query LiteLLM API for available vector stores
2. **Store metadata**: Descriptions, file counts, last updated
3. **Cross-store search**: Search multiple stores in one query
4. **Store aliases**: User-defined friendly names
5. **Default store per query type**: Route queries based on content

### Example: Auto-Discovery

```python
@mcp.tool(name="litellm_list_vector_stores")
async def litellm_list_vector_stores() -> str:
    """List all vector stores available in LiteLLM."""
    # Query LiteLLM API for stores
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE_URL}/v1/vector_stores",
            headers={"Authorization": f"Bearer {API_KEY}"}
        )
        stores = response.json()

    return json.dumps(stores, indent=2)
```

---

## Conclusion

**Recommended Approach:** Hybrid (Option 1 + 4)

This provides:
- **Simplicity**: Minimal code changes
- **Flexibility**: Named stores + direct IDs
- **User Experience**: Natural language queries
- **Backward Compatibility**: No breaking changes
- **Scalability**: Easy to add more stores

**Implementation Priority:**
1. **Phase 1**: Add `vector_store` parameter (enables multi-store)
2. **Phase 2**: Add named store configuration (improves UX)
3. **Phase 3**: Add store listing tool (aids discovery)

**Quick Start:** Just implement Phase 1 for immediate multi-store support.

---

## References

- [MCP Best Practices](../reference/mcp_best_practices.md)
- [LiteLLM Vector Store API](https://docs.litellm.ai/docs/completion/knowledgebase)
- [Server Implementation](../server.py)
