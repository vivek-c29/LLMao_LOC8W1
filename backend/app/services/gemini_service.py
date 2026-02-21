import google.generativeai as genai
from app.config import get_settings

settings = get_settings()
genai.configure(api_key=settings.gemini_api_key)


def get_flash_model():
    return genai.GenerativeModel("gemini-3-flash-preview")


async def analyze_image_for_problem(image_bytes: bytes, mime_type: str, description: str) -> dict:
    """
    Send an image + description to Gemini and get back a structured JSON diagnostic.
    """
    model = get_flash_model()

    prompt = f"""
You are a skilled home-repair diagnostic AI assistant.

A client has uploaded an image and described their problem as: "{description}"

Analyze the image carefully and return ONLY valid JSON (no markdown, no explanation) in this exact format:
{{
  "summary": "<2-3 sentence plain-language description of the problem>",
  "severity": "<one of: low | medium | high>",
  "parts_list": ["<part 1>", "<part 2>", "..."],
  "estimated_cost_inr": "<rough cost range in INR, e.g. ₹200–₹800>"
}}
"""
    image_part = {"mime_type": mime_type, "data": image_bytes}
    response = model.generate_content([prompt, image_part])

    raw = response.text.strip()
    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    import json
    return json.loads(raw)


async def translate_text(text: str, target_language: str) -> str:
    """Translate a piece of text to the target language using Gemini."""
    if target_language == "en":
        return text

    lang_map = {
        "hi": "Hindi",
        "mr": "Marathi",
        "te": "Telugu",
    }
    lang_name = lang_map.get(target_language, target_language)

    model = get_flash_model()
    prompt = (
        f"Translate the following text to {lang_name}. "
        f"Return ONLY the translated text, nothing else.\n\n{text}"
    )
    response = model.generate_content(prompt)
    return response.text.strip()
