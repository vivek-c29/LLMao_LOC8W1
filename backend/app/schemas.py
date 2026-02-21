from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel
from app.models import UserRole, JobStatus


# ── User ─────────────────────────────────────────────────────────────
class UserCreate(BaseModel):
    name: str
    phone: str
    role: UserRole = UserRole.client
    preferred_language: str = "en"


class UserOut(BaseModel):
    id: int
    name: str
    phone: str
    role: UserRole
    preferred_language: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Job ──────────────────────────────────────────────────────────────
class JobCreate(BaseModel):
    client_id: int
    title: str
    description: str
    image_url: Optional[str] = None
    location: Optional[str] = None
    budget: Optional[float] = None


class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[JobStatus] = None
    budget: Optional[float] = None


class JobOut(BaseModel):
    id: int
    client_id: int
    title: str
    description: str
    image_url: Optional[str]
    ai_summary: Optional[Any]
    status: JobStatus
    location: Optional[str]
    budget: Optional[float]
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Bid ──────────────────────────────────────────────────────────────
class BidCreate(BaseModel):
    job_id: int
    worker_id: int
    amount: float
    message: Optional[str] = None


class BidOut(BaseModel):
    id: int
    job_id: int
    worker_id: int
    amount: float
    message: Optional[str]
    is_accepted: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkerStats(BaseModel):
    worker_id: int
    total_bids: int
    total_jobs_completed: int
    total_earnings: float


# ── Review ───────────────────────────────────────────────────────────
class ReviewCreate(BaseModel):
    job_id: int
    reviewer_id: int
    worker_id: int
    rating: float
    comment: Optional[str] = None


class ReviewOut(BaseModel):
    id: int
    job_id: int
    reviewer_id: int
    worker_id: int
    rating: float
    comment: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkerReviewStats(BaseModel):
    worker_id: int
    average_rating: float
    total_reviews: int


# ── AI Diagnostic ─────────────────────────────────────────────────────
class AISummary(BaseModel):
    summary: str
    severity: str           # low / medium / high
    parts_list: list[str]
    estimated_cost_inr: Optional[str] = None


# ── Deal ─────────────────────────────────────────────────────────────
class DealAccept(BaseModel):
    job_id: int
    worker_id: int
    bid_id: int
