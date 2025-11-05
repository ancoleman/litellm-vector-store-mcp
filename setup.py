from setuptools import setup, find_packages

setup(
    name="litellm-vector-store-mcp",
    version="0.1.0",
    description="MCP server for searching LiteLLM vector stores",
    author="Your Name",
    author_email="your.email@example.com",
    py_modules=["server"],
    install_requires=[
        "mcp>=1.0.0",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
    ],
    entry_points={
        "console_scripts": [
            "litellm-vector-store-mcp=server:main",
        ],
    },
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
