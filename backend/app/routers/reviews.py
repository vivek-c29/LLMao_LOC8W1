from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import Review
from app.schemas import ReviewCreate, ReviewOut, WorkerReviewStats
from typing import List

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("/", response_model=ReviewOut, status_code=201)
async def create_review(payload: ReviewCreate, db: AsyncSession = Depends(get_db)):
    review = Review(**payload.model_dump())
    db.add(review)
    await db.flush()
    await db.refresh(review)
    return review


@router.get("/worker/{worker_id}", response_model=List[ReviewOut])
async def get_worker_reviews(worker_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Review).where(Review.worker_id == worker_id).order_by(Review.created_at.desc())
    )
    return result.scalars().all()


@router.get("/worker/{worker_id}/stats", response_model=WorkerReviewStats)
async def get_worker_review_stats(worker_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(
        select(func.avg(Review.rating), func.count(Review.id))
        .where(Review.worker_id == worker_id)
    )
    row = res.one()
    avg_rating = float(row[0]) if row[0] else 0.0
    total = row[1]
    return WorkerReviewStats(worker_id=worker_id, average_rating=round(avg_rating, 2), total_reviews=total)
