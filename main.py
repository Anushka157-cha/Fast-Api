import time
import logging
from fastapi import FastAPI, Depends, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from config import settings
from database import engine, get_db
from models import Base
from routers import auth, tasks
from security import SECRET_KEY, ALGORITHM  # re-exported for tests/backward compatibility

# Configure application logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("api")

# Create tables in the database (local dev fallback; production uses Alembic migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Production-ready FastAPI project with JWT Auth, User Isolation, and SQLite/PostgreSQL",
    version=settings.VERSION
)

# 1. CORS Middleware (allows web frontend apps to communicate with this API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Performance & Request Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = (time.perf_counter() - start_time) * 1000
    response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
    logger.info(f"{request.method} {request.url.path} - {response.status_code} ({process_time:.2f}ms)")
    return response

# 3. Custom Validation Exception Handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    formatted_errors = []
    for error in exc.errors():
        locs = [str(loc) for loc in error["loc"] if loc != "body"]
        field_name = " -> ".join(locs) if locs else "request"
        formatted_errors.append({
            "field": field_name,
            "message": error["msg"]
        })
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Input validation error",
            "errors": formatted_errors
        }
    )

# Include API routers
app.include_router(auth.router)
app.include_router(tasks.router)

@app.get("/", tags=["Root"])
def home():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "docs_url": "/docs"
    }

@app.get("/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint for cloud load balancers and orchestrators (K8s / Render / AWS).
    Verifies that FastAPI is running and database connectivity is operational.
    """
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e),
                "version": settings.VERSION
            }
        )

    return {
        "status": "healthy",
        "database": db_status,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }