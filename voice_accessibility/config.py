"""
config.py
---------
All user-configurable variables for the voice accessibility module.
These variables are placeholders — they will be set by the UI layer
or by the RAG pipeline code before calling process_input / process_output.
"""

import os
from dotenv import load_dotenv

# Load API keys from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# ---------------------------------------------------------------------------
# API Keys (loaded from .env file)
# ---------------------------------------------------------------------------
SARVAM_STT_API_KEY = os.getenv("SARVAM_STT_API_KEY", "")
SARVAM_TTS_API_KEY = os.getenv("SARVAM_TTS_API_KEY", "")

# ---------------------------------------------------------------------------
# Sarvam API Endpoints
# ---------------------------------------------------------------------------
SARVAM_STT_URL = "https://api.sarvam.ai/speech-to-text"
SARVAM_TTS_URL = "https://api.sarvam.ai/text-to-speech"

# ---------------------------------------------------------------------------
# Sarvam Model Versions
# ---------------------------------------------------------------------------
SARVAM_STT_MODEL = "saaras:v2"
SARVAM_TTS_MODEL = "bulbul:v2"

# ---------------------------------------------------------------------------
# User-Configurable Variables (set by UI before calling processors)
# ---------------------------------------------------------------------------

# "voice" or "text"
input_mode = "text"

# "voice" or "text"
output_mode = "text"

# Language code of user's input (e.g., "hi-IN", "ta-IN", "en-IN")
input_lang = "en-IN"

# Language code of desired output (e.g., "hi-IN", "ta-IN", "en-IN")
output_lang = "en-IN"

# True  = Saarika mode="translate" (voice → English text in one step)
# False = Saarika mode="transcribe" → IndicTrans2 (two steps, more accurate)
fast_mode = True

# ---------------------------------------------------------------------------
# Supported Languages
# ---------------------------------------------------------------------------
# Intersection of Sarvam (Bulbul/Saarika) and IndicTrans2 support.
# Use these codes when setting input_lang / output_lang.
#
# Format: "language_code": "Display Name"
# ---------------------------------------------------------------------------
SUPPORTED_LANGUAGES = {
    "en-IN": "English",
    "hi-IN": "Hindi",
    "ta-IN": "Tamil",
    "te-IN": "Telugu",
    "mr-IN": "Marathi",
    "bn-IN": "Bengali",
    "kn-IN": "Kannada",
    "ml-IN": "Malayalam",
    "gu-IN": "Gujarati",
    "pa-IN": "Punjabi",
    "od-IN": "Odia",
}

# ---------------------------------------------------------------------------
# IndicTrans2 language code mapping
# ---------------------------------------------------------------------------
# Sarvam uses "hi-IN" style codes, IndicTrans2 uses "hin_Deva" style codes.
# This map bridges them.
# ---------------------------------------------------------------------------
INDICTRANS2_LANG_MAP = {
    "en-IN": "eng_Latn",
    "hi-IN": "hin_Deva",
    "ta-IN": "tam_Taml",
    "te-IN": "tel_Telu",
    "mr-IN": "mar_Deva",
    "bn-IN": "ben_Beng",
    "kn-IN": "kan_Knda",
    "ml-IN": "mal_Mlym",
    "gu-IN": "guj_Gujr",
    "pa-IN": "pan_Guru",
    "od-IN": "ory_Orya",
}