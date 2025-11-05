# Usage Examples

## How Claude Interprets Search Results

When you use this MCP server, Claude receives structured search results and can interpret them to answer your questions.

### Example 1: Finding Configuration Details

**Your Question:**
```
Search the vector store for how Redis Stack is configured
```

**What Happens:**
1. Claude calls `search_vector_store` with query: "how Redis Stack is configured"
2. The MCP server searches your vector store
3. Results are returned with:
   - File paths (e.g., `redis-stack.yaml.txt`)
   - Relevance scores (e.g., 0.3118)
   - Content snippets (full YAML configuration)
4. Claude reads and interprets the results

**Claude's Response:**
```
Based on the vector store search results, here's how Redis Stack is configured:

## Configuration Overview

The Redis Stack instance is deployed as a Kubernetes StatefulSet with the following key settings:

**Resource Limits:**
- CPU: 4000m request, 8000m limit
- Memory: 16Gi request, 32Gi limit
- Storage: 100Gi persistent volume

**Redis Configuration:**
- Maximum memory: 25GB with allkeys-lru eviction policy
- Persistence: RDB snapshots (900s, 300s, 60s intervals)
- Authentication: Password-based via Kubernetes secret

**Network Setup:**
- Headless service for StatefulSet
- Internal LoadBalancer for VPC access
- Port 6379 for Redis protocol

The configuration is sourced from: `redis-stack.yaml.txt` (Score: 0.3118)
```

### Example 2: Understanding Implementation

**Your Question:**
```
How is the GKE cluster configured? Use the vector store to find details.
```

**Claude's Response:**
```
I'll search the vector store for GKE cluster configuration details.

[Calls search_vector_store tool with query: "GKE cluster configuration"]

Based on the search results, the GKE cluster is configured as:

## GKE Autopilot Configuration

**Cluster Type:** Fully managed Autopilot mode
- Google handles all node management and scaling
- Pay-per-pod pricing model

**Network Configuration:**
- Private cluster with no public endpoints
- Uses existing VPC for connectivity
- Secondary IP ranges for pods (gke-pods) and services (gke-services)
- Master CIDR: [from your config]

**Security:**
- Workload Identity enabled for GCP API access
- Master authorized networks restrict API access
- Private nodes with no external IPs

**Monitoring:**
- Managed Prometheus enabled
- System component and workload logging

Source: `modules/gke-autopilot/main.tf.txt` (Score: 0.3948)
```

### Example 3: Finding Code Examples

**Your Question:**
```
Show me examples of how Terraform modules are structured in this project
```

**Claude's Response:**
```
Let me search the vector store for Terraform module examples.

[Calls search_vector_store tool]

Here are the Terraform module patterns used in your project:

## Module Structure

**Variables Pattern:**
Each module has a `variables.tf` with:
- Input validation
- Sensible defaults
- Clear descriptions

Example from the Redis module:
```hcl
variable "tier" {
  description = "Redis tier - BASIC or STANDARD_HA"
  type        = string
  default     = "BASIC"

  validation {
    condition     = contains(["BASIC", "STANDARD_HA"], var.tier)
    error_message = "Tier must be BASIC or STANDARD_HA"
  }
}
```

**Outputs Pattern:**
Modules expose connection strings and resource IDs:
```hcl
output "redis_connection_string" {
  description = "Redis connection string for LiteLLM"
  value       = "redis://..."
  sensitive   = true
}
```

Sources: `modules/redis/variables.tf.txt`, `modules/redis/outputs.tf.txt`
```

## Interactive Workflow

### Multi-Step Research

You can ask Claude to do multi-step research using the vector store:

```
1. First, search for how Redis is configured
2. Then search for how it's used in the LiteLLM deployment
3. Explain the complete data flow
```

Claude will:
1. Make multiple `search_vector_store` calls
2. Synthesize information across results
3. Provide a comprehensive explanation

### Code Comparison

```
Compare how Redis is configured in the Memorystore module versus the Redis Stack K8s module
```

Claude will:
1. Search for both configurations
2. Extract key differences
3. Explain trade-offs between approaches

### Finding Related Files

```
Find all files related to semantic caching in the infrastructure
```

Claude will:
1. Search for "semantic caching"
2. List all related files with relevance scores
3. Summarize how caching is implemented across the stack

## Tips for Best Results

### 1. Be Specific

✅ Good: "Show me the Redis Stack StatefulSet configuration"
❌ Less Good: "Tell me about Redis"

### 2. Use Technical Terms

✅ Good: "Find Terraform modules that create GKE clusters"
❌ Less Good: "How is Kubernetes set up?"

### 3. Ask for Multiple Results

```
Search the vector store for Cloud Build configurations, return 10 results
```

This gives Claude more context to work with.

### 4. Chain Queries

```
1. Search for the VPC module
2. Based on that, search for how it's used in the GKE module
3. Explain the network architecture
```

### 5. Request Code Snippets

```
Find examples of how environment variables are injected in Cloud Build configs
```

Claude will extract and explain the relevant code sections.

## Understanding Search Scores

- **0.8 - 1.0**: Extremely relevant, exact matches
- **0.5 - 0.8**: Highly relevant, strong semantic match
- **0.3 - 0.5**: Relevant, contains useful information
- **0.0 - 0.3**: Weakly relevant, may have partial matches

Claude considers these scores when prioritizing which results to focus on.

## Advanced Usage

### Debugging Issues

```
Search for how IAP tunnels are configured and explain why kubectl might not connect
```

Claude will:
1. Find IAP tunnel configuration
2. Find kubectl configuration
3. Identify potential connection issues
4. Suggest fixes

### Architecture Documentation

```
Create a diagram of how all the infrastructure components connect, based on the vector store
```

Claude will:
1. Search for each component
2. Extract connection patterns
3. Generate a textual diagram (or suggest a tool for visualization)

### Migration Planning

```
We want to migrate from Memorystore Redis to Redis Stack on GKE.
Search for both configurations and create a migration plan.
```

Claude will:
1. Compare both configurations
2. Identify differences in connection strings, features, etc.
3. Suggest migration steps
