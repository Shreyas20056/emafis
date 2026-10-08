import sys
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Add backend directory to sys.path
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from database import init_db
from api.analysis import router as analysis_router
from api.portfolio import router as portfolio_router
from api.auth import router as auth_router



@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[INFO] Starting EMAFIS API...")
    init_db()
    print("[OK] Database initialized")
    yield
    print("[INFO] EMAFIS API stopped")



app = FastAPI(
    title="EMAFIS - Explainable Multi-Agent Financial Intelligence System",
    description="Multi-Agent system with Dynamic Weighting, Adaptive Learning, Portfolio support and XAI",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(analysis_router)
app.include_router(portfolio_router)
app.include_router(auth_router)



@app.get("/")
def root():
    return {
        "service": "EMAFIS API",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
def health():
    return {"status": "ok", "service": "EMAFIS", "time": datetime.utcnow().isoformat()}


@app.get("/api/agent-performance")
def agent_performance():
    from core.learning import get_agent_performance
    return {
        "agent_performance": get_agent_performance(),
        "updated_at": datetime.utcnow().isoformat()
    }