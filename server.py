#!/usr/bin/env python3
"""
LiteLLM Vector Store MCP Server

A Model Context Protocol server that enables Claude to search your LiteLLM vector stores
for relevant code and documentation with semantic search capabilities.
"""

import json
import os
import sys
from enum import Enum
from typing import Any, Dict, List, Optional

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, field_validator, ConfigDict

# Load environment variables from .env file
load_dotenv()

# Initialize the MCP server with proper naming convention
mcp = FastMCP("litellm_vector_store_mcp")

# Constants
CHARACTER_LIMIT = 25000  # Maximum response size in characters
API_BASE_URL = os.getenv("LITELLM_BASE_URL", "https://litellm.psolabs.com")
API_KEY = os.getenv("LITELLM_API_KEY")
VECTOR_STORE_ID = os.getenv("LITELLM_VECTOR_STORE_ID")
VERTEX_AI_PROJECT = os.getenv("VERTEX_AI_PROJECT")
VERTEX_AI_LOCATION = os.getenv("VERTEX_AI_LOCATION", "us-east4")

# Validate required environment variables on startup
if not API_KEY:
    print(
        "ERROR: LITELLM_API_KEY environment variable is required. "
        "Set it in your .env file or environment.",
        file=sys.stderr,
    )
    sys.exit(1)

if not VECTOR_STORE_ID:
    print(
        "ERROR: LITELLM_VECTOR_STORE_ID environment variable is required. "
        "Set it in your .env file or environment.",
        file=sys.stderr,
    )
    sys.exit(1)


# Enums
class ResponseFormat(str, Enum):
    """Output format for tool responses."""

    MARKDOWN = "markdown"
    JSON = "json"


# Pydantic Models for Input Validation
class VectorStoreSearchInput(BaseModel):
    """Input model for vector store search operations."""

    model_config = ConfigDict(
        str_strip_whitespace=True,  # Auto-strip whitespace from strings
        validate_assignment=True,  # Validate on assignment
        extra="forbid",  # Forbid extra fields
    )

    query: str = Field(
        ...,
        description=(
            "Natural language search query to find relevant code, documentation, "
            "or configuration files (e.g., 'How is Redis configured?', "
            "'GKE Terraform module implementation', 'semantic caching setup')"
        ),
        min_length=2,
        max_length=500,
    )

    max_results: int = Field(
        default=5,
        description="Maximum number of results to return (1-20)",
        ge=1,
        le=20,
    )

    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description=(
            "Output format: 'markdown' for human-readable formatted results, "
            "'json' for machine-readable structured data"
        ),
    )

    vector_store: Optional[str] = Field(
        default=None,
        description=(
            "Vector store to search. Can be:\n"
            "- A friendly name: 'panser-corpus', 'internal-corpus', 'mcp-servers-corpus'\n"
            "- A direct ID: '2341871806232657920'\n"
            "- Omit to use default from LITELLM_VECTOR_STORE_ID\n\n"
            "Use litellm_list_vector_stores tool to see all available stores.\n\n"
            "Examples:\n"
            "  - 'internal-corpus' (searches internal framework code)\n"
            "  - 'panser-corpus' (searches Panser framework)\n"
            "  - '2341871806232657920' (direct ID)\n"
            "  - null/omit (uses default)"
        ),
    )

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Validate and clean the search query."""
        if not v.strip():
            raise ValueError("Query cannot be empty or whitespace only")
        return v.strip()


# Shared utility functions
async def _list_vector_stores() -> List[Dict[str, Any]]:
    """Fetch list of all available vector stores from LiteLLM.

    Returns:
        List of vector store dictionaries with id, name, description, etc.

    Raises:
        httpx.HTTPStatusError: If the API request fails
        httpx.TimeoutException: If the request times out
    """
    url = f"{API_BASE_URL}/vector_store/list"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])


async def _resolve_vector_store_id(vector_store: Optional[str]) -> str:
    """Resolve a vector store name or ID to an actual ID.

    Args:
        vector_store: Vector store name, ID, or None for default

    Returns:
        Resolved vector store ID

    Raises:
        ValueError: If the named store is not found
    """
    # Use default if not specified
    if vector_store is None:
        return VECTOR_STORE_ID

    # Check if it looks like an ID (all digits)
    if vector_store.isdigit():
        return vector_store

    # Assume it's a name - fetch list and resolve
    try:
        stores = await _list_vector_stores()

        # Try to find by name
        for store in stores:
            if store.get("vector_store_name") == vector_store:
                return store["vector_store_id"]

        # Not found - provide helpful error
        available_names = [s.get("vector_store_name", "unknown") for s in stores]
        raise ValueError(
            f"Vector store '{vector_store}' not found. "
            f"Available stores: {', '.join(available_names)}. "
            f"Use litellm_list_vector_stores tool to see all options."
        )

    except httpx.HTTPError as e:
        # If listing fails, assume it's a direct ID and let the search fail with better error
        return vector_store


async def _make_vector_store_request(
    query: str, max_results: int, vector_store_id: str
) -> Dict[str, Any]:
    """Make an async request to the LiteLLM vector store search endpoint.

    Args:
        query: Search query string
        max_results: Maximum number of results to return
        vector_store_id: The vector store ID to search

    Returns:
        Dict containing search results or error information

    Raises:
        httpx.HTTPStatusError: If the API request fails
        httpx.TimeoutException: If the request times out
    """
    url = f"{API_BASE_URL}/v1/vector_stores/{vector_store_id}/search"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    request_body: Dict[str, Any] = {
        "query": query,
        "vector_store_id": vector_store_id,
        "custom_llm_provider": "vertex_ai",
    }

    # Add optional Vertex AI configuration if provided
    if VERTEX_AI_PROJECT:
        request_body["vertex_ai_project"] = VERTEX_AI_PROJECT
    if VERTEX_AI_LOCATION:
        request_body["vertex_ai_location"] = VERTEX_AI_LOCATION

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, headers=headers, json=request_body)
        response.raise_for_status()
        return response.json()


def _handle_api_error(e: Exception) -> str:
    """Provide clear, actionable error messages for API failures.

    Args:
        e: The exception that occurred

    Returns:
        Human-readable error message with guidance on how to proceed
    """
    if isinstance(e, httpx.HTTPStatusError):
        status_code = e.response.status_code
        if status_code == 404:
            return (
                "Error: Vector store not found. Please verify your LITELLM_VECTOR_STORE_ID "
                "is correct in the .env file."
            )
        elif status_code == 401 or status_code == 403:
            return (
                "Error: Authentication failed. Please check your LITELLM_API_KEY "
                "is valid and has access to the vector store."
            )
        elif status_code == 429:
            return (
                "Error: Rate limit exceeded. Please wait a moment before making "
                "another search request."
            )
        elif status_code == 500:
            return (
                "Error: Vector store service error. The LiteLLM server encountered "
                "an internal error. Please try again in a moment."
            )
        return f"Error: API request failed with status {status_code}. Please check your configuration."
    elif isinstance(e, httpx.TimeoutException):
        return (
            "Error: Request timed out after 30 seconds. The vector store search "
            "is taking too long. Try a more specific query or reduce max_results."
        )
    elif isinstance(e, httpx.ConnectError):
        return (
            f"Error: Unable to connect to {API_BASE_URL}. Please check your "
            "LITELLM_BASE_URL and network connection."
        )
    return f"Error: Unexpected error occurred: {type(e).__name__} - {str(e)}"


def _format_markdown_results(
    data: List[Dict[str, Any]], query: str, truncated: bool = False
) -> str:
    """Format search results as human-readable Markdown.

    Args:
        data: List of search result dictionaries
        query: The original search query
        truncated: Whether results were truncated due to character limit

    Returns:
        Markdown-formatted string
    """
    if not data:
        return f"No results found for query: '{query}'\n\nTry:\n- Using more specific keywords\n- Checking spelling\n- Using technical terms from your codebase"

    lines = [
        "# Vector Store Search Results",
        "",
        f"**Query:** {query}",
        f"**Results Found:** {len(data)}",
    ]

    if truncated:
        lines.append("")
        lines.append(
            "⚠️  **Results truncated** due to size limit. Use max_results parameter "
            "to control the number of results returned."
        )

    lines.append("")

    for idx, result in enumerate(data, 1):
        score = result.get("score", 0)
        filename = result.get("filename", "Unknown")
        file_id = result.get("file_id", "")

        # Extract text content
        content_items = result.get("content", [])
        text_content = ""
        for item in content_items:
            if item.get("type") == "text":
                text_content = item.get("text", "")
                break

        lines.append(f"## Result {idx}: {filename}")
        lines.append("")
        lines.append(f"- **Relevance Score:** {score:.4f}")
        lines.append(f"- **File Path:** `{file_id}`")
        lines.append("")
        lines.append("### Content:")
        lines.append("```")

        # Truncate individual content items to keep response manageable
        max_content_length = 2000
        if len(text_content) > max_content_length:
            lines.append(text_content[:max_content_length])
            lines.append(
                f"... (truncated, {len(text_content)} total characters)"
            )
        else:
            lines.append(text_content)

        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def _format_json_results(
    data: List[Dict[str, Any]], query: str, truncated: bool = False
) -> str:
    """Format search results as structured JSON.

    Args:
        data: List of search result dictionaries
        query: The original search query
        truncated: Whether results were truncated due to character limit

    Returns:
        JSON-formatted string
    """
    response = {
        "query": query,
        "total_results": len(data),
        "truncated": truncated,
        "results": [],
    }

    if truncated:
        response["truncation_message"] = (
            "Results were truncated to fit within character limits. "
            "Reduce max_results to get complete content for each result."
        )

    for result in data:
        # Extract text content
        content_items = result.get("content", [])
        text_content = ""
        for item in content_items:
            if item.get("type") == "text":
                text_content = item.get("text", "")
                break

        response["results"].append(
            {
                "score": result.get("score", 0),
                "filename": result.get("filename", "Unknown"),
                "file_id": result.get("file_id", ""),
                "content": text_content,
                "attributes": result.get("attributes", {}),
            }
        )

    return json.dumps(response, indent=2)


# Tool definitions
@mcp.tool(
    name="litellm_list_vector_stores",
    annotations={
        "title": "List Available Vector Stores",
        "readOnlyHint": True,  # Tool does not modify environment
        "destructiveHint": False,  # Tool does not perform destructive operations
        "idempotentHint": True,  # Repeated calls return same results
        "openWorldHint": True,  # Tool interacts with external LiteLLM service
    },
)
async def litellm_list_vector_stores(response_format: ResponseFormat = ResponseFormat.MARKDOWN) -> str:
    """List all available vector stores in the LiteLLM instance.

    This tool retrieves all configured vector stores from the LiteLLM server,
    showing their IDs, friendly names, descriptions, and metadata. Use this
    to discover which vector stores are available before searching.

    Args:
        response_format (ResponseFormat): Output format ('markdown' or 'json', default: 'markdown')

    Returns:
        str: List of vector stores in the requested format

        Markdown format (default):
            Human-readable list with names, IDs, and descriptions

        JSON format:
            {
                "total_count": int,
                "vector_stores": [
                    {
                        "id": str,
                        "name": str,
                        "description": str,
                        "provider": str,
                        "created_at": str,
                        "updated_at": str
                    }
                ]
            }

    Examples:
        Use when:
        - "What vector stores are available?" → Lists all stores
        - "Show me all code repositories" → Lists stores with descriptions
        - Before searching to know which store to use

        Don't use when:
        - You already know the vector store name/ID to search

    Error Handling:
        - Authentication failures (401/403): Check LITELLM_API_KEY
        - Connection errors: Check LITELLM_BASE_URL and network
        - Timeouts: Service may be overloaded, try again

    Performance Notes:
        - Supports pagination (default: 100 items per page)
        - Results are cached for efficiency
        - Typically returns in 1-2 seconds
    """
    try:
        # Fetch all vector stores
        stores = await _list_vector_stores()

        if not stores:
            if response_format == ResponseFormat.JSON:
                return json.dumps({
                    "total_count": 0,
                    "vector_stores": [],
                    "message": "No vector stores found. Your API key may not have access to any stores."
                }, indent=2)
            else:
                return "No vector stores found.\n\nPossible reasons:\n- Your API key doesn't have access to any vector stores\n- No vector stores are configured in LiteLLM"

        # Format response based on requested format
        if response_format == ResponseFormat.MARKDOWN:
            lines = [
                "# Available Vector Stores",
                "",
                f"**Total Stores:** {len(stores)}",
                "",
            ]

            for idx, store in enumerate(stores, 1):
                name = store.get("vector_store_name", "Unnamed")
                store_id = store.get("vector_store_id", "Unknown")
                description = store.get("vector_store_description", "No description")
                provider = store.get("custom_llm_provider", "Unknown")
                created = store.get("created_at", "Unknown")

                lines.append(f"## {idx}. {name}")
                lines.append("")
                lines.append(f"- **ID:** `{store_id}`")
                lines.append(f"- **Description:** {description}")
                lines.append(f"- **Provider:** {provider}")
                lines.append(f"- **Created:** {created}")
                lines.append("")
                lines.append(f"**Usage:** `vector_store=\"{name}\"` or `vector_store=\"{store_id}\"`")
                lines.append("")
                lines.append("---")
                lines.append("")

            return "\n".join(lines)

        else:
            # JSON format
            formatted_stores = []
            for store in stores:
                formatted_stores.append({
                    "id": store.get("vector_store_id"),
                    "name": store.get("vector_store_name"),
                    "description": store.get("vector_store_description"),
                    "provider": store.get("custom_llm_provider"),
                    "created_at": store.get("created_at"),
                    "updated_at": store.get("updated_at"),
                    "metadata": store.get("vector_store_metadata"),
                    "params": store.get("litellm_params"),
                })

            return json.dumps({
                "total_count": len(stores),
                "vector_stores": formatted_stores
            }, indent=2)

    except Exception as e:
        error_msg = _handle_api_error(e)
        if response_format == ResponseFormat.JSON:
            return json.dumps({"error": error_msg}, indent=2)
        return error_msg


@mcp.tool(
    name="litellm_search_vector_store",
    annotations={
        "title": "Search LiteLLM Vector Store",
        "readOnlyHint": True,  # Tool does not modify environment
        "destructiveHint": False,  # Tool does not perform destructive operations
        "idempotentHint": True,  # Repeated calls with same args have no additional effect
        "openWorldHint": True,  # Tool interacts with external LiteLLM service
    },
)
async def litellm_search_vector_store(params: VectorStoreSearchInput) -> str:
    """Search the LiteLLM vector store for relevant code, documentation, and configuration files.

    This tool performs semantic search across your indexed codebase using natural language
    queries. It returns file chunks ranked by relevance with full source information,
    enabling you to find implementations, understand system configurations, and locate
    specific code patterns.

    Args:
        params (VectorStoreSearchInput): Validated input parameters containing:
            - query (str): Natural language search query (2-500 chars)
                Examples: "Redis configuration", "GKE Terraform module", "IAP tunnel setup"
            - max_results (int): Number of results to return (1-20, default: 5)
            - response_format (ResponseFormat): Output format ('markdown' or 'json', default: 'markdown')
            - vector_store (Optional[str]): Vector store to search - can be name or ID (default: uses LITELLM_VECTOR_STORE_ID)
                Examples: "panser-corpus", "internal-corpus", "2341871806232657920"

    Returns:
        str: Search results in the requested format

        Markdown format (default):
            Human-readable results with file paths, relevance scores, and content snippets

        JSON format:
            {
                "query": str,           # The search query
                "total_results": int,   # Number of results returned
                "truncated": bool,      # Whether results were truncated
                "results": [
                    {
                        "score": float,      # Relevance score (0-1, higher = better)
                        "filename": str,     # Source filename
                        "file_id": str,      # Full GCS path
                        "content": str,      # File content chunk
                        "attributes": {...}  # Additional metadata
                    }
                ]
            }

    Examples:
        Use when:
        - "Find how Redis Stack is configured" → query="Redis Stack configuration"
        - "Show GKE module implementation" → query="GKE Terraform module"
        - "Locate semantic caching code" → query="semantic caching implementation"
        - "Search the panser-corpus for authentication code" → query="authentication", vector_store="panser-corpus"
        - "Search internal codebase for deployment scripts" → query="deployment scripts", vector_store="internal-corpus"

        Don't use when:
        - You have an exact file path (use file read tools instead)
        - You need to modify code (this tool is read-only)
        - You don't know which stores exist (use litellm_list_vector_stores first)

    Error Handling:
        - Input validation errors handled by Pydantic model
        - Returns actionable error messages for:
            * Authentication failures (401/403): Check LITELLM_API_KEY
            * Vector store not found (404): Check LITELLM_VECTOR_STORE_ID
            * Rate limiting (429): Wait before retrying
            * Timeouts: Reduce max_results or use more specific query
            * Connection errors: Check LITELLM_BASE_URL and network

    Performance Notes:
        - Results are ranked by semantic similarity (higher scores = more relevant)
        - Responses are limited to 25,000 characters total
        - Individual content snippets truncated at 2,000 characters
        - Reduce max_results if hitting character limits
    """
    try:
        # Resolve vector store name/ID to actual ID
        resolved_id = await _resolve_vector_store_id(params.vector_store)

        # Make API request using validated parameters
        data = await _make_vector_store_request(params.query, params.max_results, resolved_id)

        # Extract results from response
        results = data.get("data", [])

        if not results:
            if params.response_format == ResponseFormat.JSON:
                return json.dumps(
                    {
                        "query": params.query,
                        "total_results": 0,
                        "truncated": False,
                        "results": [],
                        "message": f"No results found for query: '{params.query}'",
                    },
                    indent=2,
                )
            else:
                return _format_markdown_results([], params.query)

        # Format response based on requested format
        if params.response_format == ResponseFormat.MARKDOWN:
            formatted_result = _format_markdown_results(results, params.query)
        else:
            formatted_result = _format_json_results(results, params.query)

        # Check character limit and truncate if needed
        if len(formatted_result) > CHARACTER_LIMIT:
            # Reduce results by half and try again
            truncated_results = results[: max(1, len(results) // 2)]

            if params.response_format == ResponseFormat.MARKDOWN:
                formatted_result = _format_markdown_results(
                    truncated_results, params.query, truncated=True
                )
            else:
                formatted_result = _format_json_results(
                    truncated_results, params.query, truncated=True
                )

        return formatted_result

    except Exception as e:
        error_msg = _handle_api_error(e)
        if params.response_format == ResponseFormat.JSON:
            return json.dumps({"error": error_msg}, indent=2)
        return error_msg


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
