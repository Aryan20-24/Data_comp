"""
output_processor.py
-------------------
Handles all output logic: English RAG answer -> desired format for user.

One function: process_output(english_text, output_mode, output_lang)

Cases:
1. output_mode="text"  + output_lang="en-IN"        -> pass through
2. output_mode="text"  + output_lang!="en-IN"        -> IndicTrans2
3. output_mode="voice" + output_lang="en-IN"         -> Bulbul TTS
4. output_mode="voice" + output_lang!="en-IN"        -> IndicTrans2 + Bulbul TTS

Returns: dict {"text": str, "audio": bytes or None}
"""

from .translate import translate
from .tts import text_to_speech

def process_output(
    english_text: str,
    output_mode: str = "text",
    output_lang: str = "en-IN",
) -> dict:
    """
    Process RAG pipeline's English answer into the user's desired format.

    Parameters
    ----------
    english_text : str
        The English text answer from the RAG pipeline.
    output_mode : str
        "text" or "voice"
    output_lang : str
        Language code of the desired output (e.g., "hi-IN", "en-IN").

    Returns
    -------
    dict
        {
            "text": str,         # The final text (translated if needed)
            "audio": bytes|None  # WAV audio bytes if voice, None if text only
        }

    Raises
    ------
    ValueError
        If output_mode is invalid or english_text is empty.
    """

    # --- Validate ---
    if output_mode not in ("text", "voice"):
        raise ValueError(
            f"output_mode must be 'text' or 'voice', got '{output_mode}'"
        )

    if not english_text or not english_text.strip():
        raise ValueError("english_text is empty.")

    english_text = english_text.strip()

    # -----------------------------------------------------------------
    # Determine the final text (translate if needed)
    # -----------------------------------------------------------------
    if output_lang == "en-IN":
        final_text = english_text
    else:
        final_text = translate(
            english_text, source_lang="en-IN", target_lang=output_lang
        )

    # -----------------------------------------------------------------
    # TEXT OUTPUT
    # -----------------------------------------------------------------
    if output_mode == "text":
        return {
            "text": final_text,
            "audio": None,
        }

    # -----------------------------------------------------------------
    # VOICE OUTPUT
    # -----------------------------------------------------------------
    if output_mode == "voice":
        audio_bytes = text_to_speech(
            text=final_text,
            language=output_lang,
        )
        return {
            "text": final_text,
            "audio": audio_bytes,
        }