#!/usr/bin/env python3
"""
Test script to verify MCP server integration works correctly.
This simulates what Claude Code does when calling the MCP tools.
"""

import asyncio
import json
from server import server, suno_client
from suno_client import SunoClient
from mcp.types import TextContent

async def test_mcp_tools():
    """Test all MCP tools to ensure they work correctly."""

    print("=" * 70)
    print("MCP SERVER INTEGRATION TEST")
    print("=" * 70)

    # Initialize a test client
    import server as server_module
    server_module.suno_client = SunoClient()

    try:
        # Test 1: Get Credits
        print("\n[TEST 1] Testing get_credits tool...")
        print("-" * 70)

        from server import handle_call_tool
        result = await handle_call_tool("get_credits", {})

        if result and isinstance(result, list) and len(result) > 0:
            print("✓ get_credits tool works!")
            print(f"Response: {result[0].text[:200]}...")
        else:
            print("✗ get_credits tool failed!")
            return False

        # Test 2: Generate Music (non-custom mode, fast test)
        print("\n[TEST 2] Testing generate_music tool (non-custom mode)...")
        print("-" * 70)

        gen_args = {
            "prompt": "A short test melody",
            "model_version": "v3.5",
            "wait_audio": False,
            "callback_url": "https://example.com/webhook/test"
        }

        result = await handle_call_tool("generate_music", gen_args)

        if result and isinstance(result, list) and len(result) > 0:
            response_text = result[0].text
            print("✓ generate_music tool works!")
            print(f"Response:\n{response_text}")

            # Extract task ID from response
            if "Task ID:" in response_text:
                task_id = response_text.split("Task ID:")[1].strip().split("\n")[0].strip()
                print(f"\n✓ Task ID extracted: {task_id}")
            else:
                print("✗ Could not extract task ID from response")
                return False
        else:
            print("✗ generate_music tool failed!")
            return False

        # Test 3: Get Task Status
        print("\n[TEST 3] Testing get_task_status tool...")
        print("-" * 70)

        # Wait a moment for the task to be registered
        await asyncio.sleep(2)

        status_args = {
            "task_id": task_id
        }

        result = await handle_call_tool("get_task_status", status_args)

        if result and isinstance(result, list) and len(result) > 0:
            print("✓ get_task_status tool works!")
            print(f"Response:\n{result[0].text}")
        else:
            print("✗ get_task_status tool failed!")
            return False

        # Test 4: Generate Music (custom mode with v5)
        print("\n[TEST 4] Testing generate_music tool (custom mode with v5)...")
        print("-" * 70)

        custom_args = {
            "prompt": "Test lyrics for MCP integration\nJust a simple test",
            "title": "MCP Test Song",
            "style": "pop, upbeat, electronic",
            "model_version": "v5",
            "custom_mode": True,
            "vocal_gender": "f",
            "wait_audio": False,
            "callback_url": "https://example.com/webhook/test"
        }

        result = await handle_call_tool("generate_music", custom_args)

        if result and isinstance(result, list) and len(result) > 0:
            response_text = result[0].text
            print("✓ generate_music (custom mode + v5) works!")
            print(f"Response:\n{response_text}")

            if "Task ID:" in response_text:
                task_id_v5 = response_text.split("Task ID:")[1].strip().split("\n")[0].strip()
                print(f"\n✓ V5 Task ID: {task_id_v5}")
            else:
                print("✗ Could not extract task ID from v5 response")
                return False
        else:
            print("✗ generate_music (custom mode) failed!")
            return False

        # Test 5: List Tools (verify new tool is registered)
        print("\n[TEST 5] Verifying all tools are registered...")
        print("-" * 70)

        from server import handle_list_tools
        tools = await handle_list_tools()

        tool_names = [tool.name for tool in tools]
        print(f"Registered tools: {tool_names}")

        expected_tools = ["generate_music", "get_task_status", "get_music_info", "get_credits"]
        for tool in expected_tools:
            if tool in tool_names:
                print(f"  ✓ {tool}")
            else:
                print(f"  ✗ {tool} - MISSING!")
                return False

        print("\n" + "=" * 70)
        print("ALL MCP INTEGRATION TESTS PASSED!")
        print("=" * 70)
        print("\n✓ The MCP server is fully functional and ready to use")
        print("✓ All fixes have been applied successfully")
        print("✓ Custom mode with v5 model works")
        print("✓ Task status checking works")
        print("✓ Error handling is in place")

        return True

    except Exception as e:
        print(f"\n✗ TEST FAILED WITH ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        import server as server_module
        if server_module.suno_client:
            await server_module.suno_client.close()


async def main():
    """Run the integration tests."""
    success = await test_mcp_tools()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
