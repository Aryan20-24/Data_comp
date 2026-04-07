"""
translate.py
------------
Translation using IndicTrans2 (AI4Bharat).
Runs locally on CPU. No API calls.

One function: translate(text, source_lang, target_lang)
- Loads the model ONCE at first call, reuses for all subsequent calls.
- If source_lang == target_lang, returns text as-is (no work done).

Uses two models:
- indic-en  : for translating any Indian language to English
- en-indic  : for translating English to any Indian language

Returns: str (translated text)
"""

from .config import INDICTRANS2_LANG_MAP

# ---------------------------------------------------------------------------
# Model cache - loaded once, reused forever
# ---------------------------------------------------------------------------
_indic_en_model = None
_indic_en_tokenizer = None
_en_indic_model = None
_en_indic_tokenizer = None


def _load_indic_en():
    """Load IndicTrans2 Indic to English model (first call only)."""
    global _indic_en_model, _indic_en_tokenizer
    if _indic_en_model is not None:
        return _indic_en_model, _indic_en_tokenizer

    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

    model_name = "ai4bharat/indictrans2-indic-en-dist-200M"
    _indic_en_tokenizer = AutoTokenizer.from_pretrained(
        model_name, trust_remote_code=True
    )
    _indic_en_model = AutoModelForSeq2SeqLM.from_pretrained(
        model_name, trust_remote_code=True
    )
    return _indic_en_model, _indic_en_tokenizer


def _load_en_indic():
    """Load IndicTrans2 English to Indic model (first call only)."""
    global _en_indic_model, _en_indic_tokenizer
    if _en_indic_model is not None:
        return _en_indic_model, _en_indic_tokenizer

    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

    model_name = "ai4bharat/indictrans2-en-indic-dist-200M"
    _en_indic_tokenizer = AutoTokenizer.from_pretrained(
        model_name, trust_remote_code=True
    )
    _en_indic_model = AutoModelForSeq2SeqLM.from_pretrained(
        model_name, trust_remote_code=True
    )
    return _en_indic_model, _en_indic_tokenizer


def translate(
    text: str,
    source_lang: str,
    target_lang: str,
) -> str:
    """
    Translate text between English and Indian languages using IndicTrans2.

    Parameters
    ----------
    text : str
        Text to translate.
    source_lang : str
        Language code of the input text (e.g., "hi-IN", "en-IN").
    target_lang : str
        Language code of the desired output (e.g., "en-IN", "ta-IN").

    Returns
    -------
    str
        Translated text.

    Raises
    ------
    ValueError
        If text is empty or language codes are not supported.
    """

    # --- No work needed ---
    if source_lang == target_lang:
        return text

    if not text or not text.strip():
        raise ValueError("text is empty. Provide valid text to translate.")

    # --- Map to IndicTrans2 language codes ---
    src_code = INDICTRANS2_LANG_MAP.get(source_lang)
    tgt_code = INDICTRANS2_LANG_MAP.get(target_lang)

    if src_code is None:
        raise ValueError(
            f"source_lang '{source_lang}' is not supported. "
            f"Supported: {list(INDICTRANS2_LANG_MAP.keys())}"
        )
    if tgt_code is None:
        raise ValueError(
            f"target_lang '{target_lang}' is not supported. "
            f"Supported: {list(INDICTRANS2_LANG_MAP.keys())}"
        )

    # --- Pick the right model ---
    if source_lang == "en-IN":
        # English to Indic
        model, tokenizer = _load_en_indic()
    elif target_lang == "en-IN":
        # Indic to English
        model, tokenizer = _load_indic_en()
    else:
        # Indic to Indic: go through English as pivot
        # Step 1: source to English
        english_text = translate(text, source_lang, "en-IN")
        # Step 2: English to target
        return translate(english_text, "en-IN", target_lang)

    # --- Tokenize and translate ---
    inputs = tokenizer(
        text,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=512,
    )

    generated = model.generate(
        **inputs,
        forced_bos_token_id=tokenizer.convert_tokens_to_ids(tgt_code),
        max_length=512,
    )

    translated = tokenizer.decode(generated[0], skip_special_tokens=True)
    return translated.strip()