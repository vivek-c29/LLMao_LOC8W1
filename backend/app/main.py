from fastapi import FastAPI
from app.database.mongo import db
from app.routes import scan

app = FastAPI(title="Sahayak API")

app.include_router(scan.router)

@app.get("/")
def root():
    return {"message": "Sahayak backend running 🚀"}


@app.get("/test-db")
async def test_db():
    try:
        await db.command("ping")
        return {"status": "success", "message": "MongoDB connected ✅"}
    except Exception as e:
        return {"status": "failed", "error": str(e)}
