"""
DiagnoLeads FastAPI Application

Multi-tenant B2B assessment platform with AI capabilities.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.middleware import TenantMiddleware
from app.api.v1 import api_router

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    description="Multi-tenant B2B assessment platform with AI",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Multi-tenant Middleware
# app.add_middleware(TenantMiddleware)  # TODO: Uncomment after implementation

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return JSONResponse(
        content={
            "status": "healthy",
            "service": "diagnoleads-api",
            "version": "0.1.0",
        }
    )


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return JSONResponse(
        content={
            "message": "DiagnoLeads API",
            "version": "0.1.0",
            "docs": "/api/docs",
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
