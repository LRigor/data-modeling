"""
FastAPI application main file.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.routes import patients, call_history, medical_conditions
from app.exceptions import DatabaseError
from app.logger import logger

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    myTomorrows CRM API - A FastAPI application for managing patient and person data.
    
    ## Features
    
    * **Patient Management**: Full CRUD operations for patients
    * **Call History**: Track all patient navigator calls
    * **Medical Conditions**: Manage medical condition lookup table
    * **Person Normalization**: Single source of truth for person data
    
    ## Design Principles
    
    * Normalized database design
    * Support for multiple journeys per patient
    * Preserved call history (no data loss)
    * Returning patient handling
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    patients.router,
    prefix=settings.api_v1_prefix,
)
app.include_router(
    call_history.router,
    prefix=settings.api_v1_prefix,
)
app.include_router(
    medical_conditions.router,
    prefix=settings.api_v1_prefix,
)


@app.get("/", tags=["root"])
def root() -> dict:
    """
    Root endpoint providing API information.
    
    Returns:
        Dictionary with API metadata
    """
    return {
        "message": "myTomorrows CRM API",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["health"])
def health_check() -> dict:
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns:
        Dictionary with service health status
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
    }


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """
    Handle ValueError exceptions.
    
    Args:
        request: FastAPI request object
        exc: ValueError exception
        
    Returns:
        JSON error response
    """
    logger.warning(f"Validation error: {exc}")
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc), "error_code": "VALIDATION_ERROR"},
    )


@app.exception_handler(DatabaseError)
async def database_error_handler(request: Request, exc: DatabaseError) -> JSONResponse:
    """
    Handle DatabaseError exceptions.
    
    Args:
        request: FastAPI request object
        exc: DatabaseError exception
        
    Returns:
        JSON error response
    """
    logger.error(f"Database error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred", "error_code": "DATABASE_ERROR"},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
