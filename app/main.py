"""
FastAPI application for PII extraction and management
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import time

from app.config import settings
from app.api import extraction, matcher, pdf, consent, search
from app.services.pdf_service import pdf_service
from app.utils.logger import logger

# Create FastAPI app
app = FastAPI(
    title="PII Extraction Service",
    description="AI-based document PII extraction with semantic matching and consent management",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests"""
    start_time = time.time()

    # Process request
    response = await call_next(request)

    # Calculate duration
    duration = time.time() - start_time

    logger.info(
        "HTTP request",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration * 1000, 2),
        },
    )

    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# Include routers
app.include_router(extraction.router)
app.include_router(matcher.router)
app.include_router(pdf.router)
app.include_router(consent.router)
app.include_router(search.router)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting PII Extraction Service")

    # Create sample PDF template
    pdf_service.create_sample_template()

    logger.info("Service started successfully")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "PII Extraction Service",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "extract": "POST /extract - Extract PII from documents",
            "match": "POST /match - Match PII using similarity",
            "prefill-pdf": "POST /prefill-pdf - Fill PDF forms",
            "consent_create": "POST /consent/create - Create consent token",
            "consent_redeem": "GET /consent/redeem - Redeem consent token",
            "search": "GET /search - Semantic search (bonus)",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
    )
