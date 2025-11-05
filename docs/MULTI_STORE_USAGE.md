# Multi-Vector Store Usage Guide

This guide shows how to use the MCP server to work with multiple vector stores, including discovering available stores and searching specific codebases.

## 🎯 Overview

Your LiteLLM instance has **7 vector stores** available:

| Name | Description | ID |
|------|-------------|-----|
| **panser-corpus** | Panser framework code | 612489549322387456 |
| **migrationmanager-corpus** | Migration Manager framework | 2233785415175766016 |
| **companion-corpus** | Companion framework | 5692549928996306944 |
| **mcp-servers-corpus** | MCP Servers framework | 3530822107858468864 |
| **prismaautomation-corpus** | Prisma Automation framework | 9151314442816847872 |
| **internal-corpus** | Internal framework (LiteLLM deployment) | 2341871806232657920 |
| **gcsai-corpus** | GCSAI framework | 5800636320053198848 |

---

## 📚 Available Tools

### 1. `litellm_list_vector_stores`

Discover all available vector stores.

**Usage with Claude:**
```
What vector stores are available?
```

```
List all code repositories I can search
```

```
Show me all the vector stores
```

**Returns:**
```markdown
# Available Vector Stores

**Total Stores:** 7

## 1. panser-corpus
- **ID:** `612489549322387456`
- **Description:** Code corpus for Panser framework
- **Provider:** vertex_ai

**Usage:** `vector_store="panser-corpus"` or `vector_store="612489549322387456"`
...
```

### 2. `litellm_search_vector_store`

Search a specific vector store (or default).

**Parameters:**
- `query`: Search query
- `max_results`: Number of results (1-20)
- `response_format`: "markdown" or "json"
- `vector_store`: Store name or ID (optional)

---

## 🎭 User Experience with Claude

### Scenario 1: Discovery Workflow

**Step 1: Ask Claude what's available**
```
User: What vector stores can I search?

Claude: [Calls litellm_list_vector_stores]
You have access to 7 vector stores:

1. **panser-corpus** - Panser framework code
2. **migrationmanager-corpus** - Migration Manager framework
3. **companion-corpus** - Companion framework
4. **mcp-servers-corpus** - MCP Servers framework
5. **prismaautomation-corpus** - Prisma Automation framework
6. **internal-corpus** - Internal framework (LiteLLM deployment)
7. **gcsai-corpus** - GCSAI framework

Which one would you like to search?
```

**Step 2: Search specific store**
```
User: Search the panser-corpus for authentication code

Claude: [Calls litellm_search_vector_store with vector_store="panser-corpus"]
I found authentication code in the Panser framework:

## Result 1: access_token.md (Score: 0.6272)
The PANser Webservice implements JWT-based authentication...
[Shows code and explanation]
```

---

### Scenario 2: Direct Search (No Discovery)

**User already knows which store:**
```
User: Search the internal-corpus for Redis configuration

Claude: [Calls litellm_search_vector_store with vector_store="internal-corpus"]
Here's how Redis is configured in the internal framework:

[Shows Redis Stack YAML configuration from internal-corpus]
```

---

### Scenario 3: Cross-Store Comparison

**Compare implementations across codebases:**
```
User: How is authentication handled in panser vs companion?

Claude: Let me search both codebases...

[Calls litellm_search_vector_store with vector_store="panser-corpus", query="authentication"]
[Calls litellm_search_vector_store with vector_store="companion-corpus", query="authentication"]

**Panser Framework:**
- Uses JWT tokens with OAuth 2.0
- Implements access tokens with refresh capability
- Stores tokens in Redis cache

**Companion Framework:**
- Uses API key-based authentication
- Implements rate limiting per key
- Stores keys in Cloud SQL

The main difference is that Panser uses OAuth/JWT for user authentication,
while Companion uses simpler API keys for service-to-service auth.
```

---

### Scenario 4: Finding the Right Store

**User doesn't know which store to search:**
```
User: I need to find code related to Prisma Cloud automation

Claude: Let me check which vector stores are available...

[Calls litellm_list_vector_stores]

I see there's a "prismaautomation-corpus" that looks relevant.
Let me search that for you.

[Calls litellm_search_vector_store with vector_store="prismaautomation-corpus"]

Found several Prisma Cloud automation files...
```

---

### Scenario 5: Search All Stores (Sequential)

**User wants to search everything:**
```
User: Search all vector stores for "Docker deployment" examples

Claude: I'll search across all 7 vector stores for Docker deployment examples.

[Calls litellm_search_vector_store 7 times, once per store]

Here's what I found across all codebases:

**internal-corpus (3 results):**
- Docker Compose for Redis Stack
- LiteLLM Cloud Run deployment
- Bastion VM configuration

**panser-corpus (2 results):**
- PANser Docker container setup
- Multi-stage build examples

**mcp-servers-corpus (5 results):**
- MCP server Dockerfiles
- Development container configs
- Production deployment patterns

The most comprehensive Docker examples are in the mcp-servers-corpus.
```

---

## 💡 Query Patterns

### Simple Queries (Uses Default Store)

```
"Find Redis configuration"
"Show me the GKE module"
"Search for Cloud Build scripts"
```

Claude uses the default vector store from `LITELLM_VECTOR_STORE_ID`.

### Named Store Queries

```
"Search panser-corpus for authentication"
"Find Docker configs in mcp-servers-corpus"
"Look for deployment scripts in internal-corpus"
```

Claude extracts the store name and passes it to the tool.

### Direct ID Queries (Rare)

```
"Search vector store 612489549322387456 for examples"
```

Claude uses the direct ID (useful for stores not configured).

### Discovery Queries

```
"What vector stores are available?"
"List all code repositories"
"Show me what I can search"
```

Claude calls `litellm_list_vector_stores`.

---

## 🔧 Technical Details

### Name Resolution

When you specify `vector_store="panser-corpus"`, the MCP server:

1. Checks if it's a direct ID (all digits) → Use as-is
2. If not, calls `/vector_store/list` to get all stores
3. Finds the store with matching `vector_store_name`
4. Extracts its `vector_store_id`
5. Uses that ID for the search

**Example:**
```python
# User specifies name
vector_store="panser-corpus"

# Server resolves to ID
resolved_id = "612489549322387456"

# Searches using ID
POST /v1/vector_stores/612489549322387456/search
```

### Error Handling

**Invalid store name:**
```
Error: Vector store 'invalid-name' not found.
Available stores: panser-corpus, migrationmanager-corpus, companion-corpus,
mcp-servers-corpus, prismaautomation-corpus, internal-corpus, gcsai-corpus.
Use litellm_list_vector_stores tool to see all options.
```

**No access:**
```
Error: Authentication failed. Please check your LITELLM_API_KEY
is valid and has access to the vector store.
```

---

## 🎯 Best Practices

### 1. Discover First, Search Second

**Recommended workflow:**
```
User: What stores are available?
[Claude lists stores]

User: Search the one about MCP servers for FastMCP examples
[Claude searches mcp-servers-corpus]
```

### 2. Use Descriptive Names in Queries

**Good:**
```
"Search panser-corpus for OAuth implementation"
"Find deployment configs in internal-corpus"
```

**Less Good:**
```
"Search for OAuth in panser"  # "panser" might not match "panser-corpus"
"Find stuff in 612489549322387456"  # IDs are hard to remember
```

### 3. Default Store for General Queries

**If you're primarily working with one codebase:**
```
# Set as default in .env
LITELLM_VECTOR_STORE_ID=2341871806232657920  # internal-corpus

# Then simple queries just work
"Find Redis config"  # Searches internal-corpus automatically
```

### 4. Specify Store for Cross-Repository Work

**When working across multiple frameworks:**
```
"Compare authentication in panser vs companion"
"Find all Docker setups across all frameworks"
"Show me MCP server implementations in mcp-servers-corpus"
```

---

## 📊 Response Formats

### Markdown (Default - Human-Readable)

```
# Available Vector Stores

**Total Stores:** 7

## 1. panser-corpus
- **ID:** `612489549322387456`
- **Description:** Code corpus for Panser framework
```

**Best for:**
- Reading and understanding
- Presenting to users
- Quick scanning

### JSON (Programmatic)

```json
{
  "total_count": 7,
  "vector_stores": [
    {
      "id": "612489549322387456",
      "name": "panser-corpus",
      "description": "Code corpus for Panser framework",
      "provider": "vertex_ai",
      "created_at": "2025-11-04T11:35:33.602632Z"
    }
  ]
}
```

**Best for:**
- Processing with scripts
- Extracting specific fields
- Integration with other tools

---

## 🚀 Advanced Usage

### Batch Search Across Multiple Stores

**Find the same thing in all frameworks:**
```
User: Search all frameworks for how they handle rate limiting

Claude: Let me search across all 7 vector stores...

[Makes 7 search calls, one per store]

**Results Summary:**

panser-corpus: Uses token bucket algorithm
migrationmanager-corpus: Implements sliding window rate limit
companion-corpus: Uses Redis for distributed rate limiting
...
```

### Intelligent Store Selection

**Claude can choose the right store:**
```
User: I'm working on Prisma automation, find the deployment scripts

Claude: Based on your context, I'll search the prismaautomation-corpus...

[Searches prismaautomation-corpus automatically]
```

### Combined Discovery + Search

**Single query that does both:**
```
User: Find me the best place to look for MCP server examples and show me some

Claude: [Calls litellm_list_vector_stores]
I can see there's a dedicated "mcp-servers-corpus" for MCP server code.

[Calls litellm_search_vector_store with vector_store="mcp-servers-corpus"]

Here are MCP server examples from that codebase:
[Shows results]
```

---

## 🎓 Common Scenarios

### DevOps Engineer

```
"List all infrastructure codebases"
→ [Lists 7 stores]

"Search internal-corpus for GKE configuration"
→ [Finds GKE Terraform modules]

"Now search gcsai-corpus for the same thing"
→ [Compares implementations]
```

### Software Engineer

```
"What frameworks have authentication code?"
→ [Searches panser, companion, others for "authentication"]

"Show me the JWT implementation in panser-corpus"
→ [Finds PANser OAuth/JWT code]
```

### Documentation Writer

```
"Search all stores for README files"
→ [Finds documentation across all frameworks]

"Which framework has the best deployment docs?"
→ [Compares deployment documentation quality]
```

---

## 📝 Summary

The MCP server now supports:

✅ **Automatic Discovery**: List all 7 vector stores dynamically
✅ **Name Resolution**: Use friendly names like "panser-corpus"
✅ **Direct IDs**: Support numeric IDs for flexibility
✅ **Default Fallback**: Works without specifying store
✅ **Error Guidance**: Helpful messages when store not found
✅ **Cross-Store Search**: Search multiple stores in one conversation

**User Experience:**
- Natural language queries
- Claude handles all the complexity
- Transparent store resolution
- Clear, actionable errors

**Ready for production use across all your frameworks! 🚀**
