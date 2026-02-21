import os
import uuid
from fastapi import APIRouter, UploadFile, File
from app.services.vision import analyze_image
from app.database.mongo import db

router = APIRouter(prefix="/scan", tags=["Scan"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/")
async def scan_image(file: UploadFile = File(...)):
    # 1️⃣ Save image
    file_ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    # 2️⃣ AI Vision Analysis
    ai_result = analyze_image(file_path)

    # 3️⃣ Save to MongoDB
    scan_data = {
        "image": filename,
        "result": ai_result
    }

    await db.scans.insert_one(scan_data)

    # 4️⃣ Response
    return {
        "status": "success",
        "scan_result": ai_result
    }