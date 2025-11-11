"""
API v1 Router

Combines all API endpoints under /api/v1
"""

from fastapi import APIRouter

from app.api.v1 import auth, assessments, leads, analytics, qr_codes, qr_scans

api_router = APIRouter()

# Include sub-routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(assessments.router, tags=["Assessments"])
api_router.include_router(leads.router, tags=["Leads"])
api_router.include_router(analytics.router, tags=["Analytics"])
api_router.include_router(qr_codes.router, tags=["QR Codes"])
api_router.include_router(qr_scans.router, tags=["QR Scans"])


# Placeholder endpoint
@api_router.get("/")
async def api_root():
    """API v1 root endpoint"""
    return {
        "message": "DiagnoLeads API v1",
        "endpoints": {
            "auth": "/api/v1/auth",
            "assessments": "/api/v1/assessments",
            "leads": "/api/v1/leads",
            "analytics": "/api/v1/analytics",
        },
    }
