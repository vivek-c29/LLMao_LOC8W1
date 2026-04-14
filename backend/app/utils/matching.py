import math
from typing import List, Dict, Any

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # Convert decimal degrees to radians 
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r

def calculate_proximity_score(distance_km: float) -> int:
    """
    Convert distance into a proximity score based on a fixed scale.
    """
    if distance_km <= 2:
        return 5
    elif distance_km <= 5:
        return 4
    elif distance_km <= 10:
        return 3
    elif distance_km <= 20:
        return 2
    else:
        return 1

def match_workers(job_location: Dict[str, float], required_skill: str, workers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filters and ranks workers based on skill, distance, and rating.
    
    Args:
        job_location: Dict with 'lat' and 'lng'
        required_skill: The skill needed for the job
        workers: List of worker dicts/objects containing skills, rating, and location
    """
    matched_workers = []
    
    job_lat = job_location.get('lat')
    job_lng = job_location.get('lng')

    for worker in workers:
        # 1. Filter by required skill
        worker_skills = [s.lower() for s in worker.get('skills', [])]
        if required_skill.lower() not in worker_skills:
            continue

        # 2. Calculate distance
        worker_loc = worker.get('location', {})
        w_lat = worker_loc.get('lat')
        w_lng = worker_loc.get('lng')
        
        if w_lat is None or w_lng is None:
            continue

        distance = haversine_distance(job_lat, job_lng, w_lat, w_lng)

        # 3. Convert distance into proximity score
        proximity_score = calculate_proximity_score(distance)

        # 4. Compute final score
        # final_score = 0.6 * worker.rating + 0.4 * proximity_score
        rating = worker.get('rating', 0.0)
        final_score = (0.6 * rating) + (0.4 * proximity_score)

        # 5. Assemble result
        matched_workers.append({
            "worker_id": str(worker.get('user_id') or worker.get('_id') or worker.get('id')),
            "rating": rating,
            "distance_km": round(distance, 2),
            "proximity_score": proximity_score,
            "final_score": round(final_score, 2),
            "name": worker.get('name') # Adding name for better test visibility
        })

    # 6. Sort by final_score descending
    matched_workers.sort(key=lambda x: x['final_score'], reverse=True)

    return matched_workers
