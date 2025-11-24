# Suno MCP Server

A Model Context Protocol (MCP) server that provides AI music generation capabilities using the Suno API. This server allows Claude and other MCP clients to generate music, retrieve track information, and manage API credits through a simple tool interface.

## Features

- **Generate Music**: Create AI-generated music from text prompts with customizable parameters
- **Track Information**: Retrieve detailed information about generated tracks including status, URLs, and metadata
- **Credit Management**: Check API credit balance and usage statistics
- **Multiple Model Versions**: Support for Suno v3.5, v4, v4.5, and v5 models
- **Custom Mode**: Fine-tune generation with specific genre tags

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

### 1. generate_music

Generate AI music from a text prompt.

**Parameters:**
- `prompt` (required): Text description of the music (e.g., "upbeat electronic dance music with powerful synths")
- `make_instrumental` (optional): Generate instrumental only, no vocals (default: false)
- `model_version` (optional): AI model version - "v3.5", "v4", "v4.5", or "v5" (default: "v3.5")
- `custom_mode` (optional): Enable custom mode with separate genre tags (default: false)
- `tags` (optional): Genre/style tags, required if custom_mode is true (e.g., "electronic, dance, energetic")
- `title` (optional): Title for the generated song
- `wait_audio` (optional): Wait for generation to complete (default: true)

**Example:**
```
Generate an upbeat electronic dance track with powerful synths and energetic beats
```

### 2. get_music_info

Get detailed information about generated tracks.

**Parameters:**
- `track_ids` (required): Array of track IDs to retrieve information for

**Example:**
```
Get information for tracks: ["track-id-1", "track-id-2"]
```

### 3. get_credits

Check your Suno API account balance and usage.

**Parameters:** None

**Example:**
```
Check my Suno API credits
```

## Example Workflow

1. **Generate Music:**
   - Ask Claude: "Generate a calm piano melody for meditation"
   - The tool will return track IDs and information

2. **Check Status:**
   - If you need to check the status later, use: "Get info for track [track-id]"
   - Retrieves current status, URLs, and metadata

3. **Monitor Credits:**
   - Ask: "How many Suno credits do I have left?"
   - Returns balance and usage information

## Troubleshooting

### "SUNO_API_KEY must be provided"
- Ensure your `.env` file exists and contains a valid API key
- Check that the environment variable is properly set in your MCP configuration

### "Failed to generate music: 401 Unauthorized"
- Verify your API key is correct and active
- Check that your API key has sufficient credits

### "Connection timeout"
- Music generation can take time; the default timeout is 5 minutes
- For longer generations, consider setting `wait_audio: false` and polling with `get_music_info`

## API Reference

This server uses the Suno API v1. For more information about the API:
- Documentation: https://docs.sunoapi.org/
- API Key Management: https://sunoapi.org/api-key

## License

This MCP server is provided as-is for use with the Suno API. Please refer to Suno's terms of service for API usage guidelines.

## Support

For issues related to:
- **This MCP server**: Check the configuration and logs
- **Suno API**: Visit https://docs.sunoapi.org/
- **MCP Protocol**: Visit https://modelcontextprotocol.io/
