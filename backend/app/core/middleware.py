"""
Multi-Tenant Middleware

Automatically applies tenant context to all requests.
"""

from fastapi import Request
from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings
from app.core.deps import current_tenant_id


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract tenant_id from JWT and set tenant context.

    All database queries will automatically be scoped to the tenant.
    """

    async def dispatch(self, request: Request, call_next):
        # Handle CORS preflight requests (OPTIONS)
        if request.method == "OPTIONS":
            return await call_next(request)

        # Skip authentication for public endpoints
        public_paths = [
            "/health",
            "/",
            "/api/docs",
            "/api/redoc",
            "/api/openapi.json",
            "/api/v1/auth/login",
            "/api/v1/auth/login/json",
            "/api/v1/auth/register",
            "/api/v1/auth/refresh",
            "/api/v1/auth/password-reset",
            "/api/v1/auth/password-reset/confirm",
        ]

        # Check exact path matches
        if request.url.path in public_paths:
            return await call_next(request)

        # Check path patterns for public endpoints (embed widget)
        path = request.url.path
        if "/assessments/" in path and "/public" in path or path.startswith("/api/v1/responses"):
            return await call_next(request)

        # Extract JWT token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing or invalid authorization header"},
            )

        token = auth_header.split(" ")[1]

        try:
            # Decode JWT and extract tenant_id
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )
            tenant_id = payload.get("tenant_id")
            user_id = payload.get("user_id")

            if not tenant_id:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Invalid token: missing tenant_id claim"},
                )

            # Attach tenant_id and user_id to request state
            request.state.tenant_id = tenant_id
            request.state.user_id = user_id

            # Set context variable for RLS (database-level tenant isolation)
            current_tenant_id.set(str(tenant_id))

        except JWTError:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or expired token"},
            )

        response = await call_next(request)
        return response
