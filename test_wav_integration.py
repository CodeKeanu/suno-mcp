#!/usr/bin/env python3
"""
Integration test for WAV conversion feature.
Requires valid SUNO_API_KEY and API credits.

Usage:
    python3 test_wav_integration.py
"""

import asyncio
import os
import sys
from suno_client import SunoClient, SunoAPIError


async def test_wav_conversion_workflow():
    """Test complete workflow: generate music -> convert to WAV -> check status."""

    # Check API key
    api_key = os.getenv("SUNO_API_KEY")
    if not api_key:
        print("ERROR: SUNO_API_KEY not found in environment")
        print("Set it with: export SUNO_API_KEY='your-key-here'")
        return False

    print("=" * 70)
    print("WAV Conversion Integration Test")
    print("=" * 70)
    print()
    print("This test will:")
    print("1. Check API credits")
    print("2. Generate a short test track")
    print("3. Convert the track to WAV format")
    print("4. Check conversion status")
    print()
    print("WARNING: This will consume API credits!")
    print()

    # Ask for confirmation
    response = input("Continue with integration test? (y/N): ").strip().lower()
    if response != 'y':
        print("Test cancelled.")
        return False

    client = SunoClient()

    try:
        # Step 1: Check credits
        print("\n" + "-" * 70)
        print("Step 1: Checking API Credits")
        print("-" * 70)

        try:
            credits_result = await client.get_credits()
            credits = credits_result.get('data', 0)
            print(f"✓ Remaining credits: {credits}")

            if isinstance(credits, (int, float)) and credits < 5:
                print("WARNING: Low credits. Test may fail.")
        except SunoAPIError as e:
            print(f"✗ Failed to get credits: {e}")
            return False

        # Step 2: Generate music
        print("\n" + "-" * 70)
        print("Step 2: Generating Test Track")
        print("-" * 70)
        print("Generating short test track (this may take 30-60 seconds)...")

        try:
            music_result = await client.generate_music(
                prompt="Short upbeat test jingle",
                make_instrumental=True,
                model_version="V5",
                wait_audio=True
            )

            if not music_result.get('data') or not isinstance(music_result['data'], list):
                print(f"✗ Unexpected response format: {music_result}")
                return False

            track = music_result['data'][0]
            track_id = track.get('id')
            track_title = track.get('title', 'Unknown')

            if not track_id:
                print(f"✗ No track ID in response: {music_result}")
                return False

            print(f"✓ Generated track: {track_title}")
            print(f"  Track ID: {track_id}")
            print(f"  Status: {track.get('status', 'Unknown')}")

            if track.get('audio_url'):
                print(f"  Audio URL: {track['audio_url']}")

        except SunoAPIError as e:
            print(f"✗ Failed to generate music: {e}")
            return False

        # Step 3: Convert to WAV
        print("\n" + "-" * 70)
        print("Step 3: Converting to WAV")
        print("-" * 70)
        print(f"Converting track {track_id} to WAV format...")

        try:
            wav_result = await client.convert_to_wav(
                audio_id=track_id,
                callback_url="https://example.com/webhook"
            )

            if not wav_result.get('data') or not isinstance(wav_result['data'], dict):
                print(f"✗ Unexpected response format: {wav_result}")
                return False

            task_id = wav_result['data'].get('taskId')

            if not task_id:
                print(f"✗ No task ID in response: {wav_result}")
                return False

            print(f"✓ Conversion started")
            print(f"  Task ID: {task_id}")

        except SunoAPIError as e:
            print(f"✗ Failed to start conversion: {e}")
            return False

        # Step 4: Check conversion status
        print("\n" + "-" * 70)
        print("Step 4: Checking Conversion Status")
        print("-" * 70)
        print("Polling for conversion completion (max 60 seconds)...")

        max_attempts = 20
        poll_interval = 3

        for attempt in range(1, max_attempts + 1):
            try:
                status_result = await client.get_wav_conversion_status(task_id)

                if not status_result.get('data'):
                    print(f"  Attempt {attempt}: No data in response")
                    await asyncio.sleep(poll_interval)
                    continue

                status_data = status_result['data']
                current_status = status_data.get('status', 'UNKNOWN')

                print(f"  Attempt {attempt}/{max_attempts}: {current_status}")

                if current_status == 'COMPLETED':
                    response_data = status_data.get('response', {})
                    wav_data = response_data.get('wavData', {})
                    wav_url = wav_data.get('wavUrl')

                    print(f"\n✓ Conversion completed!")
                    print(f"  Task ID: {status_data.get('taskId')}")
                    print(f"  Audio ID: {wav_data.get('audioId')}")
                    print(f"  WAV URL: {wav_url}")
                    print(f"  Created: {wav_data.get('createTime', 'Unknown')}")

                    return True

                elif current_status == 'FAILED':
                    print(f"\n✗ Conversion failed!")
                    print(f"  Response: {status_result}")
                    return False

                # Still processing, wait before next check
                if attempt < max_attempts:
                    await asyncio.sleep(poll_interval)

            except SunoAPIError as e:
                print(f"  Attempt {attempt}: Error checking status: {e}")
                if attempt < max_attempts:
                    await asyncio.sleep(poll_interval)

        print(f"\n⚠ Timeout after {max_attempts * poll_interval} seconds")
        print("The conversion may still be processing. Check status later with:")
        print(f"  Task ID: {task_id}")
        return False

    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        await client.close()


def main():
    """Run the integration test."""
    try:
        result = asyncio.run(test_wav_conversion_workflow())

        print("\n" + "=" * 70)
        if result:
            print("✓ WAV CONVERSION INTEGRATION TEST PASSED")
            print("=" * 70)
            print("\nThe WAV conversion feature is working correctly with the Suno API!")
            return 0
        else:
            print("✗ WAV CONVERSION INTEGRATION TEST FAILED")
            print("=" * 70)
            print("\nCheck the error messages above for details.")
            return 1

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        return 1
    except Exception as e:
        print(f"\n\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
