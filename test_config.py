#!/usr/bin/env python3
"""
Test configuration and verify vector store access

Run this script to verify your .env configuration is correct.
"""

import os
import sys

import requests
from dotenv import load_dotenv


def test_configuration():
    """Test that all required configuration is present and valid"""
    print("=" * 60)
    print("LiteLLM Vector Store MCP - Configuration Test")
    print("=" * 60)

    # Load .env file
    load_dotenv()
    print("\n✓ Loaded .env file")

    # Check required variables
    base_url = os.getenv("LITELLM_BASE_URL", "https://litellm.psolabs.com")
    api_key = os.getenv("LITELLM_API_KEY")
    vector_store_id = os.getenv("LITELLM_VECTOR_STORE_ID")
    vertex_ai_project = os.getenv("VERTEX_AI_PROJECT")
    vertex_ai_location = os.getenv("VERTEX_AI_LOCATION", "us-east4")

    print("\nConfiguration:")
    print(f"  LITELLM_BASE_URL: {base_url}")
    print(f"  LITELLM_API_KEY: {'✓ Set' if api_key else '✗ NOT SET'}")
    print(f"  LITELLM_VECTOR_STORE_ID: {vector_store_id if vector_store_id else '✗ NOT SET'}")
    print(f"  VERTEX_AI_PROJECT: {vertex_ai_project if vertex_ai_project else '(not set)'}")
    print(f"  VERTEX_AI_LOCATION: {vertex_ai_location}")

    if not api_key:
        print("\n✗ ERROR: LITELLM_API_KEY is required")
        return False

    if not vector_store_id:
        print("\n✗ ERROR: LITELLM_VECTOR_STORE_ID is required")
        return False

    # Test vector store access
    print("\n" + "=" * 60)
    print("Testing Vector Store Access...")
    print("=" * 60)

    url = f"{base_url}/v1/vector_stores/{vector_store_id}/search"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    request_body = {
        "query": "test query",
        "vector_store_id": vector_store_id,
        "custom_llm_provider": "vertex_ai",
    }

    if vertex_ai_project:
        request_body["vertex_ai_project"] = vertex_ai_project
    if vertex_ai_location:
        request_body["vertex_ai_location"] = vertex_ai_location

    try:
        print(f"\nSearching: {url}")
        response = requests.post(url, headers=headers, json=request_body, timeout=30)

        if response.status_code == 200:
            data = response.json()
            num_results = len(data.get("data", []))
            print(f"\n✓ SUCCESS! Vector store is accessible")
            print(f"  Found {num_results} results for test query")
            return True
        elif response.status_code == 401:
            print(f"\n✗ Authentication failed (401)")
            print(f"  Check your LITELLM_API_KEY")
            return False
        elif response.status_code == 404:
            print(f"\n✗ Vector store not found (404)")
            print(f"  Check your LITELLM_VECTOR_STORE_ID")
            return False
        else:
            print(f"\n✗ Request failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print(f"\n✗ Request timed out")
        print(f"  Check your network connection and LITELLM_BASE_URL")
        return False
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


def main():
    success = test_configuration()

    print("\n" + "=" * 60)
    if success:
        print("✓ Configuration is valid!")
        print("\nYou can now use the MCP server with Claude.")
        print("\nNext steps:")
        print("  1. Add this server to your Claude Desktop config")
        print("  2. Restart Claude Desktop")
        print("  3. Ask Claude to search your vector store")
        sys.exit(0)
    else:
        print("✗ Configuration has errors")
        print("\nPlease fix the errors above and try again.")
        print("\nSee README.md for configuration help.")
        sys.exit(1)


if __name__ == "__main__":
    main()
