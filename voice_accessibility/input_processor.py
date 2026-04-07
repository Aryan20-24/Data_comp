"""
input_processor.py
------------------
Handles all input logic: voice or text -> English text for RAG.

One function: process_input(user_input, input_mode, input_lang, fast_mode)

Cases:
1. input_mode="text"  + input_lang="en-IN"         -> pass through
2. input_mode="text"  + input_lang!="en-IN"         -> IndicTrans2
3. input_mode="voice" + fast_mode=True               -> Saarika (translate)
4. input_mode="voice" + fast_mode=False              -> Saarika (transcribe) + IndicTrans2

Returns: str (always English text)
"""

from .stt import speech_to_text
from .translate import translate


def process_input(
    user_input,
    input_mode: str = "text",
    input_lang: str = "en-IN",
    fast_mode: bool = True,
) -> str:
    """
    Process user input into English text ready for the RAG pipeline.

    Parameters
    ----------
    user_input : str or bytes
        If input_mode="text"  -> str (the typed text)
        If input_mode="voice" -> bytes (raw audio WAV bytes)
    input_mode : str
        "text" or "voice"
    input_lang : str
        Language code of the user's input (e.g., "hi-IN", "en-IN").
    fast_mode : bool
        Only used when input_mode="voice".
        True  = Saarika translate mode (voice -> English in one step)
        False = Saarika transcribe + IndicTrans2 (two steps, more accurate)

    Returns
    -------
    str
        English text ready to be passed to the RAG pipeline.

    Raises
    ------
    ValueError
        If input_mode is invalid or user_input is empty.
    """

    # --- Validate ---
    if input_mode not in ("text", "voice"):
        raise ValueError(
            f"input_mode must be 'text' or 'voice', got '{input_mode}'"
        )

    if not user_input:
        raise ValueError("user_input is empty.")

    # -----------------------------------------------------------------
    # TEXT INPUT
    # -----------------------------------------------------------------
    if input_mode == "text":
        text = user_input.strip()

        # Case 1: Already English -> pass through
        if input_lang == "en-IN":
            return text

        # Case 2: Non-English text -> translate to English
        english_text = translate(text, source_lang=input_lang, target_lang="en-IN")
        return english_text

    # -----------------------------------------------------------------
    # VOICE INPUT
    # -----------------------------------------------------------------
    if input_mode == "voice":
        audio_bytes = user_input

        if fast_mode:
            # Case 3: Saarika translate mode -> English text directly
            english_text = speech_to_text(
                audio_bytes=audio_bytes,
                fast_mode=True,
                input_lang=input_lang,
            )
            return english_text

        else:
            # Case 4: Saarika transcribe -> native text -> IndicTrans2 -> English
            native_text = speech_to_text(
                audio_bytes=audio_bytes,
                fast_mode=False,
                input_lang=input_lang,
            )

            # If input was already English, no translation needed
            if input_lang == "en-IN":
                return native_text

            english_text = translate(
                native_text, source_lang=input_lang, target_lang="en-IN"
            )
            return english_text
