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

- **Option 1 (Docker - Recommended)**: Docker and Docker Compose installed
- **Option 2 (Native Python)**: Python 3.10 or higher
- A Suno API key (obtain from [sunoapi.org](https://sunoapi.org))
- An MCP-compatible client: Claude Desktop or Claude Code

## Installation

### Option 1: Docker Installation (Recommended)

Docker provides a portable, isolated environment for the MCP server with all dependencies pre-configured.

1. Clone this repository:
```bash
git clone https://github.com/CodeKeanu/suno-mcp.git
cd suno-mcp
```

2. Configure your API key:
```bash
cp .env.example .env
```

3. Edit `.env` and add your Suno API key:
```
SUNO_API_KEY=your_actual_api_key_here
SUNO_API_BASE_URL=https://api.sunoapi.org
```

4. Build the Docker image:
```bash
docker build -t suno-mcp-server:latest .
# Or use docker-compose:
docker-compose build
```

That's it! The Docker image is now ready to use.

### Option 2: Native Python Installation

1. Clone this repository:
```bash
git clone https://github.com/CodeKeanu/suno-mcp.git
cd suno-mcp
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

## Usage

### Usage with Claude Desktop

Claude Desktop is the official desktop application for Claude that supports MCP servers.

#### Docker Configuration (Recommended)

1. Locate your Claude Desktop configuration file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. Add the Suno MCP server configuration (replace `/absolute/path/to/suno-mcp` with your actual path):

```json
{
  "mcpServers": {
    "suno": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "--env-file",
        "/absolute/path/to/suno-mcp/.env",
        "suno-mcp-server:latest"
      ]
    }
  }
}
```

**Example paths:**
- macOS: `/Users/yourusername/projects/suno-mcp/.env`
- Windows: `C:\\Users\\yourusername\\projects\\suno-mcp\\.env`
- Linux: `/home/yourusername/projects/suno-mcp/.env`

**Important Notes:**
- Use **absolute paths** (full path from root), not relative paths
- On Windows, use double backslashes (`\\`) or forward slashes (`/`)
- Ensure Docker Desktop is running before starting Claude Desktop
- The `.env` file must contain your valid Suno API key

3. **Restart Claude Desktop** completely for changes to take effect

4. Test the integration by asking Claude:
   - "Can you check my Suno API credits?"
   - "Generate a short happy instrumental song"

#### Native Python Configuration

For native Python (without Docker):

```json
{
  "mcpServers": {
    "suno": {
      "command": "python",
      "args": ["/absolute/path/to/suno-mcp/server.py"],
      "env": {
        "SUNO_API_KEY": "your_actual_api_key_here",
        "SUNO_API_BASE_URL": "https://api.sunoapi.org"
      }
    }
  }
}
```

### Usage with Claude Code

Claude Code is a CLI tool for software development with Claude.

#### Docker Configuration (Recommended)

**Option 1: Using Claude Code Settings UI**

1. Open Claude Code settings
2. Navigate to MCP Servers section
3. Add a new server with:
   - **Name**: `suno`
   - **Command**: `docker`
   - **Arguments**: `["run", "--rm", "-i", "--env-file", "/absolute/path/to/suno-mcp/.env", "suno-mcp-server:latest"]`
   - Replace `/absolute/path/to/suno-mcp/.env` with your actual path

**Option 2: Manual Configuration**

Add to your MCP settings file (typically `~/.config/claude-code/mcp_settings.json`):

```json
{
  "mcpServers": {
    "suno": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "--env-file",
        "/absolute/path/to/suno-mcp/.env",
        "suno-mcp-server:latest"
      ]
    }
  }
}
```

**Important:** Replace `/absolute/path/to/suno-mcp/.env` with the actual path where you cloned the repository.

**Docker Flags Explained:**
- `--rm`: Automatically remove container when it exits
- `-i`: Keep stdin open for MCP stdio communication
- `--env-file`: Load environment variables from `.env` file (keeps API key secure)

#### Native Python Configuration

**Option 1: Using Claude Code Settings UI**

1. Open Claude Code settings
2. Navigate to MCP Servers section
3. Add a new server with:
   - **Name**: `suno`
   - **Command**: `python`
   - **Arguments**: `["/absolute/path/to/suno-mcp/server.py"]`
   - **Environment Variables**:
     - `SUNO_API_KEY`: Your API key
     - `SUNO_API_BASE_URL`: `https://api.sunoapi.org`

**Option 2: Manual Configuration**

Add to your MCP settings file:

```json
{
  "mcpServers": {
    "suno": {
      "command": "python",
      "args": ["/absolute/path/to/suno-mcp/server.py"],
      "env": {
        "SUNO_API_KEY": "your_actual_api_key_here",
        "SUNO_API_BASE_URL": "https://api.sunoapi.org"
      }
    }
  }
}
```

**Important:**
- Replace `/absolute/path/to/suno-mcp/server.py` with your actual path
- Restart Claude Code after adding the configuration

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

## Docker Deployment Guide

This section covers Docker-specific usage and management.

### Building the Image

```bash
# Using Docker directly
docker build -t suno-mcp-server:latest .

# Or using Docker Compose (if installed)
docker-compose build
# OR (newer plugin syntax)
docker compose build
```

### Running the Container Manually

For testing or standalone use:

```bash
# Run with environment file
docker run --rm -i --env-file .env suno-mcp-server:latest

# Or pass environment variables directly
docker run --rm -i \
  -e SUNO_API_KEY=your_api_key_here \
  -e SUNO_API_BASE_URL=https://api.sunoapi.org \
  suno-mcp-server:latest
```

### Health Checks

The Docker container includes automatic health monitoring:

```bash
# Check container health status
docker ps

# View health check logs
docker inspect --format='{{json .State.Health}}' suno-mcp-server

# Manual health check
docker exec suno-mcp-server python healthcheck.py
```

Health checks verify:
- Environment variables are properly set
- Required Python modules are available
- Suno client can initialize correctly

### Docker Compose Usage

```bash
# Build the image
docker-compose build

# Start the server (for testing)
docker-compose up

# View logs
docker-compose logs -f

# Stop the server
docker-compose down

# Rebuild after code changes
docker-compose build --no-cache
```

### Security Best Practices

1. **Never commit `.env` to version control** - It contains your API key
2. **Use `.env` file** - Keeps secrets out of command history and scripts
3. **Non-root execution** - Container runs as `appuser` (UID 1000)
4. **Minimal image** - Based on `python:3.12-slim` to reduce attack surface
5. **Read-only filesystem** - Optional; uncomment in `docker-compose.yml` if needed

### Container Resource Management

The `docker-compose.yml` includes resource limits:
- CPU limit: 1.0 cores
- Memory limit: 512MB
- CPU reservation: 0.5 cores
- Memory reservation: 256MB

Adjust these in `docker-compose.yml` if needed for your environment.

### Updating the Container

After making code changes:

```bash
# Rebuild the image
docker-compose build

# Or rebuild without cache
docker-compose build --no-cache

# Restart Claude Code to pick up the new image
```

### Troubleshooting Docker Issues

#### Container fails health check
```bash
# Check health check output
docker logs suno-mcp-server

# Run health check manually
docker run --rm -i --env-file .env suno-mcp-server:latest python healthcheck.py
```

#### "Cannot connect to the Docker daemon"
- Ensure Docker is running: `sudo systemctl start docker`
- Check Docker permissions: `sudo usermod -aG docker $USER` (then log out/in)

#### Container exits immediately
- Check logs: `docker logs suno-mcp-server`
- Verify `.env` file exists and contains valid API key
- Ensure image built successfully: `docker images | grep suno-mcp-server`

#### Environment variables not loading
- Verify `.env` file path in docker-compose.yml or docker run command
- Check file permissions: `ls -la .env`
- Ensure `.env` file format is correct (no quotes around values)

## Troubleshooting

### Common Errors

#### "SUNO_API_KEY must be provided"
- **Docker**:
  - Ensure `.env` file exists in your project directory
  - Verify the absolute path to `.env` in your MCP configuration is correct
  - Check that the `.env` file contains: `SUNO_API_KEY=your_actual_key`
  - Make sure Docker can access the file (permissions)
- **Native**:
  - Ensure your `.env` file exists and contains a valid API key
  - Or verify the `SUNO_API_KEY` is set in the `env` section of your MCP configuration

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
