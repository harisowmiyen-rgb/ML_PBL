from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import settings
from backend.app.database.database import init_db
from backend.app.api.routes import router as general_router
from backend.app.api.scan import router as scan_router
from backend.app.api.reports import router as reports_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup
    init_db()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="High-performance backend detecting deceptive e-commerce UI/UX patterns using hybrid ML and heuristic analysis.",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "Dark Pattern Detector API",
        "status": "running"
    }

app.include_router(general_router, prefix=settings.API_PREFIX, tags=["System"])
app.include_router(scan_router, prefix=settings.API_PREFIX, tags=["Scanner"])
app.include_router(reports_router, prefix=settings.API_PREFIX, tags=["Reports & Feedback"])
