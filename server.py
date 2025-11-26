#!/usr/bin/env python3
"""Suno MCP Server - AI Music Generation via Model Context Protocol."""

import asyncio
import os
from typing import Any
from dotenv import load_dotenv

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

from suno_client import SunoClient, SunoAPIError

# Load environment variables
load_dotenv()

# Initialize server
server = Server("suno-mcp-server")

# Global client instance
suno_client: SunoClient | None = None


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available Suno API tools."""
    return [
        Tool(
            name="generate_music",
            description="Generate AI music from a text prompt. Creates high-quality music in various styles and genres. Supports both simple and custom modes with advanced controls. Returns track IDs that can be used to check status and retrieve the generated audio.",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Text description/lyrics for the music. In Custom Mode with make_instrumental=false, this is used as exact lyrics (max 3000-5000 chars). In Non-custom Mode, used as core idea for auto-generated lyrics (max 500 chars). Not required if custom_mode=true and make_instrumental=true."
                    },
                    "make_instrumental": {
                        "type": "boolean",
                        "description": "If true, generate instrumental only without vocals",
                        "default": False
                    },
                    "model_version": {
                        "type": "string",
                        "description": "AI model version to use. V5 offers superior musical expression and faster generation.",
                        "enum": ["v3.5", "v4", "v4.5", "v4.5plus", "v5"],
                        "default": "v3.5"
                    },
                    "custom_mode": {
                        "type": "boolean",
                        "description": "Enable custom mode for advanced control. When true, requires style and title parameters. Allows you to specify exact lyrics, music style, and other advanced settings.",
                        "default": False
                    },
                    "style": {
                        "type": "string",
                        "description": "Music style/genre (required in Custom Mode, e.g., 'orchestral epic, cinematic, powerful strings'). Max 200-1000 chars depending on model."
                    },
                    "title": {
                        "type": "string",
                        "description": "Song title (required in Custom Mode). Max 80 characters."
                    },
                    "wait_audio": {
                        "type": "boolean",
                        "description": "If true, wait for audio generation to complete before returning",
                        "default": True
                    },
                    "callback_url": {
                        "type": "string",
                        "description": "Webhook URL for completion notification (e.g., 'https://example.com/webhook')"
                    },
                    "persona_id": {
                        "type": "string",
                        "description": "Persona identifier for stylistic influence (Custom Mode only)"
                    },
                    "negative_tags": {
                        "type": "string",
                        "description": "Styles or traits to exclude from generation (e.g., 'aggressive, heavy metal')"
                    },
                    "vocal_gender": {
                        "type": "string",
                        "description": "Preferred vocal gender",
                        "enum": ["m", "f"]
                    },
                    "style_weight": {
                        "type": "number",
                        "description": "Weight of style guidance (0.00-1.00). Higher values adhere more strictly to the specified style.",
                        "minimum": 0.0,
                        "maximum": 1.0
                    },
                    "weirdness_constraint": {
                        "type": "number",
                        "description": "Creative deviation tolerance (0.00-1.00). Higher values allow more experimental/unusual results.",
                        "minimum": 0.0,
                        "maximum": 1.0
                    },
                    "audio_weight": {
                        "type": "number",
                        "description": "Input audio influence weighting (0.00-1.00)",
                        "minimum": 0.0,
                        "maximum": 1.0
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_task_status",
            description="Get the status of a music generation task using the taskId returned from generate_music. This shows generation progress and track information once complete.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "The task ID returned from generate_music"
                    }
                },
                "required": ["task_id"]
            }
        ),
        Tool(
            name="get_music_info",
            description="Get detailed information about generated music tracks using track IDs (not task IDs). Use this for tracks you already have the specific track IDs for.",
            inputSchema={
                "type": "object",
                "properties": {
                    "track_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of track IDs to retrieve information for"
                    }
                },
                "required": ["track_ids"]
            }
        ),
        Tool(
            name="get_credits",
            description="Check your Suno API account credit balance and usage statistics.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="convert_to_wav",
            description="Convert a generated MP3 track to high-quality WAV format. Requires BOTH task_id (generation job ID) AND audio_id (specific track ID). CRITICAL FOR AI: Returns a NEW conversion task_id (different from generation task_id) which you MUST save and provide to the user. This conversion task_id is the ONLY way to retrieve the WAV download URL later. The API does NOT support querying by audio_id alone. If the conversion task_id is lost, the WAV URL is permanently unrecoverable.",
            inputSchema={
                "type": "object",
                "properties": {
                    "callback_url": {
                        "type": "string",
                        "description": "Webhook URL for conversion completion notification (e.g., 'https://example.com/webhook')"
                    },
                    "task_id": {
                        "type": "string",
                        "description": "Generation task ID (taskId) from music['data']['taskId'] - the hex string identifying the generation job (REQUIRED)"
                    },
                    "audio_id": {
                        "type": "string",
                        "description": "Track ID (audioId) from music['data']['sunoData'][0]['id'] - UUID identifying the specific track to convert (REQUIRED)"
                    }
                },
                "required": ["callback_url", "task_id", "audio_id"]
            }
        ),
        Tool(
            name="get_wav_conversion_status",
            description="Get the status of a WAV conversion task and retrieve the WAV download URL. CRITICAL: You must use the CONVERSION task_id returned from convert_to_wav (NOT the generation task_id from generate_music). These are two different task IDs. The conversion task_id is the ONLY way to retrieve the WAV download URL - there is no other method to query by audio_id or generation task_id.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "The task ID returned from convert_to_wav"
                    }
                },
                "required": ["task_id"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool execution requests."""
    if not suno_client:
        raise RuntimeError("Suno client not initialized")

    try:
        if name == "generate_music":
            # Extract arguments
            prompt = arguments.get("prompt")
            make_instrumental = arguments.get("make_instrumental", False)
            model_version = arguments.get("model_version", "v3.5")

            # Convert model version format from "v3.5" to "V3_5" for API
            model_version_map = {
                "v3.5": "V3_5",
                "v4": "V4",
                "v4.5": "V4_5",
                "v4.5plus": "V4_5PLUS",
                "v5": "V5"
            }
            api_model_version = model_version_map.get(model_version, "V3_5")

            custom_mode = arguments.get("custom_mode", False)
            style = arguments.get("style")
            title = arguments.get("title")
            wait_audio = arguments.get("wait_audio", True)
            callback_url = arguments.get("callback_url")
            persona_id = arguments.get("persona_id")
            negative_tags = arguments.get("negative_tags")
            vocal_gender = arguments.get("vocal_gender")
            style_weight = arguments.get("style_weight")
            weirdness_constraint = arguments.get("weirdness_constraint")
            audio_weight = arguments.get("audio_weight")

            # Generate music
            result = await suno_client.generate_music(
                prompt=prompt,
                make_instrumental=make_instrumental,
                model_version=api_model_version,
                wait_audio=wait_audio,
                custom_mode=custom_mode,
                style=style,
                title=title,
                callback_url=callback_url,
                persona_id=persona_id,
                negative_tags=negative_tags,
                vocal_gender=vocal_gender,
                style_weight=style_weight,
                weirdness_constraint=weirdness_constraint,
                audio_weight=audio_weight
            )

            # Format response
            response_text = f"Music generation {'completed' if wait_audio else 'started'}!\n\n"

            if "data" in result and result["data"] is not None:
                data = result["data"]

                # Check if data is a dict with taskId (async generation)
                if isinstance(data, dict) and "taskId" in data:
                    response_text += f"Task ID: {data['taskId']}\n"
                    response_text += "\nNote: Generation is processing asynchronously. You can check status later using the task ID.\n"
                # Check if data is a list of tracks (completed generation)
                elif isinstance(data, list):
                    tracks = data
                    response_text += f"Generated {len(tracks)} track(s):\n\n"

                    for i, track in enumerate(tracks, 1):
                        response_text += f"Track {i}:\n"
                        response_text += f"  ID: {track.get('id', 'N/A')}\n"
                        response_text += f"  Title: {track.get('title', 'N/A')}\n"
                        response_text += f"  Status: {track.get('status', 'N/A')}\n"

                        if track.get('audio_url'):
                            response_text += f"  Audio URL: {track['audio_url']}\n"
                        if track.get('video_url'):
                            response_text += f"  Video URL: {track['video_url']}\n"
                        if track.get('duration'):
                            response_text += f"  Duration: {track['duration']}s\n"

                        response_text += "\n"

                    if not wait_audio:
                        response_text += "Note: Use get_music_info with the track IDs above to check generation status and retrieve audio URLs.\n"
                else:
                    response_text += f"Data: {data}\n"
            else:
                response_text += f"Response: {result}\n"

            return [TextContent(type="text", text=response_text)]

        elif name == "get_task_status":
            # Extract task ID
            task_id = arguments.get("task_id")
            if not task_id:
                raise ValueError("task_id is required")

            # Get task status
            result = await suno_client.get_task_status(task_id)

            # Format response
            response_text = "Music Generation Task Status:\n\n"

            if "data" in result:
                data = result["data"]

                response_text += f"Task ID: {data.get('taskId', 'N/A')}\n"
                response_text += f"Status: {data.get('status', 'N/A')}\n"
                response_text += f"Operation: {data.get('operationType', 'N/A')}\n"
                response_text += f"Model: {data.get('type', 'N/A')}\n"

                # Check if response contains track data
                response_data = data.get('response')
                suno_data = []
                if response_data and isinstance(response_data, dict):
                    suno_data = response_data.get('sunoData', [])

                if suno_data:
                    response_text += f"\n{len(suno_data)} track(s) generated:\n\n"

                    for i, track in enumerate(suno_data, 1):
                        response_text += f"Track {i}:\n"
                        response_text += f"  ID: {track.get('id', 'N/A')}\n"
                        response_text += f"  Title: {track.get('title', 'N/A')}\n"
                        response_text += f"  Model: {track.get('modelName', 'N/A')}\n"

                        if track.get('duration'):
                            response_text += f"  Duration: {track['duration']}s\n"

                        if track.get('tags'):
                            response_text += f"  Tags: {track['tags']}\n"

                        if track.get('audioUrl'):
                            response_text += f"  Audio URL: {track['audioUrl']}\n"

                        if track.get('streamAudioUrl'):
                            response_text += f"  Stream URL: {track['streamAudioUrl']}\n"

                        if track.get('imageUrl'):
                            response_text += f"  Image URL: {track['imageUrl']}\n"

                        if track.get('createTime'):
                            response_text += f"  Created: {track['createTime']}\n"

                        response_text += "\n"
                else:
                    response_text += f"\nGeneration in progress. Current status: {data.get('status', 'UNKNOWN')}\n"
            else:
                response_text += f"Response: {result}\n"

            return [TextContent(type="text", text=response_text)]

        elif name == "get_music_info":
            # Extract track IDs
            track_ids = arguments.get("track_ids")
            if not track_ids or not isinstance(track_ids, list):
                raise ValueError("track_ids must be a non-empty list")

            # Get music info
            result = await suno_client.get_music_info(track_ids)

            # Format response
            response_text = "Music Track Information:\n\n"

            if "data" in result:
                tracks = result["data"]

                for i, track in enumerate(tracks, 1):
                    response_text += f"Track {i}:\n"
                    response_text += f"  ID: {track.get('id', 'N/A')}\n"
                    response_text += f"  Title: {track.get('title', 'N/A')}\n"
                    response_text += f"  Status: {track.get('status', 'N/A')}\n"
                    response_text += f"  Model: {track.get('model_name', 'N/A')}\n"

                    if track.get('audio_url'):
                        response_text += f"  Audio URL: {track['audio_url']}\n"
                    if track.get('video_url'):
                        response_text += f"  Video URL: {track['video_url']}\n"
                    if track.get('image_url'):
                        response_text += f"  Image URL: {track['image_url']}\n"

                    if track.get('duration'):
                        response_text += f"  Duration: {track['duration']}s\n"
                    if track.get('tags'):
                        response_text += f"  Tags: {track['tags']}\n"
                    if track.get('prompt'):
                        response_text += f"  Prompt: {track['prompt']}\n"

                    response_text += f"  Created: {track.get('created_at', 'N/A')}\n"
                    response_text += "\n"
            else:
                response_text += f"Response: {result}\n"

            return [TextContent(type="text", text=response_text)]

        elif name == "get_credits":
            # Get credit info
            result = await suno_client.get_credits()

            # Format response
            response_text = "Suno API Credits:\n\n"

            if "data" in result:
                data = result["data"]
                # The API returns credits as a simple float value
                if isinstance(data, (int, float)):
                    response_text += f"Remaining Credits: {data}\n"
                else:
                    # Handle if the API format changes to return detailed breakdown
                    response_text += f"Total Credits: {data.get('total_credits', 'N/A')}\n"
                    response_text += f"Used Credits: {data.get('used_credits', 'N/A')}\n"
                    response_text += f"Remaining Credits: {data.get('remaining_credits', 'N/A')}\n"
            else:
                response_text += f"Response: {result}\n"

            return [TextContent(type="text", text=response_text)]

        elif name == "convert_to_wav":
            # Extract arguments
            callback_url = arguments.get("callback_url")
            task_id = arguments.get("task_id")
            audio_id = arguments.get("audio_id")

            if not callback_url:
                raise ValueError("callback_url is required")

            if not task_id:
                raise ValueError("task_id is required (generation job ID from music['data']['taskId'])")

            if not audio_id:
                raise ValueError("audio_id is required (track ID from music['data']['sunoData'][0]['id'])")

            # Convert to WAV (BOTH IDs required per Suno API)
            result = await suno_client.convert_to_wav(
                callback_url=callback_url,
                task_id=task_id,
                audio_id=audio_id
            )

            # Format response
            response_text = "WAV Conversion Started!\n\n"

            if "data" in result and result["data"] is not None:
                data = result["data"]

                # Check if data contains taskId
                if isinstance(data, dict) and "taskId" in data:
                    conversion_task_id = data['taskId']
                    response_text += f"🎵 WAV Conversion Initiated\n\n"
                    response_text += f"=" * 60 + "\n"
                    response_text += f"⚠️  CRITICAL: SAVE THIS CONVERSION TASK ID  ⚠️\n"
                    response_text += f"=" * 60 + "\n\n"
                    response_text += f"Conversion Task ID: {conversion_task_id}\n\n"
                    response_text += f"This is a DIFFERENT ID from the generation task_id!\n"
                    response_text += f"Original Generation Task ID: {task_id}\n"
                    response_text += f"Track Audio ID: {audio_id}\n\n"
                    response_text += f"🔴 WITHOUT THIS CONVERSION TASK ID, YOU CANNOT:\n"
                    response_text += f"   - Retrieve the WAV download URL\n"
                    response_text += f"   - Check conversion status\n"
                    response_text += f"   - Access the converted file\n\n"
                    response_text += f"✅ TO GET THE WAV DOWNLOAD URL:\n"
                    response_text += f"   Use: get_wav_conversion_status(task_id=\"{conversion_task_id}\")\n\n"
                    response_text += f"⚠️  The Suno API has NO other way to retrieve the WAV URL.\n"
                    response_text += f"   You CANNOT query by audio_id or generation task_id.\n"
                    response_text += f"   If you lose this conversion task_id, the WAV is unrecoverable.\n"
                else:
                    response_text += f"Data: {data}\n"
            else:
                response_text += f"Response: {result}\n"

            return [TextContent(type="text", text=response_text)]

        elif name == "get_wav_conversion_status":
            # Extract task ID
            task_id = arguments.get("task_id")
            if not task_id:
                raise ValueError("task_id is required")

            # Get WAV conversion status
            result = await suno_client.get_wav_conversion_status(task_id)

            # Format response
            response_text = "WAV Conversion Task Status:\n\n"

            if "data" in result and result["data"] is not None:
                data = result["data"]

                response_text += f"Task ID: {data.get('taskId', 'N/A')}\n"
                response_text += f"Music ID: {data.get('musicId', 'N/A')}\n"
                response_text += f"Status: {data.get('successFlag', 'N/A')}\n"

                # Check if conversion is complete and has WAV URL
                response_data = data.get('response')
                if response_data and isinstance(response_data, dict):
                    wav_url = response_data.get('audioWavUrl')
                    if wav_url:
                        response_text += "\n✅ WAV Conversion Complete!\n"
                        response_text += f"WAV Download URL: {wav_url}\n"

                        if data.get('completeTime'):
                            response_text += f"Completed: {data['completeTime']}\n"
                        if data.get('createTime'):
                            response_text += f"Created: {data['createTime']}\n"
                    else:
                        # Conversion still in progress
                        response_text += f"\n⏳ Conversion in progress...\n"
                        response_text += f"Current Status: {data.get('successFlag', 'PENDING')}\n"
                else:
                    response_text += f"\n⏳ Conversion in progress...\n"
                    response_text += f"Current Status: {data.get('successFlag', 'PENDING')}\n"

                # Show errors if any
                if data.get('errorCode') or data.get('errorMessage'):
                    response_text += f"\n⚠️ Error Details:\n"
                    response_text += f"Error Code: {data.get('errorCode', 'N/A')}\n"
                    response_text += f"Error Message: {data.get('errorMessage', 'N/A')}\n"
            else:
                response_text += f"Response: {result}\n"

            return [TextContent(type="text", text=response_text)]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except SunoAPIError as e:
        return [TextContent(type="text", text=f"Suno API Error: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Run the MCP server."""
    global suno_client

    # Initialize Suno client
    try:
        suno_client = SunoClient()
        # Successfully initialized - do not print to stdout as it corrupts MCP JSON-RPC protocol
    except Exception as e:
        # Failed to initialize - exit silently to avoid corrupting MCP protocol
        # Error will be reported when tools are called
        return

    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        try:
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="suno-mcp-server",
                    server_version="1.0.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
        finally:
            if suno_client:
                await suno_client.close()


if __name__ == "__main__":
    asyncio.run(main())
