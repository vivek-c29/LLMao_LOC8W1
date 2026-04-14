import os
import uuid
from fastapi import APIRouter, UploadFile, File, Form
from app.services.vision import analyze_image
from app.database.mongo import scans_collection
from app.models.scan import ScanDB
from bson import ObjectId

router = APIRouter(prefix="/scan", tags=["Scan"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/")
async def scan_image(
    job_id: str = Form(...), 
    file: UploadFile = File(...)
):
    # 1️⃣ Save image
    file_ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    # 2️⃣ AI Vision Analysis
    ai_result = analyze_image(file_path)

    # 3️⃣ Validate and Save to MongoDB using ScanDB schema
    scan_obj = ScanDB(
        job_id=ObjectId(job_id),
        image_url=filename,
        detected_problem=ai_result.get("problem", "Unknown"),
        suggested_worker_type=ai_result.get("skill", "general"),
        urgency=5.0,
        ai_result=ai_result
    )

    await scans_collection.insert_one(scan_obj.model_dump(by_alias=True))

    # 4️⃣ Response
    return {
        "status": "success",
        "scan_data": scan_obj.model_dump(by_alias=True)
    }