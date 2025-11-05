#!/usr/bin/env python3
"""
Test script for multi-vector store functionality

This script demonstrates:
1. Listing all available vector stores
2. Searching by vector store name
3. Searching by vector store ID
4. Error handling for invalid stores
"""

import asyncio
import json
from server import (
    litellm_list_vector_stores,
    litellm_search_vector_store,
    VectorStoreSearchInput,
    ResponseFormat,
)


async def test_list_stores():
    """Test listing all available vector stores"""
    print("=" * 60)
    print("TEST 1: List All Vector Stores")
    print("=" * 60)

    # Test Markdown format
    print("\n📋 Markdown Format:")
    print("-" * 60)
    result_md = await litellm_list_vector_stores(ResponseFormat.MARKDOWN)
    print(result_md)

    # Test JSON format
    print("\n📊 JSON Format:")
    print("-" * 60)
    result_json = await litellm_list_vector_stores(ResponseFormat.JSON)
    data = json.loads(result_json)
    print(f"Total stores: {data['total_count']}")
    print("\nStores:")
    for store in data['vector_stores']:
        print(f"  - {store['name']} ({store['id']})")


async def test_search_by_name():
    """Test searching using vector store names"""
    print("\n" + "=" * 60)
    print("TEST 2: Search by Vector Store Name")
    print("=" * 60)

    test_cases = [
        ("internal-corpus", "Redis configuration"),
        ("panser-corpus", "authentication"),
        ("mcp-servers-corpus", "FastMCP"),
    ]

    for store_name, query in test_cases:
        print(f"\n🔍 Searching '{store_name}' for: '{query}'")
        print("-" * 60)

        params = VectorStoreSearchInput(
            query=query,
            max_results=2,
            response_format=ResponseFormat.MARKDOWN,
            vector_store=store_name,
        )

        result = await litellm_search_vector_store(params)

        # Show first 500 chars of result
        print(result[:500])
        if len(result) > 500:
            print(f"\n... (truncated, {len(result)} total chars)")
        print()


async def test_search_by_id():
    """Test searching using direct vector store IDs"""
    print("\n" + "=" * 60)
    print("TEST 3: Search by Vector Store ID")
    print("=" * 60)

    # Use a specific ID
    params = VectorStoreSearchInput(
        query="Terraform modules",
        max_results=3,
        response_format=ResponseFormat.JSON,
        vector_store="1111111111111111111",  # internal-corpus ID
    )

    print(f"\n🔍 Searching ID '1111111111111111111' for: 'Terraform modules'")
    print("-" * 60)

    result = await litellm_search_vector_store(params)
    data = json.loads(result)

    print(f"Query: {data['query']}")
    print(f"Total results: {data['total_results']}")
    print(f"Truncated: {data['truncated']}")
    print(f"\nTop result:")
    if data['results']:
        top = data['results'][0]
        print(f"  Filename: {top['filename']}")
        print(f"  Score: {top['score']}")
        print(f"  Content preview: {top['content'][:100]}...")


async def test_search_default():
    """Test searching without specifying vector store (uses default)"""
    print("\n" + "=" * 60)
    print("TEST 4: Search Default Vector Store")
    print("=" * 60)

    params = VectorStoreSearchInput(
        query="GKE cluster",
        max_results=2,
        response_format=ResponseFormat.MARKDOWN,
        # vector_store not specified - uses default from env
    )

    print(f"\n🔍 Searching default vector store for: 'GKE cluster'")
    print("-" * 60)

    result = await litellm_search_vector_store(params)
    print(result[:400])
    if len(result) > 400:
        print(f"\n... (truncated)")


async def test_invalid_store():
    """Test error handling for invalid vector store"""
    print("\n" + "=" * 60)
    print("TEST 5: Error Handling - Invalid Store Name")
    print("=" * 60)

    params = VectorStoreSearchInput(
        query="test query",
        vector_store="nonexistent-corpus",  # This doesn't exist
    )

    print(f"\n🔍 Searching 'nonexistent-corpus' (should fail)")
    print("-" * 60)

    try:
        result = await litellm_search_vector_store(params)
        print(result)
    except Exception as e:
        print(f"❌ Expected error occurred: {e}")


async def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "MULTI-VECTOR STORE TEST SUITE" + " " * 18 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    try:
        await test_list_stores()
        await test_search_by_name()
        await test_search_by_id()
        await test_search_default()
        await test_invalid_store()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 60)
        print("\nThe MCP server now supports:")
        print("  ✓ Listing all vector stores")
        print("  ✓ Searching by friendly name")
        print("  ✓ Searching by direct ID")
        print("  ✓ Default fallback to env var")
        print("  ✓ Helpful error messages")
        print("\nReady for Claude Code integration! 🚀")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
