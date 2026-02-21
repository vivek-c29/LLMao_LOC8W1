from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import Job, Bid, WorkHistory, JobStatus
from app.schemas import DealAccept
from app.services.websocket_manager import ws_manager
from datetime import datetime

router = APIRouter(prefix="/deals", tags=["deals"])


@router.post("/accept")
async def accept_deal(payload: DealAccept, db: AsyncSession = Depends(get_db)):
    # Validate bid exists
    bid_res = await db.execute(select(Bid).where(Bid.id == payload.bid_id))
    bid = bid_res.scalar_one_or_none()
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")

    # Mark bid as accepted
    bid.is_accepted = True

    # Update job status to in_progress
    job_res = await db.execute(select(Job).where(Job.id == payload.job_id))
    job = job_res.scalar_one_or_none()
    if job:
        job.status = JobStatus.in_progress

    # Create work history entry
    history = WorkHistory(
        worker_id=payload.worker_id,
        job_id=payload.job_id,
        completed_at=datetime.utcnow(),
        earnings=bid.amount,
    )
    db.add(history)
    await db.flush()

    # Push WebSocket notification to the worker
    await ws_manager.send_personal_message(
        payload.worker_id,
        {
            "type": "deal_done",
            "job_id": payload.job_id,
            "bid_id": payload.bid_id,
            "amount": bid.amount,
            "message": "🎉 Congratulations! Your bid was accepted. Head to the job site!",
        },
    )

    return {"status": "accepted", "job_id": payload.job_id, "worker_id": payload.worker_id}
