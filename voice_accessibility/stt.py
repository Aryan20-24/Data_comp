"""
stt.py
------
Speech-to-Text using Sarvam Saarika API.

One function: speech_to_text(audio_bytes, fast_mode, input_lang)
- fast_mode=True  → Saarika mode="translate"   → returns English text directly
- fast_mode=False → Saarika mode="transcribe"  → returns text in original language

Returns: str (transcribed or translated text)
"""

import requests
from .config import SARVAM_STT_API_KEY, SARVAM_STT_URL, SARVAM_STT_MODEL

def speech_to_text(
    audio_bytes: bytes,
    fast_mode: bool = True,
    input_lang: str = "hi-IN",
    filename: str = "audio.wav",
) -> str:
    """
    Convert speech audio to text using Sarvam Saarika API.

    Parameters
    ----------
    audio_bytes : bytes
        Raw audio file bytes (WAV format recommended).
    fast_mode : bool
        True  = mode "translate"  → returns English text directly.
        False = mode "transcribe" → returns text in the spoken language.
    input_lang : str
        Language code of the spoken audio (e.g., "hi-IN", "ta-IN").
        Used by Saarika to improve recognition accuracy.
    filename : str
        Name for the audio file sent to the API. Default "audio.wav".

    Returns
    -------
    str
        The transcribed/translated text.

    Raises
    ------
    ValueError
        If API key is not set or audio_bytes is empty.
    RuntimeError
        If the API call fails.
    """

    # --- Validate inputs ---
    if not SARVAM_STT_API_KEY:
        raise ValueError(
            "SARVAM_STT_API_KEY is not set. Add it to your .env file."
        )

    if not audio_bytes:
        raise ValueError("audio_bytes is empty. Provide valid audio data.")

    # --- Determine mode ---
    mode = "translate" if fast_mode else "transcribe"

    # --- Build request ---
    headers = {
        "api-subscription-key": SARVAM_STT_API_KEY,
    }

    files = {
        "file": (filename, audio_bytes, "audio/wav"),
    }

    data = {
        "model": SARVAM_STT_MODEL,
        "mode": mode,
        "language_code": input_lang,
    }

    # --- Call Saarika API ---
    try:
        response = requests.post(
            SARVAM_STT_URL,
            headers=headers,
            files=files,
            data=data,
            timeout=120,
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Saarika STT API call failed: {e}") from e

    # --- Extract transcript ---
    result = response.json()
    transcript = result.get("transcript")

    if transcript is None:
        raise RuntimeError(
            f"Unexpected Saarika response (no transcript field): {result}"
        )

    return transcript.strip()