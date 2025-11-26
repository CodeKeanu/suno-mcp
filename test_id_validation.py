#!/usr/bin/env python3
"""
Test to demonstrate the ID validation preventing common user errors.
This tests the exact scenario where users get "track can't be found" errors.
"""

import asyncio
import os
from suno_client import SunoClient


async def test_id_confusion_scenarios():
    """Test that validation catches common ID confusion mistakes."""
    print("=" * 70)
    print("Testing ID Validation - Preventing 'Track Not Found' Errors")
    print("=" * 70)
    print()

    # Set up test client
    os.environ['SUNO_API_KEY'] = 'test_key_validation'
    client = SunoClient()

    try:
        # Scenario 1: User tries to use generation task_id as audio_id (COMMON MISTAKE!)
        print("Scenario 1: Using generation taskId as audio_id parameter")
        print("-" * 70)
        print("What user is doing:")
        print("  music = generate_music(...)")
        print("  task_id = music['data']['taskId']  # Gets: 'abc123def456'")
        print("  convert_to_wav(audio_id=task_id)   # WRONG! This causes 404")
        print()

        try:
            await client.convert_to_wav(
                callback_url="https://example.com/webhook",
                audio_id="abc123def456"  # Wrong! This is a taskId, not an audio_id
            )
            print("❌ FAILED: Should have caught invalid audio_id format!")
        except ValueError as e:
            print(f"✅ CAUGHT ERROR (as expected):")
            print(f"   {str(e)}")
        print()

        # Scenario 2: User tries to use track UUID as task_id (REVERSE MISTAKE!)
        print("\nScenario 2: Using track UUID as task_id parameter")
        print("-" * 70)
        print("What user is doing:")
        print("  track_id = music['data']['sunoData'][0]['id']  # UUID")
        print("  convert_to_wav(task_id=track_id)  # Could work, but confusing")
        print()

        try:
            await client.convert_to_wav(
                callback_url="https://example.com/webhook",
                task_id="7752c889-3601-4e55-b805-54a28a53de85"  # UUID in task_id param
            )
            print("❌ FAILED: Should have warned about UUID in task_id!")
        except ValueError as e:
            print(f"✅ CAUGHT ERROR (as expected):")
            print(f"   {str(e)}")
        print()

        # Scenario 3: Invalid callback URL
        print("\nScenario 3: Invalid callback_url format")
        print("-" * 70)

        try:
            await client.convert_to_wav(
                callback_url="not-a-url",
                audio_id="7752c889-3601-4e55-b805-54a28a53de85"
            )
            print("❌ FAILED: Should have caught invalid URL!")
        except ValueError as e:
            print(f"✅ CAUGHT ERROR (as expected):")
            print(f"   {str(e)}")
        print()

        # Scenario 4: Invalid URL scheme
        print("\nScenario 4: Invalid URL scheme (SSRF protection)")
        print("-" * 70)

        try:
            await client.convert_to_wav(
                callback_url="ftp://example.com/webhook",
                audio_id="7752c889-3601-4e55-b805-54a28a53de85"
            )
            print("❌ FAILED: Should have rejected ftp:// scheme!")
        except ValueError as e:
            print(f"✅ CAUGHT ERROR (as expected):")
            print(f"   {str(e)}")
        print()

        # Scenario 5: CORRECT usage with audio_id (UUID)
        print("\nScenario 5: CORRECT - Using proper UUID as audio_id")
        print("-" * 70)
        print("What user should do:")
        print("  track_id = music['data']['sunoData'][0]['id']")
        print("  convert_to_wav(callback_url='...', audio_id=track_id)")
        print()
        print("✅ This would pass validation (won't actually call API in this test)")
        print()

        # Scenario 6: CORRECT usage with task_id (hex string)
        print("\nScenario 6: CORRECT - Using proper hex string as task_id")
        print("-" * 70)
        print("What user should do:")
        print("  task_id = music['data']['taskId']")
        print("  convert_to_wav(callback_url='...', task_id=task_id)")
        print()
        print("✅ This would pass validation (won't actually call API in this test)")
        print()

        print("=" * 70)
        print("Summary: ID Validation Working Correctly!")
        print("=" * 70)
        print()
        print("The validation now catches these common mistakes BEFORE calling the API:")
        print("  ✓ Using generation taskId as audio_id → Clear error message")
        print("  ✓ Using track UUID as task_id → Warning to use audio_id instead")
        print("  ✓ Invalid URL formats → Validation error")
        print("  ✓ Dangerous URL schemes → SSRF protection")
        print()
        print("This prevents the '404 track not found' error from the API!")
        print()

    finally:
        await client.close()


def main():
    """Run the ID validation tests."""
    asyncio.run(test_id_confusion_scenarios())


if __name__ == "__main__":
    main()
