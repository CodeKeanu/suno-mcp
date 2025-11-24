# Suno MCP Server

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/CodeKeanu/suno-mcp)
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-orange.svg)](https://modelcontextprotocol.io/)
[![Suno API](https://img.shields.io/badge/Suno%20API-v1-purple.svg)](https://docs.sunoapi.org/)
[![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)](LICENSE)

A Model Context Protocol (MCP) server that provides AI music generation capabilities using the Suno API. This server allows Claude and other MCP clients to generate music, retrieve track information, and manage API credits through a simple tool interface.

## Features

- **Generate Music**: Create AI-generated music from text prompts with customizable parameters
- **Track Status Monitoring**: Check generation progress and retrieve completed track information using task IDs
- **Track Information**: Retrieve detailed information about generated tracks including status, URLs, and metadata using track IDs
- **Credit Management**: Check API credit balance and usage statistics
- **Multiple Model Versions**: Support for Suno v3.5, v4, v4.5, v4.5plus, and v5 models (v5 recommended for superior quality and speed)
- **Custom Mode**: Fine-tune generation with exact lyrics, specific genre tags, and advanced controls
- **Advanced Controls**: Style weighting, weirdness constraint, vocal gender selection, and more

## Prerequisites

- Python 3.10 or higher
- A Suno API key (obtain from [sunoapi.org](https://sunoapi.org))
- Claude Code or another MCP-compatible client

## Installation

1. Clone or navigate to this directory:
```bash
cd /root/suno-mcp-proj
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your API key:
```bash
cp .env.example .env
```

4. Edit `.env` and add your Suno API key:
```
SUNO_API_KEY=your_actual_api_key_here
SUNO_API_BASE_URL=https://api.sunoapi.org
```

## Usage with Claude Code

To use this MCP server with Claude Code, add it to your MCP settings configuration:

### Option 1: Using Claude Code Settings UI

1. Open Claude Code settings
2. Navigate to MCP Servers section
3. Add a new server with:
   - **Name**: `suno`
   - **Command**: `python`
   - **Arguments**: `["/root/suno-mcp-proj/server.py"]`
   - **Environment Variables**:
     - `SUNO_API_KEY`: Your API key
     - `SUNO_API_BASE_URL`: `https://api.sunoapi.org`

### Option 2: Manual Configuration

Add to your MCP settings file (typically `~/.config/claude-code/mcp_settings.json`):

```json
{
  "mcpServers": {
    "suno": {
      "command": "python",
      "args": ["/root/suno-mcp-proj/server.py"],
      "env": {
        "SUNO_API_KEY": "your_actual_api_key_here",
        "SUNO_API_BASE_URL": "https://api.sunoapi.org"
      }
    }
  }
}
```

Restart Claude Code after adding the configuration.

## Available Tools

The server exposes 4 MCP tools for music generation and management:

### 1. generate_music

Generate AI music from a text prompt with extensive customization options.

**Parameters:**

**Core Parameters:**
- `prompt` (conditional): Text description/lyrics for the music
  - **Custom Mode with vocals**: Used as exact lyrics (max 3000-5000 chars depending on model)
  - **Non-custom Mode**: Used as core idea for auto-generated lyrics (max 500 chars)
  - **Custom Mode instrumental**: Not required if `make_instrumental=true`
- `make_instrumental` (optional, default: false): Generate instrumental only without vocals
- `model_version` (optional, default: "v3.5"): AI model version
  - Options: "v3.5", "v4", "v4.5", "v4.5plus", "v5"
  - **Recommendation**: Use "v5" for superior musical expression and faster generation
- `wait_audio` (optional, default: true): Wait for generation to complete before returning

**Custom Mode Parameters:**
- `custom_mode` (optional, default: false): Enable advanced control mode
  - When enabled, requires `style` and `title` parameters
  - Allows exact lyrics specification and fine-grained style control
- `style` (required if custom_mode=true): Music style/genre tags (max 200-1000 chars)
  - Example: "orchestral epic, cinematic, powerful strings, dramatic choir"
- `title` (required if custom_mode=true): Song title (max 80 chars)

**Advanced Parameters:**
- `callback_url` (optional): Webhook URL for completion notification
  - **Note**: The Suno API may require this parameter. If generation fails with "Please enter callBackUrl", provide a URL (e.g., "https://example.com/webhook")
- `persona_id` (optional): Persona identifier for stylistic influence (Custom Mode only)
- `negative_tags` (optional): Styles or traits to exclude (e.g., "aggressive, heavy metal")
- `vocal_gender` (optional): Preferred vocal gender ("m" or "f")
- `style_weight` (optional): Weight of style guidance (0.00-1.00)
  - Higher values adhere more strictly to the specified style
- `weirdness_constraint` (optional): Creative deviation tolerance (0.00-1.00)
  - Higher values allow more experimental/unusual results
- `audio_weight` (optional): Input audio influence weighting (0.00-1.00)

**Returns:**
- Task ID for async generation tracking
- Track information if `wait_audio=true`

**Example:**
```
Generate a calm piano meditation piece using v5 model
```

### 2. get_task_status

Get the status of a music generation task and retrieve track information once complete.

**Parameters:**
- `task_id` (required): The task ID returned from `generate_music`

**Returns:**
- Task status (e.g., "TEXT_SUCCESS")
- Operation type and model information
- Track details including IDs, titles, audio URLs, and metadata when generation is complete

**Example:**
```
Check status of task: 684b694f002afbb35b49994b32a6a01e
```

**Note:** This tool uses task IDs (not track IDs). Use this to monitor async generations started with `wait_audio=false` or to retrieve information about recently completed generations.

### 3. get_music_info

Get detailed information about specific tracks using track IDs.

**Parameters:**
- `track_ids` (required): Array of track IDs to retrieve information for

**Returns:**
- Detailed track information including status, URLs, duration, tags, and creation time

**Example:**
```
Get information for tracks: ["7752c889-3601-4e55-b805-54a28a53de85", "be973545-05f9-4a00-9177-81d4ce0ed5c1"]
```

**Note:** This tool uses specific track IDs (not task IDs). Track IDs are returned from `generate_music` or `get_task_status`.

### 4. get_credits

Check your Suno API account credit balance.

**Parameters:** None

**Returns:**
- Remaining API credits

**Example:**
```
Check my Suno API credits
```

## Example Workflows

### Basic Music Generation (Recommended)
1. **Generate Music with v5 Model:**
   ```
   Generate an epic orchestral battle theme using v5 model in custom mode
   ```
   - Claude will use custom mode with appropriate style tags
   - Returns task ID and track information
   - Uses v5 model for best quality

2. **Check Credits:**
   ```
   How many Suno credits do I have left?
   ```

### Advanced: Async Generation with Monitoring
1. **Start Async Generation:**
   ```
   Generate a 3-minute ambient soundscape, don't wait for completion
   ```
   - Returns task ID immediately
   - Generation continues in background

2. **Monitor Progress:**
   ```
   Check status of task: [task-id]
   ```
   - Shows generation progress
   - Returns track IDs and URLs when complete

3. **Get Track Details:**
   ```
   Get information for tracks: ["track-id-1", "track-id-2"]
   ```
   - Retrieves detailed metadata and download URLs

### Understanding IDs
- **Task ID**: Returned from `generate_music`, used with `get_task_status`
  - Example: `684b694f002afbb35b49994b32a6a01e`
  - Used to monitor generation progress

- **Track ID**: Specific to each generated song, used with `get_music_info`
  - Example: `7752c889-3601-4e55-b805-54a28a53de85`
  - Suno typically generates 2 tracks per request
  - Each track has its own unique ID

## Troubleshooting

### Common Errors

#### "SUNO_API_KEY must be provided"
- Ensure your `.env` file exists and contains a valid API key
- Check that the environment variable is properly set in your MCP configuration

#### "Failed to generate music: 401 Unauthorized"
- Verify your API key is correct and active
- Check that your API key has sufficient credits

#### "API Error (code 400): Please enter callBackUrl"
- The Suno API requires a `callback_url` parameter for some operations
- Provide a webhook URL (can be a placeholder like "https://example.com/webhook")
- Claude Code will automatically handle this when using the generate_music tool

#### "Connection timeout"
- Music generation can take time; the default timeout is 5 minutes
- For longer generations, set `wait_audio: false` and use `get_task_status` to poll for completion

#### "style must be provided when custom_mode is True"
- When using custom mode, both `style` and `title` parameters are required
- Provide genre/style tags (e.g., "epic orchestral, cinematic")

### Best Practices

1. **Always specify model version**: Use `model_version: "v5"` for best results
2. **Use custom mode for precise control**: Enables exact lyrics and detailed style specification
3. **Monitor credits regularly**: Each generation consumes credits (typically 6 credits per generation)
4. **Suno generates 2 tracks**: Each request produces 2 variations of your prompt
5. **Use task IDs vs track IDs correctly**:
   - Task IDs: For checking generation status
   - Track IDs: For retrieving specific track information

## Technical Details

### Server Information
- **Server Name**: `suno-mcp-server`
- **Version**: 1.0.0
- **Protocol**: Model Context Protocol (MCP)
- **API**: Suno API v1
- **Python Version**: 3.10+
- **Async Support**: Full async/await implementation using httpx

### API Endpoints Used
- `/api/v1/generate` - Music generation
- `/api/v1/generate/record-info` - Task/track status retrieval
- `/api/v1/generate/credit` - Credit balance check

### Model Version Mapping
The server automatically converts user-friendly version names to API format:
- `v3.5` → `V3_5` (chirp-v3-5)
- `v4` → `V4` (chirp-v4)
- `v4.5` → `V4_5` (chirp-v4-5)
- `v4.5plus` → `V4_5PLUS` (chirp-v4-5-plus)
- `v5` → `V5` (chirp-crow) - **Recommended**

### Credit Costs
- Standard generation: ~6 credits per request
- Generates 2 track variations per request
- Costs may vary based on model version and generation length

## API Reference

This server uses the Suno API v1. For more information:
- **Documentation**: https://docs.sunoapi.org/
- **API Key Management**: https://sunoapi.org/api-key
- **Support**: support@sunoapi.org

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This MCP server is provided as-is for use with the Suno API. Please refer to Suno's terms of service for API usage guidelines.

## Support

For issues related to:
- **This MCP Server**: [Open an issue](https://github.com/CodeKeanu/suno-mcp/issues)
- **Suno API**: Visit https://docs.sunoapi.org/ or contact support@sunoapi.org
- **MCP Protocol**: Visit https://modelcontextprotocol.io/

---

**Built with** ❤️ **using the Model Context Protocol**
