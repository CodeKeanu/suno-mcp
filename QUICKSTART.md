# Quick Start Guide

Get up and running with the Suno MCP Server in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Configure API Key

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API key
nano .env
```

Add your Suno API key:
```
SUNO_API_KEY=your_actual_api_key_here
SUNO_API_BASE_URL=https://api.sunoapi.org
```

## Step 3: Test the Setup (Optional but Recommended)

```bash
python testing/integration/test_client.py
```

This will verify your API key works and test all client functions.

## Step 4: Add to Claude Code

Add this server to your Claude Code MCP configuration:

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

**Note:** Replace `your_actual_api_key_here` with your real API key!

## Step 5: Restart Claude Code

Restart Claude Code to load the new MCP server.

## Step 6: Try It Out!

Ask Claude to generate music:

```
Generate a peaceful ambient soundscape with soft synths
```

Or check your credits:

```
How many Suno API credits do I have?
```

## Troubleshooting

### ImportError: No module named 'mcp'
```bash
pip install mcp
```

### "SUNO_API_KEY must be provided"
- Check that your `.env` file exists
- Verify the API key is correctly set
- Ensure Claude Code configuration has the correct env variables

### Server not showing up in Claude Code
- Check the MCP configuration file path
- Verify Python is in your PATH
- Look at Claude Code logs for error messages

## Next Steps

See `README.md` for detailed documentation on all available tools and parameters.
