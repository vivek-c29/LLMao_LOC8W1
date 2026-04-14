from pydantic import BaseModel
from typing import Dict
from .common import MongoBaseModel, PyObjectId


class ScanCreate(BaseModel):
    job_id: PyObjectId
    image_url: str
    detected_problem: str
    suggested_worker_type: str
    urgency: float
    ai_result: Dict


class ScanDB(MongoBaseModel):
    job_id: PyObjectId
    image_url: str
    detected_problem: str
    suggested_worker_type: str
    urgency: float
    ai_result: Dict