import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = genai.GenerativeModel("gemini-3-flash-preview")

SYSTEM_PROMPT = """
You are a home repair expert AI.

Analyze the given image and classify the problem strictly into ONE of the following categories:
- plumber
- electrician
- carpenter
- painter
- mason
- general

Return ONLY valid JSON in the following format:
{
  "skill": "<category>",
  "problem": "<short description>",
  "urgency": "<Low | Medium | High>",
  "confidence": <number between 60 and 99>
}

Do not add any explanation outside JSON.
"""

def analyze_image(image_path: str):
    try:
        image = Image.open(image_path)

        response = MODEL.generate_content(
            [SYSTEM_PROMPT, image],
            generation_config={"temperature": 0.2}
        )

        text = response.text.strip()

        # Safety: ensure JSON only
        result = json.loads(text)

        allowed_skills = [
            "plumber", "electrician", "carpenter",
            "painter", "mason", "general"
        ]

        if result.get("skill") not in allowed_skills:
            result["skill"] = "general"

        return result

    except Exception as e:
        return {
            "skill": "general",
            "problem": "Unable to detect issue",
            "urgency": "Low",
            "confidence": 60,
            "error": str(e)
        }