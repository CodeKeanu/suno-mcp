#!/usr/bin/env python3
"""Simple test script to verify Suno API client functionality."""

import asyncio
import json
from dotenv import load_dotenv
from suno_client import SunoClient, SunoAPIError
import httpx

# Load environment variables
load_dotenv()

# Monkey patch httpx to capture request/response
class RequestResponseCapture:
    """Capture HTTP requests and responses for debugging."""

    def __init__(self):
        self.last_request = None
        self.last_response = None

    def reset(self):
        self.last_request = None
        self.last_response = None

capture = RequestResponseCapture()


async def main():
    """Test the Suno API client."""
    print("=" * 50)
    print("Suno API Client Test")
    print("=" * 50)

    try:
        # Initialize client
        print("\n1. Initializing Suno client...")
        client = SunoClient()

        # Patch the client to capture requests/responses
        original_post = client.client.post
        original_get = client.client.get

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

        async def captured_get(*args, **kwargs):
            response = await original_get(*args, **kwargs)
            capture.last_request = {
                "method": "GET",
                "url": str(response.request.url),
                "headers": dict(response.request.headers)
            }
            capture.last_response = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": response.text
            }
            return response

        client.client.post = captured_post
        client.client.get = captured_get

        print("   ✓ Client initialized successfully")

        # Test getting credits
        print("\n2. Testing get_credits()...")
        credits = await client.get_credits()
        print("   ✓ Credits retrieved:")
        if isinstance(credits, dict) and "data" in credits:
            data = credits["data"]
            # API returns credits as a float value
            if isinstance(data, (int, float)):
                print(f"     - Remaining credits: {data}")
            elif isinstance(data, dict):
                print(f"     - Total: {data.get('total_credits', 'N/A')}")
                print(f"     - Used: {data.get('used_credits', 'N/A')}")
                print(f"     - Remaining: {data.get('remaining_credits', 'N/A')}")
            else:
                print(f"     - Credits: {data}")
        else:
            print(f"     Response: {credits}")

        # Test music generation with v5 model and callback_url
        print("\n3. Testing generate_music() with v5 model and callback_url...")
        print("   Testing: 'A Land Forgotten' - symphonic ballad")
        capture.reset()

        result = await client.generate_music(
            prompt="symphonic ballad with orchestral arrangements, emotional strings, and epic crescendos",
            title="A Land Forgotten",
            model_version="V5",
            wait_audio=False,
            callback_url="https://example.com/webhook/test"
        )

        # Display captured request
        print("\n   === API REQUEST ===")
        if capture.last_request:
            print(f"   Method: {capture.last_request['method']}")
            print(f"   URL: {capture.last_request['url']}")
            if capture.last_request.get('body'):
                try:
                    body = json.loads(capture.last_request['body'])
                    print("   Request Body:")
                    for key, value in body.items():
                        print(f"     {key}: {value}")

                    # Validate request has correct fields
                    print("\n   Request Validation:")
                    if 'callBackUrl' in body:
                        print(f"     ✓ callBackUrl present: {body['callBackUrl']}")
                    else:
                        print(f"     ✗ callBackUrl MISSING (found: {list(body.keys())})")

                    if body.get('model') == 'V5':
                        print(f"     ✓ Model version V5 set correctly")
                    else:
                        print(f"     ✗ Model version incorrect: {body.get('model')}")

                    if body.get('title') == 'A Land Forgotten':
                        print(f"     ✓ Title set correctly")
                    else:
                        print(f"     ✗ Title incorrect: {body.get('title')}")

                except json.JSONDecodeError:
                    print(f"   Body (raw): {capture.last_request['body']}")

        # Display captured response
        print("\n   === API RESPONSE ===")
        if capture.last_response:
            print(f"   Status Code: {capture.last_response['status_code']}")
            try:
                response_body = json.loads(capture.last_response['body'])
                print("   Response Body:")
                print(f"     {json.dumps(response_body, indent=6)}")

                # Validate response
                print("\n   Response Validation:")
                if response_body.get('code') == 200:
                    print(f"     ✓ Success response (code 200)")
                elif response_body.get('code') == 400:
                    print(f"     ✗ Bad request (code 400): {response_body.get('msg')}")
                else:
                    print(f"     ? Unknown response code: {response_body.get('code')}")

            except json.JSONDecodeError:
                print(f"   Body (raw): {capture.last_response['body']}")

        print("\n   ✓ Music generation request completed")
        if "data" in result and result["data"] is not None:
            data = result["data"]
            if isinstance(data, dict) and "taskId" in data:
                task_id = data["taskId"]
                print(f"     - Task ID: {task_id}")
            elif isinstance(data, list):
                print(f"     - Generated {len(data)} track(s)")
                track_ids = [track.get("id") for track in data if isinstance(track, dict) and track.get("id")]
                print(f"     - Track IDs: {track_ids}")
            else:
                print(f"     - Data: {data}")
        else:
            print(f"     Response: {result}")

        # Close client
        await client.close()
        print("\n" + "=" * 50)
        print("All tests completed successfully!")
        print("=" * 50)

    except SunoAPIError as e:
        print(f"\n✗ Suno API Error: {e}")
        return 1
    except ValueError as e:
        print(f"\n✗ Configuration Error: {e}")
        print("\nPlease ensure:")
        print("  1. You have created a .env file (copy from .env.example)")
        print("  2. Your SUNO_API_KEY is set in the .env file")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
