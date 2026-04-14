from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime
from .common import MongoBaseModel, PyObjectId
from .user import Location


class JobCreate(BaseModel):
    client_id: PyObjectId
    input_type: Literal["image", "text", "voice"]
    input_ref: str

    skill_required: str
    problem: str
    problem_type: str
    description: str
    urgency: float

    location: Location
    language: str = "en"


class JobDB(MongoBaseModel):
    client_id: PyObjectId
    input_type: str
    input_ref: str

    skill_required: str
    problem: str
    problem_type: str
    description: str
    urgency: float

    status: Literal["posted", "accepted", "in_progress", "completed", "cancelled"] = "posted"
    worker_id: Optional[PyObjectId] = None
    quoted_price: Optional[float] = None

    location: Location
    language: str = "en"
    updated_at: Optional[datetime] = None