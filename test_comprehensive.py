#!/usr/bin/env python3
"""Comprehensive test for all Suno API parameters."""

import asyncio
import json
from dotenv import load_dotenv
from suno_client import SunoClient, SunoAPIError

# Load environment variables
load_dotenv()


class RequestResponseCapture:
    """Capture HTTP requests and responses for debugging."""

    def __init__(self):
        self.last_request = None
        self.last_response = None

    def reset(self):
        self.last_request = None
        self.last_response = None


capture = RequestResponseCapture()


async def test_non_custom_mode():
    """Test non-custom mode with basic prompt."""
    print("\n" + "=" * 70)
    print("TEST 1: Non-Custom Mode (Auto-generated lyrics)")
    print("=" * 70)

    client = SunoClient()
    setup_capture(client)
    capture.reset()

    result = await client.generate_music(
        prompt="A peaceful ambient soundscape with soft synths and gentle melodies",
        model_version="V3_5",
        wait_audio=False,
        callback_url="https://example.com/webhook"
    )

    print_request_response("Non-Custom Mode")
    validate_response(result, "Non-custom mode")
    await client.close()


async def test_custom_mode_with_lyrics():
    """Test custom mode with custom lyrics."""
    print("\n" + "=" * 70)
    print("TEST 2: Custom Mode with Custom Lyrics")
    print("=" * 70)

    client = SunoClient()
    setup_capture(client)
    capture.reset()

    custom_lyrics = """[Verse]
In a land forgotten by time
Where shadows dance and stars align
A hero rises from the dust
To fight for freedom, fight for us

[Chorus]
Oh, the land forgotten
Where dreams are born and never rotten
In the echoes of the past
We'll find a hope that's meant to last

[Verse 2]
Through the valleys dark and deep
Where ancient secrets lie asleep
A melody of hope rings clear
To guide us through our darkest fear

[Chorus]
Oh, the land forgotten
Where dreams are born and never rotten
In the echoes of the past
We'll find a hope that's meant to last"""

    result = await client.generate_music(
        prompt=custom_lyrics,
        custom_mode=True,
        style="orchestral epic, cinematic, powerful strings, emotional vocals",
        title="A Land Forgotten",
        model_version="V5",
        wait_audio=False,
        callback_url="https://example.com/webhook"
    )

    print_request_response("Custom Mode with Lyrics")
    validate_response(result, "Custom mode with lyrics")
    await client.close()


async def test_instrumental_custom_mode():
    """Test custom mode instrumental (no lyrics needed)."""
    print("\n" + "=" * 70)
    print("TEST 3: Custom Mode Instrumental (No Lyrics)")
    print("=" * 70)

    client = SunoClient()
    setup_capture(client)
    capture.reset()

    result = await client.generate_music(
        custom_mode=True,
        make_instrumental=True,
        style="classical piano, melancholic, slow tempo, emotional",
        title="Moonlight Reflection",
        model_version="V4_5",
        wait_audio=False,
        callback_url="https://example.com/webhook"
    )

    print_request_response("Custom Instrumental")
    validate_response(result, "Custom instrumental")
    await client.close()


async def test_advanced_parameters():
    """Test with all advanced parameters."""
    print("\n" + "=" * 70)
    print("TEST 4: Advanced Parameters (style_weight, vocal_gender, etc.)")
    print("=" * 70)

    client = SunoClient()
    setup_capture(client)
    capture.reset()

    result = await client.generate_music(
        prompt="upbeat pop song about summer adventures",
        custom_mode=False,
        model_version="V5",
        vocal_gender="f",
        style_weight=0.8,
        weirdness_constraint=0.3,
        negative_tags="aggressive, metal, dark",
        wait_audio=False,
        callback_url="https://example.com/webhook"
    )

    print_request_response("Advanced Parameters")
    validate_response(result, "Advanced parameters")
    await client.close()


async def test_multiple_models():
    """Test different model versions."""
    print("\n" + "=" * 70)
    print("TEST 5: Multiple Model Versions")
    print("=" * 70)

    models = ["V3_5", "V4", "V4_5", "V4_5PLUS", "V5"]

    for model in models:
        print(f"\n  Testing model: {model}")
        client = SunoClient()
        setup_capture(client)
        capture.reset()

        result = await client.generate_music(
            prompt="short test melody",
            model_version=model,
            wait_audio=False,
            callback_url="https://example.com/webhook"
        )

        if result.get("code") == 200:
            print(f"    ✓ {model} succeeded")
        else:
            print(f"    ✗ {model} failed: {result.get('msg')}")

        await client.close()


def setup_capture(client):
    """Setup request/response capture for a client."""
    original_post = client.client.post

    async def captured_post(*args, **kwargs):
        response = await original_post(*args, **kwargs)
        capture.last_request = {
            "method": "POST",
            "url": str(response.request.url),
            "headers": dict(response.request.headers),
            "body": response.request.content.decode() if response.request.content else None
        }
        capture.last_response = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": response.text
        }
        return response

    client.client.post = captured_post


def print_request_response(test_name):
    """Print captured request and response."""
    print(f"\n  === API REQUEST ({test_name}) ===")
    if capture.last_request and capture.last_request.get('body'):
        try:
            body = json.loads(capture.last_request['body'])
            print("  Request Body:")
            for key, value in body.items():
                if key == "prompt" and len(str(value)) > 100:
                    print(f"    {key}: {str(value)[:100]}... ({len(str(value))} chars)")
                else:
                    print(f"    {key}: {value}")
        except json.JSONDecodeError:
            print(f"  Body (raw): {capture.last_request['body']}")

    print(f"\n  === API RESPONSE ({test_name}) ===")
    if capture.last_response:
        print(f"  Status Code: {capture.last_response['status_code']}")
        try:
            response_body = json.loads(capture.last_response['body'])
            print(f"  Response: {json.dumps(response_body, indent=4)}")
        except json.JSONDecodeError:
            print(f"  Body (raw): {capture.last_response['body']}")


def validate_response(result, test_name):
    """Validate API response."""
    print(f"\n  === VALIDATION ({test_name}) ===")
    if result.get('code') == 200:
        print(f"  ✓ Success response (code 200)")
        if result.get('data'):
            task_id = result['data'].get('taskId')
            if task_id:
                print(f"  ✓ Task ID: {task_id}")
    elif result.get('code') == 400:
        print(f"  ✗ Bad request (code 400): {result.get('msg')}")
    else:
        print(f"  ? Unknown response: {result}")


async def main():
    """Run all comprehensive tests."""
    print("=" * 70)
    print("SUNO API COMPREHENSIVE PARAMETER TESTS")
    print("=" * 70)
    print("\nTesting all available parameters and modes...")

    try:
        # Run all tests
        await test_non_custom_mode()
        await test_custom_mode_with_lyrics()
        await test_instrumental_custom_mode()
        await test_advanced_parameters()
        await test_multiple_models()

        print("\n" + "=" * 70)
        print("ALL COMPREHENSIVE TESTS COMPLETED!")
        print("=" * 70)
        return 0

    except SunoAPIError as e:
        print(f"\n✗ Suno API Error: {e}")
        return 1
    except ValueError as e:
        print(f"\n✗ Configuration Error: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
