from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import Bid, WorkHistory
from app.schemas import BidCreate, BidOut, WorkerStats
from typing import List, Optional

router = APIRouter(prefix="/bids", tags=["bids"])


@router.post("/", response_model=BidOut, status_code=201)
async def create_bid(payload: BidCreate, db: AsyncSession = Depends(get_db)):
    bid = Bid(**payload.model_dump())
    db.add(bid)
    await db.flush()
    await db.refresh(bid)
    return bid


@router.get("/", response_model=List[BidOut])
async def list_bids(
    job_id: Optional[int] = None,
    worker_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    q = select(Bid)
    if job_id:
        q = q.where(Bid.job_id == job_id)
    if worker_id:
        q = q.where(Bid.worker_id == worker_id)
    result = await db.execute(q.order_by(Bid.created_at.desc()))
    return result.scalars().all()


@router.get("/worker/{worker_id}/stats", response_model=WorkerStats)
async def get_worker_stats(worker_id: int, db: AsyncSession = Depends(get_db)):
    # Count all bids
    total_bids_res = await db.execute(
        select(func.count(Bid.id)).where(Bid.worker_id == worker_id)
    )
    total_bids = total_bids_res.scalar() or 0

    # Jobs completed + earnings from WorkHistory
    history_res = await db.execute(
        select(func.count(WorkHistory.id), func.coalesce(func.sum(WorkHistory.earnings), 0))
        .where(WorkHistory.worker_id == worker_id)
    )
    row = history_res.one()
    total_jobs_completed = row[0]
    total_earnings = float(row[1])

    return WorkerStats(
        worker_id=worker_id,
        total_bids=total_bids,
        total_jobs_completed=total_jobs_completed,
        total_earnings=total_earnings,
    )
