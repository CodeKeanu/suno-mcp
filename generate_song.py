#!/usr/bin/env python3
"""Direct song generation script - bypasses MCP server."""

import asyncio
import json
from dotenv import load_dotenv
from suno_client import SunoClient, SunoAPIError

# Load environment variables
load_dotenv()


async def generate_song():
    """Generate 'A Place Forgotten' song."""
    print("=" * 60)
    print("Generating: A Place Forgotten")
    print("=" * 60)

    lyrics = """Stone walls rise around my days
Counting shadows, losing ways
Silver moonlight through the bars
Whispers secrets to the stars

This tower holds my beating heart
Keeps the world and me apart
Memories fade like morning mist
In a place that time dismissed

I am the echo no one hears
The silent fall of frozen tears
Reaching out but no one sees
A soul that's longing to be freed

Windows frame a distant shore
Dreams of walking through that door
But these chains aren't made of steel
They're woven from what I can't feel

Will anyone remember me
When I'm just a melody
Drifting through this endless night
In a place forgotten by the light

I am the echo no one hears
The silent fall of frozen tears
Reaching out but no one sees
A soul that's longing to be freed

Still I sing into the void
Hope is battered but not destroyed
One day someone might look up
And see me in this tower stuck"""

    try:
        client = SunoClient()
        print("\n✓ Client initialized")
        print(f"\nGenerating with:")
        print(f"  Title: A Place Forgotten")
        print(f"  Style: orchestral, symphonic ballad")
        print(f"  Model: V5")
        print(f"  Vocals: Female")
        print(f"  Mode: Custom with lyrics")
        print()

        result = await client.generate_music(
            prompt=lyrics,
            title="A Place Forgotten",
            style="orchestral, symphonic ballad, epic strings, emotional piano, cinematic, powerful female vocals",
            model_version="V5",
            custom_mode=True,
            vocal_gender="f",
            wait_audio=True,
            callback_url="https://example.com/webhook/suno"
        )

        print("\n" + "=" * 60)
        print("GENERATION RESULT")
        print("=" * 60)
        print(json.dumps(result, indent=2))

        if result.get("code") == 200:
            print("\n✓ SUCCESS!")
            data = result.get("data", {})

            if isinstance(data, dict) and "taskId" in data:
                print(f"\nTask ID: {data['taskId']}")
                print("\nNote: The song is being generated. Check status with:")
                print(f"  python -c 'import asyncio; from suno_client import SunoClient; asyncio.run(SunoClient().get_music_info([\"{data['taskId']}\"]))'")

            elif isinstance(data, list):
                print(f"\n{len(data)} track(s) generated:")
                for i, track in enumerate(data, 1):
                    print(f"\nTrack {i}:")
                    print(f"  ID: {track.get('id')}")
                    print(f"  Title: {track.get('title')}")
                    print(f"  Status: {track.get('status')}")
                    if track.get('audio_url'):
                        print(f"  Audio: {track['audio_url']}")
                    if track.get('video_url'):
                        print(f"  Video: {track['video_url']}")
        else:
            print(f"\n✗ Error: {result}")

        await client.close()

    except SunoAPIError as e:
        print(f"\n✗ Suno API Error: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(generate_song())
    exit(exit_code)
