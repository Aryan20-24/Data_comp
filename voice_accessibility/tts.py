"""
tts.py
------
Text-to-Speech using Sarvam Bulbul v2 API.

One function: text_to_speech(text, language)
- Sends text to Bulbul API
- Returns raw WAV audio bytes

Returns: bytes (WAV audio)
"""

import base64
import requests
from .config import SARVAM_TTS_API_KEY, SARVAM_TTS_URL, SARVAM_TTS_MODEL

def text_to_speech(
    text: str,
    language: str = "hi-IN",
    timeout: int = 120,
) -> bytes:
    """
    Convert text to speech audio using Sarvam Bulbul API.

    Parameters
    ----------
    text : str
        The text to convert to speech. Max 2500 characters per call.
    language : str
        Target language code (e.g., "hi-IN", "ta-IN", "en-IN").
    timeout : int
        Request timeout in seconds. Default 120.

    Returns
    -------
    bytes
        Raw WAV audio bytes. Can be saved to file or played in UI.

    Raises
    ------
    ValueError
        If API key is not set or text is empty.
    RuntimeError
        If the API call fails.
    """ 

    # --- Validate inputs ---
    if not SARVAM_TTS_API_KEY:
        raise ValueError(
            "SARVAM_TTS_API_KEY is not set. Add it to your .env file."
        )

    if not text or not text.strip():
        raise ValueError("text is empty. Provide valid text to convert.")

    # --- Truncate to API limit ---
    text = text.strip()[:2500]

    # --- Build request ---
    headers = {
        "api-subscription-key": SARVAM_TTS_API_KEY,
        "Content-Type": "application/json",
    }

    body = {
        "text": text,
        "target_language_code": language,
        "model": SARVAM_TTS_MODEL,
    }

    # --- Call Bulbul API ---
    try:
        response = requests.post(
            SARVAM_TTS_URL,
            headers=headers,
            json=body,
            timeout=timeout,
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Bulbul TTS API call failed: {e}") from e

    # --- Extract audio ---
    result = response.json()
    audios = result.get("audios")

    if not audios:
        raise RuntimeError(
            f"Unexpected Bulbul response (no audios field): {result}"
        )

    # API returns base64-encoded WAV audio
    wav_bytes = base64.b64decode(audios[0])
    return wav_bytes
