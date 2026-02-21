import asyncio
import sys
import os
import random
from datetime import datetime

# Ensure project root is in sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from app.database import AsyncSessionLocal
from app.models import User, Job, Bid, Review, WorkHistory, UserRole, JobStatus

async def seed_fake_data():
    async with AsyncSessionLocal() as session:
        # Create fake users
        users = [
            User(name=f"Client {i}", phone=f"100000000{i}", role=UserRole.client, preferred_language="en") for i in range(1, 4)
        ] + [
            User(name=f"Worker {i}", phone=f"200000000{i}", role=UserRole.worker, preferred_language="en") for i in range(1, 4)
        ]
        session.add_all(users)
        await session.flush()

        # Create fake jobs
        jobs = [
            Job(
                client_id=users[0].id,
                title=f"Fix Plumbing {i}",
                description="Leaky faucet needs repair.",
                status=JobStatus.open,
                location="Mumbai",
                budget=random.uniform(500, 2000),
                created_at=datetime.utcnow()
            ) for i in range(1, 4)
        ]
        session.add_all(jobs)
        await session.flush()

        # Create fake bids
        bids = [
            Bid(
                job_id=jobs[i % 3].id,
                worker_id=users[3 + (i % 3)].id,
                amount=random.uniform(400, 1800),
                message="Ready to help!",
                is_accepted=(i == 0),
                created_at=datetime.utcnow()
            ) for i in range(3)
        ]
        session.add_all(bids)
        await session.flush()

        # Create fake reviews
        reviews = [
            Review(
                job_id=jobs[i % 3].id,
                reviewer_id=users[0].id,
                worker_id=users[3 + (i % 3)].id,
                rating=random.uniform(3.0, 5.0),
                comment="Great work!",
                created_at=datetime.utcnow()
            ) for i in range(3)
        ]
        session.add_all(reviews)
        await session.flush()

        # Create fake work history
        work_histories = [
            WorkHistory(
                worker_id=users[3 + (i % 3)].id,
                job_id=jobs[i % 3].id,
                completed_at=datetime.utcnow(),
                earnings=random.uniform(400, 1800)
            ) for i in range(3)
        ]
        session.add_all(work_histories)
        await session.commit()

if __name__ == "__main__":
    asyncio.run(seed_fake_data())
