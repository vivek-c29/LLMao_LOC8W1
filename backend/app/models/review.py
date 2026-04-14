from pydantic import BaseModel
from .common import MongoBaseModel, PyObjectId

class ReviewCreate(BaseModel):
    job_id: PyObjectId
    client_id: PyObjectId
    worker_id: PyObjectId
    rating: int
    comment: str

class ReviewDB(MongoBaseModel):
    job_id: PyObjectId
    client_id: PyObjectId
    worker_id: PyObjectId
    rating: int
    comment: str