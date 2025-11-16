"""
Main FastAPI application for Mock Interview AI System
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
import os

from app.config import settings
from app.database import create_tables, check_db_connection
from app.api import auth, resume, jobs, interview, dashboard

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("🚀 Starting Mock Interview AI System...")
    
    # Check database connection
    if not check_db_connection():
        logger.error("❌ Database connection failed")
        raise Exception("Database connection failed")
    
    # Create tables
    create_tables()
    
    # Ensure upload directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    logger.info("✅ Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Mock Interview AI System...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered resume-based job-matched mock interview system",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploads
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include API routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(resume.router, prefix="/api/resume", tags=["Resume Management"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Job Search"])
app.include_router(interview.router, prefix="/api/interview", tags=["Interview System"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard & Analytics"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Mock Interview AI System API",
        "version": settings.APP_VERSION,
        "status": "healthy",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    db_status = check_db_connection()
    
    return {
        "status": "healthy" if db_status else "unhealthy",
        "database": "connected" if db_status else "disconnected",
        "version": settings.APP_VERSION,
        "upload_dir": settings.UPLOAD_DIR,
        "openai_configured": bool(settings.OPENAI_API_KEY)
    }


@app.get("/stats")
async def get_system_stats():
    """Get system statistics"""
    # This would normally come from database queries
    return {
        "total_users": 0,
        "total_resumes": 0,
        "total_interviews": 0,
        "total_jobs": 0,
        "active_sessions": 0
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "error": "Not Found",
        "message": "The requested resource was not found",
        "status_code": 404
    }


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return {
        "error": "Internal Server Error",
        "message": "An unexpected error occurred",
        "status_code": 500
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )

