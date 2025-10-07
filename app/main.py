from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.api import api_router
from app.websocket.connection_manager import ConnectionManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    pass


app = FastAPI(
    title="Elemental Circle Game API",
    description="A strategic card game with elemental combat system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for Flutter web
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# WebSocket connection manager
connection_manager = ConnectionManager()


@app.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    await connection_manager.connect(websocket, game_id)
    try:
        while True:
            data = await websocket.receive_text()
            await connection_manager.broadcast_to_game(game_id, data)
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, game_id)


@app.get("/")
async def root():
    return {"message": "Elemental Circle Game API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )



