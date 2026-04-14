from fastapi import FastAPI
from app.database.mongo import db
from app.routes import scan, job, review, ai, auth
from app.utils.websocket import manager
from fastapi import WebSocket, WebSocketDisconnect

app = FastAPI(title="Sahayak API")

app.include_router(scan.router)
app.include_router(job.router)
app.include_router(review.router)
app.include_router(ai.router)
app.include_router(auth.router)

@app.websocket("/ws/{worker_id}")
async def websocket_endpoint(websocket: WebSocket, worker_id: str):
    await manager.connect(worker_id, websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(worker_id)

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
