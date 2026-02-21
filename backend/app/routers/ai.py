from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.schemas import AISummary
from app.services.gemini_service import analyze_image_for_problem

router = APIRouter(prefix="/ai", tags=["ai"])

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


@router.post("/analyze-problem", response_model=AISummary)
async def analyze_problem(
    image: UploadFile = File(...),
    description: str = Form(default="Please analyze this image for any issues."),
):
    if image.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported image type: {image.content_type}. Use JPEG, PNG, or WebP.",
        )

    image_bytes = await image.read()
    if len(image_bytes) > 10 * 1024 * 1024:  # 10 MB guard
        raise HTTPException(status_code=413, detail="Image too large. Max 10 MB.")

    try:
        result = await analyze_image_for_problem(image_bytes, image.content_type, description)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Gemini API error: {str(e)}")

    return AISummary(**result)