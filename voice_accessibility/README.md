# Voice Accessibility Module

This module converts multilingual user input into English for RAG and converts English RAG output back into user-preferred text or voice.

It supports:
- Input mode: `text` or `voice`
- Output mode: `text` or `voice`
- Translation via IndicTrans2
- Speech-to-text via Sarvam Saarika
- Text-to-speech via Sarvam Bulbul

---

## Folder Structure

```text
voice_accessibility/
├── .env
├── __init__.py
├── config.py
├── stt.py
├── tts.py
├── translate.py
├── input_processor.py
└── output_processor.py
```

---

## What Each File Does

### `config.py`
Central configuration:
- API keys (loaded from `.env`)
- API endpoints
- model names
- user-facing runtime variables (`input_mode`, `output_mode`, `input_lang`, `output_lang`, `fast_mode`)
- supported languages
- Sarvam-to-IndicTrans2 language code mapping

### `stt.py`
Speech-to-text wrapper for Sarvam Saarika.
- `fast_mode=True` -> Saarika `mode="translate"` -> direct English text
- `fast_mode=False` -> Saarika `mode="transcribe"` -> native-language text

### `translate.py`
Local translation using IndicTrans2.
- English <-> Indic translation
- model caching for performance
- Indic -> Indic handled via English pivot

### `tts.py`
Text-to-speech wrapper for Sarvam Bulbul.
- Converts final text into WAV audio bytes

### `input_processor.py`
Normalizes user input to **English text** before RAG.

### `output_processor.py`
Converts English RAG output into requested output language and mode.

### `__init__.py`
Exports:
- `process_input`
- `process_output`

---

## Environment Setup (`.env`)

Create `voice_accessibility/.env`:

```env
SARVAM_STT_API_KEY=your_saarika_api_key_here
SARVAM_TTS_API_KEY=your_bulbul_api_key_here
```

---

## Runtime Variables (UI should set these)

- `input_mode`: `"text"` or `"voice"`
- `output_mode`: `"text"` or `"voice"`
- `input_lang`: e.g. `"en-IN"`, `"hi-IN"`, `"ta-IN"`
- `output_lang`: e.g. `"en-IN"`, `"hi-IN"`, `"ta-IN"`
- `fast_mode`: `True` or `False`

These are meant to be controlled by your UI layer and passed into processor functions.

---

## Full Flow (Recommended)

1. Collect user input from UI
2. Call `process_input(...)` to get English text
3. Send English text to your RAG pipeline
4. Take English RAG response and call `process_output(...)`
5. Return text/audio to frontend

---

## Input Processing Cases

`process_input(user_input, input_mode, input_lang, fast_mode)`

### Case 1: Text input, English
- `input_mode="text"`
- `input_lang="en-IN"`
- Action: passthrough

### Case 2: Text input, non-English
- `input_mode="text"`
- `input_lang!="en-IN"`
- Action: IndicTrans2 translates to English

### Case 3: Voice input, fast mode
- `input_mode="voice"`
- `fast_mode=True`
- Action: Saarika `translate` mode directly returns English

### Case 4: Voice input, accurate mode
- `input_mode="voice"`
- `fast_mode=False`
- Action: Saarika `transcribe` -> native text -> IndicTrans2 -> English

Output of all cases: **English text**

---

## Output Processing Cases

`process_output(english_text, output_mode, output_lang)`

### Case 1: Text output, English
- `output_mode="text"`
- `output_lang="en-IN"`
- Action: passthrough text

### Case 2: Text output, non-English
- `output_mode="text"`
- `output_lang!="en-IN"`
- Action: IndicTrans2 translates English to target language

### Case 3: Voice output, English
- `output_mode="voice"`
- `output_lang="en-IN"`
- Action: Bulbul TTS on English text

### Case 4: Voice output, non-English
- `output_mode="voice"`
- `output_lang!="en-IN"`
- Action: IndicTrans2 (English -> target) + Bulbul TTS

Return shape:

```python
{
  "text": "...",
  "audio": b"..." or None
}
```

---

## Fast Mode vs Accurate Mode

- `fast_mode=True`
  - Lower latency
  - Single STT call (`translate`)
  - Good for quick conversational UX

- `fast_mode=False`
  - Better control/traceability
  - STT transcription + explicit translation
  - Better when debugging or when STT translation quality is inconsistent

---

## Function Signatures

```python
# input_processor.py
process_input(user_input, input_mode="text", input_lang="en-IN", fast_mode=True) -> str

# output_processor.py
process_output(english_text, output_mode="text", output_lang="en-IN") -> dict

# stt.py
speech_to_text(audio_bytes, fast_mode=True, input_lang="hi-IN", filename="audio.wav") -> str

# tts.py
text_to_speech(text, language="hi-IN", timeout=120) -> bytes

# translate.py
translate(text, source_lang, target_lang) -> str
```

---

## RAG Integration Example

```python
from voice_accessibility import process_input, process_output

# Values usually come from UI controls
input_mode = "voice"
output_mode = "voice"
input_lang = "hi-IN"
output_lang = "ta-IN"
fast_mode = True

# user_input is either text (str) or audio bytes depending on input_mode
english_query = process_input(
    user_input=user_input,
    input_mode=input_mode,
    input_lang=input_lang,
    fast_mode=fast_mode,
)

# Your existing RAG pipeline (expects English)
english_answer = rag_pipeline(english_query)

# Convert to desired user output
result = process_output(
    english_text=english_answer,
    output_mode=output_mode,
    output_lang=output_lang,
)

final_text = result["text"]
final_audio = result["audio"]  # None if output_mode="text"
```

---

## UI Binding Guidance

Bind UI controls directly to:
- `input_mode`
- `output_mode`
- `input_lang`
- `output_lang`
- `fast_mode`

Then pass those values into `process_input` and `process_output` without changing business logic.

---

## Error Handling Notes

- Missing API keys -> clear `ValueError`
- Empty text/audio -> clear `ValueError`
- API/network failures -> `RuntimeError`
- Unsupported language code -> `ValueError`

Recommended: wrap processor calls in app-level try/except and show user-friendly messages in UI.

---

## Best Practices

1. Keep RAG core strictly English for consistency.
2. Always perform language conversion at the boundaries (input/output processors).
3. Prefer `fast_mode=True` for production chat UX unless quality needs otherwise.
4. Cache/warm up IndicTrans2 models at app start if low latency is important.
5. Log `input_mode`, `output_mode`, languages, and latency for observability.

---

## Minimal Import for Teammates

```python
from voice_accessibility import process_input, process_output
```

This is the only interface needed by downstream pipeline code.