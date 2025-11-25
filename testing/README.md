# Testing

This directory contains all test files for the Suno MCP Server project.

## Directory Structure

```
testing/
├── integration/      # Integration tests (require API key and credits)
│   ├── test_client.py           # Basic Suno API client tests
│   ├── test_comprehensive.py    # Comprehensive API feature tests
│   └── test_mcp_integration.py  # MCP protocol integration tests
└── unit/             # Unit tests (future)
```

## Integration Tests

Integration tests require:
- Valid `SUNO_API_KEY` in `.env` file
- Sufficient API credits (each test consumes ~6 credits)
- Internet connectivity to reach Suno API

### Running Integration Tests

```bash
# Run all integration tests
python testing/integration/test_client.py
python testing/integration/test_comprehensive.py
python testing/integration/test_mcp_integration.py

# Or run from the project root
cd /root/suno-mcp-proj
python testing/integration/test_client.py
```

## Unit Tests

Currently empty - future unit tests will go here. Unit tests should:
- Not require API keys or network access
- Mock external dependencies
- Test individual functions and classes in isolation
- Run quickly and reliably

## Docker Tests

Docker-specific tests are in `/root/suno-mcp-proj/test_docker.sh` (kept at root for convenience).
