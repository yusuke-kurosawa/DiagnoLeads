"""
API v1 Router

Combines all API endpoints under /api/v1
"""

from fastapi import APIRouter

# from app.api.v1 import auth, assessments, leads, analytics

api_router = APIRouter()

# Include sub-routers
# api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
# api_router.include_router(assessments.router, prefix="/assessments", tags=["Assessments"])
# api_router.include_router(leads.router, prefix="/leads", tags=["Leads"])
# api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])

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
