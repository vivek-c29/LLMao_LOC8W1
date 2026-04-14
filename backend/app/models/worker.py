from pydantic import BaseModel
from typing import List
from .common import MongoBaseModel, PyObjectId
from .user import Location


class WorkerCreate(BaseModel):
    user_id: PyObjectId
    skills: List[str]
    experience_years: int
    availability: bool = True
    verified: bool = False
    location: Location


class WorkerDB(MongoBaseModel):
    user_id: PyObjectId
    skills: List[str]
    rating: float = 0.0
    total_jobs: int = 0
    total_earnings: float = 0.0
    total_jobs_completed: int = 0
    experience_years: int
    availability: bool = True
    verified: bool
    location: Location