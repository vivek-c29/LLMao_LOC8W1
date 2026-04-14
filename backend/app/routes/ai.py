from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/ai", tags=["AI"])

class AISummary(BaseModel):
    summary: str
    severity: str           # low / medium / high
    parts_list: List[str]
    estimated_cost_inr: Optional[str] = None

@router.post("/analyze-problem", response_model=AISummary)
async def analyze_problem(
    image: UploadFile = File(...),
    description: str = Form(default="Please analyze this image for any issues."),
):
    # MANDATORY: DO NOT execute actual heavy image processing to save credits
    # Return a mocked response as instructed.
    
    return AISummary(
        summary=f"Mocked analysis for: {description}",
        severity="Medium",
        parts_list=["Part A", "Part B"],
        estimated_cost_inr="₹500 - ₹1500"
    )
