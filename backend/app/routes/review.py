from fastapi import APIRouter, HTTPException, Body, Depends
from app.models.review import ReviewDB, ReviewCreate
from app.database.mongo import reviews_collection, workers_collection, jobs_collection
from app.utils.dependencies import require_role
from bson import ObjectId
from typing import List

router = APIRouter(prefix="/reviews", tags=["Reviews"])

@router.post("/")
async def create_review(
    payload: ReviewCreate,
    current_user: dict = Depends(require_role("client"))
):
    if str(payload.client_id) != current_user["id"]:
        raise HTTPException(status_code=403, detail="client_id mismatch with token")
        
    job = await jobs_collection.find_one({"_id": ObjectId(payload.job_id)})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    if str(job.get("client_id")) != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized to review this job")

    # 1. Save review
    review_obj = ReviewDB(**payload.model_dump())
    result = await reviews_collection.insert_one(review_obj.model_dump(by_alias=True))
    
    # 2. Update worker stats: average rating and total_jobs (using Project B logic)
    # Project B uses aggregation for stats, but Project A stores them directly in Worker model
    # We will recalculate and update
    worker_id = payload.worker_id
    
    pipeline = [
        {"$match": {"worker_id": ObjectId(worker_id)}},
        {"$group": {
            "_id": "$worker_id",
            "avg_rating": {"$avg": "$rating"},
            "total_reviews": {"$sum": 1}
        }}
    ]
    stats_cursor = reviews_collection.aggregate(pipeline)
    stats_list = await stats_cursor.to_list(length=1)
    
    if stats_list:
        avg_rating = stats_list[0]["avg_rating"]
        # Update worker directly
        await workers_collection.update_one(
            {"_id": ObjectId(worker_id)},
            {"$set": {"rating": round(avg_rating, 2)}}
        )

    return {
        "status": "success",
        "review_id": str(result.inserted_id)
    }

@router.get("/worker/{worker_id}")
async def get_worker_reviews(worker_id: str):
    reviews = await reviews_collection.find({"worker_id": ObjectId(worker_id)}).to_list(length=100)
    for r in reviews:
        r["_id"] = str(r["_id"])
        r["job_id"] = str(r["job_id"])
        r["worker_id"] = str(r["worker_id"])
        r["client_id"] = str(r.get("client_id", r.get("reviewer_id")))
    return reviews

@router.get("/worker/{worker_id}/stats")
async def get_worker_review_stats(worker_id: str):
    worker = await workers_collection.find_one({"_id": ObjectId(worker_id)})
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
        
    return {
        "worker_id": worker_id,
        "average_rating": worker.get("rating", 0.0),
        "total_jobs_completed": worker.get("total_jobs_completed", 0),
        "total_earnings": worker.get("total_earnings", 0.0)
    }
