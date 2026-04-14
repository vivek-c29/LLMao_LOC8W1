from fastapi import APIRouter, HTTPException, Body, Depends
from app.models.job import JobDB, Location
from app.services.vision import analyze_text
from app.utils.matching import match_workers
from app.database.mongo import jobs_collection, workers_collection, users_collection
from app.utils.dependencies import require_role
from bson import ObjectId

router = APIRouter(prefix="/job", tags=["Job"])


@router.post("/")
async def create_job(
    client_id: str = Body(...),
    input_text: str = Body(...),
    lat: float = Body(...),
    lng: float = Body(...),
    language: str = Body("en"),
    current_user: dict = Depends(require_role("client"))
):
    if current_user["id"] != client_id:
        raise HTTPException(status_code=403, detail="client_id mismatch with token")
    try:
        # 1. AI Analysis of text
        analysis = analyze_text(input_text)
        
        urgency_str = analysis.get("urgency", "Medium").lower()
        urgency_map = {"low": 3.0, "medium": 5.0, "high": 8.0}
        urgency_val = urgency_map.get(urgency_str, 5.0)

        # 2. Create Job object
        job_obj = JobDB(
            client_id=ObjectId(client_id),
            input_type="text",
            input_ref=input_text,
            skill_required=analysis.get("skill", "general"),
            problem=analysis.get("problem", input_text),
            problem_type=analysis.get("skill", "general"),
            description=input_text,
            urgency=urgency_val,
            location=Location(lat=lat, lng=lng),
            language=language or "en",
            status="posted"
        )

        # 3. Save to DB
        result = await jobs_collection.insert_one(job_obj.model_dump(by_alias=True))
        
        return {
            "status": "success",
            "job_id": str(result.inserted_id),
            "analysis": analysis
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{job_id}/matches")
async def get_job_matches(job_id: str):
    try:
        # 1. Fetch the job - check both string and ObjectId to be safe
        job = await jobs_collection.find_one({"_id": job_id})
        if not job:
            if ObjectId.is_valid(job_id):
                job = await jobs_collection.find_one({"_id": ObjectId(job_id)})
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        job_location = job.get("location")
        required_skill = job.get("skill_required")


        # 2. Fetch all workers
        workers_cursor = workers_collection.find({})
        workers = await workers_cursor.to_list(length=100)
        
        if not workers:
            return {"status": "success", "matches": []}

        # 3. Resolve worker names from users collection
        for worker in workers:
            w_user_id = worker.get("user_id")
            user = await users_collection.find_one({"_id": w_user_id})
            if not user and isinstance(w_user_id, str) and ObjectId.is_valid(w_user_id):
                user = await users_collection.find_one({"_id": ObjectId(w_user_id)})
            
            if user:
                worker["name"] = user.get("name", "Unknown")
            else:
                worker["name"] = "Unknown"


        # 4. Use the matching utility
        results = match_workers(job_location, required_skill, workers)

        return {
            "status": "success",
            "job_id": job_id,
            "required_skill": required_skill,
            "matches": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{job_id}/accept")
async def accept_job(
    job_id: str,
    worker_id: str = Body(...),
    quoted_price: float = Body(None),
    current_user: dict = Depends(require_role("worker"))
):
    if current_user["id"] != worker_id:
        raise HTTPException(status_code=403, detail="worker_id mismatch with token")
    try:
        job = await jobs_collection.find_one({"_id": ObjectId(job_id)})
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        update_data = {
            "status": "accepted",
            "worker_id": ObjectId(worker_id)
        }
        if quoted_price is not None:
            update_data["quoted_price"] = quoted_price

        await jobs_collection.update_one(
            {"_id": ObjectId(job_id)},
            {"$set": update_data}
        )

        # Notify client via logic or WS later
        return {"status": "success", "message": "Job accepted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{job_id}/start")
async def start_job(
    job_id: str,
    current_user: dict = Depends(require_role("worker"))
):
    job = await jobs_collection.find_one({"_id": ObjectId(job_id)})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if str(job.get("worker_id")) != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized to start this job")
    
    result = await jobs_collection.update_one(
        {"_id": ObjectId(job_id)},
        {"$set": {"status": "in_progress"}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"status": "success", "message": "Job marked as in-progress"}


@router.post("/{job_id}/complete")
async def complete_job(
    job_id: str, 
    earnings: float = Body(...),
    current_user: dict = Depends(require_role("worker"))
):
    try:
        job = await jobs_collection.find_one({"_id": ObjectId(job_id)})
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        worker_id = job.get("worker_id")
        if not worker_id:
            raise HTTPException(status_code=400, detail="No worker assigned to this job")
        if str(worker_id) != current_user["id"]:
            raise HTTPException(status_code=403, detail="Not authorized to complete this job")

        # 1. Update job status
        await jobs_collection.update_one(
            {"_id": ObjectId(job_id)},
            {"$set": {"status": "completed"}}
        )

        # 2. Add to Work History
        from app.models.work_history import WorkHistoryDB
        from datetime import datetime
        work_history = WorkHistoryDB(
            worker_id=worker_id,
            job_id=ObjectId(job_id),
            earnings=earnings,
            completed_at=datetime.utcnow()
        )
        from app.database.mongo import work_history_collection
        await work_history_collection.insert_one(work_history.model_dump(by_alias=True))

        # 3. Update worker earnings and total jobs
        await workers_collection.update_one(
            {"_id": worker_id},
            {
                "$inc": {
                    "total_earnings": earnings,
                    "total_jobs_completed": 1
                }
            }
        )

        return {"status": "success", "message": "Job completed and earnings tracked"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{job_id}/cancel")
async def cancel_job(job_id: str):
    result = await jobs_collection.update_one(
        {"_id": ObjectId(job_id)},
        {"$set": {"status": "cancelled"}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"status": "success", "message": "Job cancelled"}
