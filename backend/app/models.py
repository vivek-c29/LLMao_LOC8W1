import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey,
    Text, JSON, Enum as SAEnum, Boolean
)
from sqlalchemy.orm import relationship
from app.database import Base


class UserRole(str, enum.Enum):
    client = "client"
    worker = "worker"


class JobStatus(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    phone = Column(String(20), unique=True, nullable=False)
    role = Column(SAEnum(UserRole), nullable=False, default=UserRole.client)
    preferred_language = Column(String(10), default="en")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    jobs_posted = relationship("Job", back_populates="client", foreign_keys="Job.client_id")
    bids = relationship("Bid", back_populates="worker")
    reviews_given = relationship("Review", back_populates="reviewer", foreign_keys="Review.reviewer_id")
    reviews_received = relationship("Review", back_populates="worker", foreign_keys="Review.worker_id")
    work_history = relationship("WorkHistory", back_populates="worker")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(256), nullable=False)
    description = Column(Text, nullable=False)
    image_url = Column(String(512))
    ai_summary = Column(JSON)          # {summary, parts_list, severity}
    status = Column(SAEnum(JobStatus), default=JobStatus.open)
    location = Column(String(256))
    budget = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    client = relationship("User", back_populates="jobs_posted", foreign_keys=[client_id])
    bids = relationship("Bid", back_populates="job")


class Bid(Base):
    __tablename__ = "bids"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    worker_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    message = Column(Text)
    is_accepted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("Job", back_populates="bids")
    worker = relationship("User", back_populates="bids")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    worker_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Float, nullable=False)  # 1.0 – 5.0
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    reviewer = relationship("User", foreign_keys=[reviewer_id], back_populates="reviews_given")
    worker = relationship("User", foreign_keys=[worker_id], back_populates="reviews_received")


class WorkHistory(Base):
    __tablename__ = "work_history"

    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    completed_at = Column(DateTime, default=datetime.utcnow)
    earnings = Column(Float, nullable=False)

    worker = relationship("User", back_populates="work_history")
