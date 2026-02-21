from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.models import *  # noqa: ensure models are registered
from app.routers import users, jobs, bids, reviews, ai, deals
from app.services.websocket_manager import ws_manager
from app.middleware.translation import TranslationMiddleware

app = FastAPI(
    title="LoC ANTI — AI Labour Platform",
    description="AI-powered platform connecting clients with local skilled workers.",
    version="1.0.0",
)

# ── CORS ─────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:4000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Translation Middleware ────────────────────────────────────────────
app.add_middleware(TranslationMiddleware)

# ── Routers ───────────────────────────────────────────────────────────
app.include_router(users.router)
app.include_router(jobs.router)
app.include_router(bids.router)
app.include_router(reviews.router)
app.include_router(ai.router)
app.include_router(deals.router)


# ── WebSocket endpoint ────────────────────────────────────────────────
@app.websocket("/ws/{worker_id}")
async def websocket_endpoint(websocket: WebSocket, worker_id: int):
    await ws_manager.connect(worker_id, websocket)
    try:
        while True:
            # Keep connection alive; client can send pings
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(worker_id)


# ── Health Check ─────────────────────────────────────────────────────
@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}


# ── DB Startup (fallback if alembic not available) ───────────────────
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
