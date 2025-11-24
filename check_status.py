#!/usr/bin/env python3
"""Check status of generated songs."""

import asyncio
import json
import sys
from dotenv import load_dotenv
from suno_client import SunoClient, SunoAPIError

# Load environment variables
load_dotenv()


async def check_status(task_id: str):
    """Check status of a song generation task."""
    try:
        client = SunoClient()
        print(f"Checking status for task: {task_id}\n")

        result = await client.get_task_status(task_id)

        print("=" * 60)
        print("TASK INFORMATION")
        print("=" * 60)

        if result.get("code") == 200 and "data" in result:
            data = result["data"]

            print(f"Task ID: {data.get('taskId', 'N/A')}")
            print(f"Status: {data.get('status', 'N/A')}")
            print(f"Operation Type: {data.get('operationType', 'N/A')}")
            print(f"Type: {data.get('type', 'N/A')}")

            # Check if response contains track data
            response = data.get('response', {})
            suno_data = response.get('sunoData', [])

            if not suno_data:
                print("\nNo track data available yet. Generation may still be in progress.")
                print(f"Current status: {data.get('status', 'UNKNOWN')}")
            else:
                print(f"\n{len(suno_data)} track(s) generated:")

                for i, track in enumerate(suno_data, 1):
                    print(f"\n{'='*60}")
                    print(f"Track {i}:")
                    print(f"  ID: {track.get('id', 'N/A')}")
                    print(f"  Title: {track.get('title', 'N/A')}")
                    print(f"  Model: {track.get('modelName', 'N/A')}")

                    if track.get('duration'):
                        print(f"  Duration: {track['duration']}s")

                    if track.get('tags'):
                        print(f"  Tags: {track['tags']}")

                    if track.get('audioUrl'):
                        print(f"\n  🎵 Audio URL: {track['audioUrl']}")
                    else:
                        print(f"\n  🎵 Audio: Not ready yet")

                    if track.get('streamAudioUrl'):
                        print(f"  🎵 Stream URL: {track['streamAudioUrl']}")

                    if track.get('imageUrl'):
                        print(f"  🖼️  Image URL: {track['imageUrl']}")

                    if track.get('createTime'):
                        print(f"\n  Created: {track['createTime']}")

                    # Show prompt if available
                    if track.get('prompt'):
                        print(f"\n  Lyrics/Prompt:")
                        prompt_lines = track['prompt'].split('\n')
                        for line in prompt_lines[:5]:  # Show first 5 lines
                            print(f"    {line}")
                        if len(prompt_lines) > 5:
                            print(f"    ... ({len(prompt_lines) - 5} more lines)")
        else:
            print(f"Response: {json.dumps(result, indent=2)}")

        await client.close()

    except SunoAPIError as e:
        print(f"✗ Suno API Error: {e}")
        return 1
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_status.py <task_id>")
        sys.exit(1)

    task_id = sys.argv[1]
    exit_code = asyncio.run(check_status(task_id))
    exit(exit_code)
