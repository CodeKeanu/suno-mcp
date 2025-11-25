# WAV Conversion Quick Reference

## Quick Start

### 1. Generate Music First
```python
# You need a track ID from a generated song
result = await suno_client.generate_music(
    prompt="Your song description",
    wait_audio=True
)
track_id = result['data'][0]['id']  # e.g., "7752c889-3601-4e55-b805-54a28a53de85"
```

### 2. Convert to WAV
```python
wav_result = await suno_client.convert_to_wav(
    audio_id=track_id,
    callback_url="https://example.com/webhook"
)
task_id = wav_result['data']['taskId']  # e.g., "abc123def456"
```

### 3. Check Conversion Status
```python
status = await suno_client.get_wav_conversion_status(task_id=task_id)

# When complete, get the WAV URL:
if status['data']['status'] == 'COMPLETED':
    wav_url = status['data']['response']['wavData']['wavUrl']
    print(f"Download WAV: {wav_url}")
```

## MCP Tool Usage (via Claude Code)

### Convert Track to WAV
```
User: "Convert track 7752c889-3601-4e55-b805-54a28a53de85 to WAV format"

Claude uses tool: convert_to_wav
Parameters:
  - audio_id: "7752c889-3601-4e55-b805-54a28a53de85"
  - callback_url: "https://example.com/webhook"

Response: Task ID abc123def456
```

### Check Conversion Status
```
User: "Check the status of WAV conversion task abc123def456"

Claude uses tool: get_wav_conversion_status
Parameters:
  - task_id: "abc123def456"

Response: Status and WAV URL (when complete)
```

## API Endpoints

```bash
# Convert to WAV
POST https://api.sunoapi.org/api/v1/wav/generate
Content-Type: application/json
Authorization: Bearer YOUR_API_KEY

{
  "audioId": "7752c889-3601-4e55-b805-54a28a53de85",
  "callBackUrl": "https://example.com/webhook"
}

# Check Status
GET https://api.sunoapi.org/api/v1/wav/record-info?taskId=abc123def456
Authorization: Bearer YOUR_API_KEY
```

## Common Parameters

### audio_id (Track ID)
- Format: UUID (e.g., `7752c889-3601-4e55-b805-54a28a53de85`)
- Source: From `generate_music` or `get_music_info` results
- **NOT** the task ID from generation

### callback_url
- Format: HTTPS URL
- Purpose: Webhook notification when conversion completes
- Example: `https://example.com/webhook`
- Can use placeholder for testing

### task_id (WAV Conversion Task)
- Format: Hex string (e.g., `abc123def456`)
- Source: Returned from `convert_to_wav`
- Used to check conversion status

## Response Status Values

- `PENDING` - Conversion queued
- `PROCESSING` - Conversion in progress
- `COMPLETED` - Conversion finished, WAV URL available
- `FAILED` - Conversion failed, check error message

## Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `audio_id is required` | Missing audio_id parameter | Provide track ID from generated music |
| `callback_url is required` | Missing callback_url | Provide valid HTTPS webhook URL |
| `task_id is required` | Missing task_id | Provide task ID from convert_to_wav |
| `Invalid audio ID format` | Wrong ID format | Use UUID format from track, not task ID |
| `API Error (code 401)` | Invalid API key | Check SUNO_API_KEY in .env |
| `API Error (code 404)` | Track/task not found | Verify ID is correct and track exists |

## Complete Workflow Example

```python
import asyncio
from suno_client import SunoClient

async def generate_and_convert_to_wav():
    client = SunoClient()

    try:
        # Step 1: Generate music
        print("Generating music...")
        music = await client.generate_music(
            prompt="Epic orchestral soundtrack",
            model_version="V5",
            wait_audio=True
        )

        # Extract track ID
        track_id = music['data'][0]['id']
        track_title = music['data'][0]['title']
        print(f"Generated: {track_title} (ID: {track_id})")

        # Step 2: Convert to WAV
        print("Starting WAV conversion...")
        conversion = await client.convert_to_wav(
            audio_id=track_id,
            callback_url="https://example.com/webhook"
        )

        task_id = conversion['data']['taskId']
        print(f"Conversion task ID: {task_id}")

        # Step 3: Poll for completion
        print("Waiting for conversion...")
        max_attempts = 20

        for attempt in range(max_attempts):
            status = await client.get_wav_conversion_status(task_id)
            current_status = status['data']['status']

            print(f"Attempt {attempt + 1}: {current_status}")

            if current_status == 'COMPLETED':
                wav_url = status['data']['response']['wavData']['wavUrl']
                print(f"\n✓ Success! WAV URL: {wav_url}")
                return wav_url

            elif current_status == 'FAILED':
                print("\n✗ Conversion failed!")
                return None

            # Wait before next check
            await asyncio.sleep(3)

        print("\n⚠ Timeout waiting for conversion")
        return None

    finally:
        await client.close()

# Run
if __name__ == "__main__":
    wav_url = asyncio.run(generate_and_convert_to_wav())
```

## Testing Without API Calls

```bash
# Run validation tests (no API key needed)
python3 test_wav_feature.py

# Expected output: All 5 tests PASS
```

## File Locations

| File | Purpose |
|------|---------|
| `/root/suno-mcp-proj/suno_client.py` | Client implementation (lines 241-317) |
| `/root/suno-mcp-proj/server.py` | MCP tools (lines 151-182, 404-472) |
| `/root/suno-mcp-proj/test_wav_feature.py` | Validation tests |
| `/root/suno-mcp-proj/WAV_FEATURE_DOCUMENTATION.md` | Full documentation |

## Tips

1. **Track ID vs Task ID**: Don't confuse them!
   - Track ID = Music file identifier (UUID format)
   - Generation Task ID = From generate_music (used with get_task_status)
   - Conversion Task ID = From convert_to_wav (used with get_wav_conversion_status)

2. **Callback URL**: Required by API but can be placeholder for testing

3. **Polling Frequency**: Wait 3-5 seconds between status checks

4. **Credits**: Check your API credit balance - conversions may cost additional credits

5. **Download WAV**: Use the `wavUrl` from completed status response

## Next Steps

1. Test with real Suno API
2. Implement production security hardening (URL validation)
3. Add retry logic for failed conversions
4. Consider batch conversion support

---

**Version**: 1.0.0
**Last Updated**: 2025-11-25
