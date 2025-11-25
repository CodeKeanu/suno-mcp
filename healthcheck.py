#!/usr/bin/env python3
"""Health check script for Suno MCP Server container.

This script verifies that:
1. Required environment variables are set
2. The Suno client can be initialized
3. Basic imports work correctly

Exit codes:
  0 - Healthy
  1 - Unhealthy
"""

import sys
import os


def check_health() -> bool:
    """
    Perform health check on the MCP server.

    Returns:
        True if healthy, False otherwise
    """
    try:
        # Check 1: Verify required environment variable is set
        api_key = os.getenv("SUNO_API_KEY")
        if not api_key:
            print("UNHEALTHY: SUNO_API_KEY environment variable not set", file=sys.stderr)
            return False

        # Check 2: Verify base URL is set (with default)
        base_url = os.getenv("SUNO_API_BASE_URL", "https://api.sunoapi.org")
        if not base_url:
            print("UNHEALTHY: SUNO_API_BASE_URL is empty", file=sys.stderr)
            return False

        # Check 3: Verify required modules can be imported
        try:
            from suno_client import SunoClient, SunoAPIError
            from mcp.server import Server
            import httpx
            import asyncio
        except ImportError as e:
            print(f"UNHEALTHY: Failed to import required module: {e}", file=sys.stderr)
            return False

        # Check 4: Verify SunoClient can be instantiated (without making API calls)
        try:
            # This just checks initialization, not actual API connectivity
            # We don't want to make real API calls in health checks
            client = SunoClient(api_key=api_key, base_url=base_url)
            # Note: We don't call close() as we're not using it async here
        except ValueError as e:
            print(f"UNHEALTHY: Failed to initialize SunoClient: {e}", file=sys.stderr)
            return False
        except Exception as e:
            print(f"UNHEALTHY: Unexpected error during initialization: {e}", file=sys.stderr)
            return False

        # All checks passed
        return True

    except Exception as e:
        print(f"UNHEALTHY: Unexpected error in health check: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    if check_health():
        print("HEALTHY: Suno MCP Server is ready")
        sys.exit(0)
    else:
        sys.exit(1)
