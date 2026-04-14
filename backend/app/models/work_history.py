from datetime import datetime
from .common import MongoBaseModel, PyObjectId

class WorkHistoryDB(MongoBaseModel):
    worker_id: PyObjectId
    job_id: PyObjectId
    completed_at: datetime = datetime.utcnow()
    earnings: float
