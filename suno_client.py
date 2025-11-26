"""Suno API Client for music generation."""

import httpx
from typing import Optional, Dict, Any, List
import os
import re
from urllib.parse import urlparse


class SunoAPIError(Exception):
    """Base exception for Suno API errors."""
    pass


class SunoClient:
    """Client for interacting with the Suno API."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize the Suno API client.

        Args:
            api_key: Suno API key. If not provided, will read from SUNO_API_KEY env var.
            base_url: Base URL for the Suno API. Defaults to https://api.sunoapi.org
        """
        self.api_key = api_key or os.getenv("SUNO_API_KEY")
        if not self.api_key:
            raise ValueError("SUNO_API_KEY must be provided or set in environment")

        self.base_url = base_url or os.getenv("SUNO_API_BASE_URL", "https://api.sunoapi.org")
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=300.0  # 5 minute timeout for music generation
        )

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def generate_music(
        self,
        prompt: Optional[str] = None,
        make_instrumental: bool = False,
        model_version: str = "V3_5",
        wait_audio: bool = True,
        custom_mode: bool = False,
        style: Optional[str] = None,
        title: Optional[str] = None,
        callback_url: Optional[str] = None,
        persona_id: Optional[str] = None,
        negative_tags: Optional[str] = None,
        vocal_gender: Optional[str] = None,
        style_weight: Optional[float] = None,
        weirdness_constraint: Optional[float] = None,
        audio_weight: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Generate music from a text prompt.

        Args:
            prompt: Text description/lyrics for the music. In Custom Mode with instrumental=False,
                   this is used as exact lyrics (max 3000-5000 chars depending on model).
                   In Non-custom Mode, used as core idea for auto-generated lyrics (max 500 chars).
                   Not required if custom_mode=True and make_instrumental=True.
            make_instrumental: If True, generate instrumental only (no vocals)
            model_version: AI model version (V3_5, V4, V4_5, V4_5PLUS, or V5). Defaults to V3_5.
            wait_audio: If True, wait for audio generation to complete
            custom_mode: If True, use custom mode (requires style and title; prompt required if not instrumental)
            style: Music style/genre (required in Custom Mode). Max 200-1000 chars depending on model.
            title: Song title (required in Custom Mode). Max 80 characters.
            callback_url: Webhook URL for completion notification (required by API)
            persona_id: Persona identifier for stylistic influence (Custom Mode only)
            negative_tags: Styles/traits to exclude from generation
            vocal_gender: Preferred vocal gender ('m' or 'f')
            style_weight: Weight of style guidance (0.00-1.00)
            weirdness_constraint: Creative deviation tolerance (0.00-1.00)
            audio_weight: Input audio influence weighting (0.00-1.00)

        Returns:
            Dictionary containing generation task info and results

        Raises:
            SunoAPIError: If the API request fails
            ValueError: If required parameters are missing or invalid
        """
        # Validate custom mode requirements
        if custom_mode:
            if not style:
                raise ValueError("style must be provided when custom_mode is True")
            if not title:
                raise ValueError("title must be provided when custom_mode is True")
            if not make_instrumental and not prompt:
                raise ValueError("prompt must be provided when custom_mode is True and instrumental is False")

        # Validate non-custom mode requirements
        if not custom_mode and not prompt:
            raise ValueError("prompt is required in non-custom mode")

        # Build payload with required parameters
        payload: Dict[str, Any] = {
            "instrumental": make_instrumental,
            "model": model_version,
            "wait_audio": wait_audio,
            "customMode": custom_mode
        }

        # Add prompt if provided
        if prompt:
            payload["prompt"] = prompt

        # Add custom mode parameters
        if custom_mode:
            payload["style"] = style
            payload["title"] = title

        # Add callback URL (required by API)
        if callback_url:
            payload["callBackUrl"] = callback_url

        # Add optional parameters if provided
        if persona_id:
            payload["personaId"] = persona_id

        if negative_tags:
            payload["negativeTags"] = negative_tags

        if vocal_gender and vocal_gender in ['m', 'f']:
            payload["vocalGender"] = vocal_gender

        if style_weight is not None and 0.0 <= style_weight <= 1.0:
            payload["styleWeight"] = style_weight

        if weirdness_constraint is not None and 0.0 <= weirdness_constraint <= 1.0:
            payload["weirdnessConstraint"] = weirdness_constraint

        if audio_weight is not None and 0.0 <= audio_weight <= 1.0:
            payload["audioWeight"] = audio_weight

        try:
            response = await self.client.post("/api/v1/generate", json=payload)
            response.raise_for_status()
            result = response.json()

            # Check for API-level errors (Suno returns HTTP 200 with error codes in JSON)
            if isinstance(result, dict) and result.get("code") != 200:
                error_msg = result.get("msg", "Unknown error")
                raise SunoAPIError(f"API Error (code {result.get('code')}): {error_msg}")

            return result
        except httpx.HTTPError as e:
            raise SunoAPIError(f"Failed to generate music: {str(e)}")

    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get status of a music generation task using taskId.

        Args:
            task_id: Task ID returned from generate_music

        Returns:
            Dictionary containing task status and track information

        Raises:
            SunoAPIError: If the API request fails
        """
        try:
            response = await self.client.get(
                "/api/v1/generate/record-info",
                params={"taskId": task_id}
            )
            response.raise_for_status()
            result = response.json()

            # Check for API-level errors
            if isinstance(result, dict) and result.get("code") != 200:
                error_msg = result.get("msg", "Unknown error")
                raise SunoAPIError(f"API Error (code {result.get('code')}): {error_msg}")

            return result
        except httpx.HTTPError as e:
            raise SunoAPIError(f"Failed to get task status: {str(e)}")

    async def get_music_info(self, ids: List[str]) -> Dict[str, Any]:
        """
        Get information about generated music tracks using track IDs.

        Args:
            ids: List of track IDs to retrieve information for

        Returns:
            Dictionary containing track information

        Raises:
            SunoAPIError: If the API request fails
        """
        try:
            # Join IDs with commas for query parameter
            ids_param = ",".join(ids)
            response = await self.client.get(
                "/api/v1/generate/record-info",
                params={"ids": ids_param}
            )
            response.raise_for_status()
            result = response.json()

            # Check for API-level errors
            if isinstance(result, dict) and result.get("code") != 200:
                error_msg = result.get("msg", "Unknown error")
                raise SunoAPIError(f"API Error (code {result.get('code')}): {error_msg}")

            return result
        except httpx.HTTPError as e:
            raise SunoAPIError(f"Failed to get music info: {str(e)}")

    async def get_credits(self) -> Dict[str, Any]:
        """
        Get remaining API credits.

        Returns:
            Dictionary containing credit balance and usage statistics

        Raises:
            SunoAPIError: If the API request fails
        """
        try:
            response = await self.client.get("/api/v1/generate/credit")
            response.raise_for_status()
            result = response.json()

            # Check for API-level errors
            if isinstance(result, dict) and result.get("code") != 200:
                error_msg = result.get("msg", "Unknown error")
                raise SunoAPIError(f"API Error (code {result.get('code')}): {error_msg}")

            return result
        except httpx.HTTPError as e:
            raise SunoAPIError(f"Failed to get credits: {str(e)}")

    async def convert_to_wav(
        self,
        callback_url: str,
        task_id: str,
        audio_id: str
    ) -> Dict[str, Any]:
        """
        Convert a generated audio track to WAV format.

        Per Suno API docs: BOTH taskId AND audioId are REQUIRED parameters.
        The audioId specifies which exact track to convert (tasks can have multiple tracks).

        Args:
            callback_url: Webhook URL for conversion completion notification (required)
            task_id: Original generation task ID (taskId) from generate_music (required)
            audio_id: Track ID (audioId) of the specific track to convert (required)

        Returns:
            Dictionary containing WAV conversion task information with taskId

        Raises:
            SunoAPIError: If the API request fails
            ValueError: If required parameters are missing or invalid

        Example:
            # Generate music and wait for completion
            music = await client.generate_music(prompt="Epic soundtrack", wait_audio=True)

            # Extract BOTH IDs (both required for WAV conversion)
            gen_task_id = music['data']['taskId']           # Generation job ID
            track_id = music['data']['sunoData'][0]['id']   # Specific track ID

            # Convert to WAV (requires both IDs)
            conversion = await client.convert_to_wav(
                callback_url="https://example.com/webhook",
                task_id=gen_task_id,
                audio_id=track_id
            )
        """
        if not callback_url:
            raise ValueError("callback_url is required for WAV conversion")

        if not task_id:
            raise ValueError("task_id is required for WAV conversion (generation job ID)")

        if not audio_id:
            raise ValueError("audio_id is required for WAV conversion (specific track ID)")

        # Validate callback_url format
        if callback_url:
            parsed = urlparse(callback_url)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError(
                    f"Invalid callback_url format: '{callback_url}'. "
                    "Must be a valid URL like 'https://example.com/webhook'"
                )
            if parsed.scheme not in ['http', 'https']:
                raise ValueError(
                    f"Invalid callback_url scheme: '{parsed.scheme}'. "
                    "Must use http:// or https://"
                )

        # Validate audio_id format (should be UUID)
        if audio_id:
            # UUID format: 8-4-4-4-12 hex characters
            uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
            if not uuid_pattern.match(audio_id):
                raise ValueError(
                    f"Invalid audio_id format: '{audio_id}'. "
                    f"Expected UUID format like '7752c889-3601-4e55-b805-54a28a53de85'. "
                    f"This is the track's 'id' field from sunoData array, NOT the generation taskId. "
                    f"If you have a taskId (hex string without dashes), use the task_id parameter instead."
                )

        # Validate task_id format (should be hex string without dashes, or could have dashes)
        # Task IDs are typically hex strings (with or without dashes)
        # If user accidentally passes a UUID here, warn them
        uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
        if uuid_pattern.match(task_id):
            raise ValueError(
                f"Possible parameter error: task_id '{task_id}' looks like a UUID (track ID). "
                f"task_id should be the generation job ID (hex string), not a track UUID. "
                f"Check that you're using task_id from music['data']['taskId'], not from sunoData[]['id']"
            )

        # Build payload - BOTH IDs are required per API documentation
        payload: Dict[str, Any] = {
            "callBackUrl": callback_url,
            "taskId": task_id,
            "audioId": audio_id
        }

        try:
            response = await self.client.post("/api/v1/wav/generate", json=payload)
            response.raise_for_status()
            result = response.json()

            # Check for API-level errors (Suno returns HTTP 200 with error codes in JSON)
            if isinstance(result, dict):
                code = result.get("code")

                # 409 = WAV already exists - this is informational, not an error
                if code == 409:
                    # WAV already exists - provide helpful message with the original conversion task ID
                    # Note: We don't have the original conversion task ID, so user needs to retrieve it
                    raise SunoAPIError(
                        f"WAV conversion already exists for this track (code 409). "
                        f"The track audio_id '{audio_id}' has already been converted to WAV. "
                        f"To retrieve the WAV download URL, you need the original conversion task_id. "
                        f"If you don't have it, you may need to track conversion task IDs when creating conversions. "
                        f"Note: The Suno API does not provide a way to query WAV status by audio_id alone."
                    )
                elif code != 200:
                    error_msg = result.get("msg", "Unknown error")
                    raise SunoAPIError(f"API Error (code {code}): {error_msg}")

            return result
        except httpx.HTTPError as e:
            raise SunoAPIError(f"Failed to convert to WAV: {str(e)}")

    async def get_wav_conversion_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get status of a WAV conversion task using taskId.

        Args:
            task_id: Task ID returned from convert_to_wav

        Returns:
            Dictionary containing WAV conversion status and download information

        Raises:
            SunoAPIError: If the API request fails
            ValueError: If task_id is missing
        """
        if not task_id:
            raise ValueError("task_id is required to check WAV conversion status")

        try:
            response = await self.client.get(
                "/api/v1/wav/record-info",
                params={"taskId": task_id}
            )
            response.raise_for_status()
            result = response.json()

            # Check for API-level errors
            if isinstance(result, dict) and result.get("code") != 200:
                error_msg = result.get("msg", "Unknown error")
                raise SunoAPIError(f"API Error (code {result.get('code')}): {error_msg}")

            return result
        except httpx.HTTPError as e:
            raise SunoAPIError(f"Failed to get WAV conversion status: {str(e)}")
