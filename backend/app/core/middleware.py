"""
Multi-Tenant Middleware

Automatically applies tenant context to all requests.
"""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt, JWTError

from app.core.config import settings


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract tenant_id from JWT and set tenant context.

    All database queries will automatically be scoped to the tenant.
    """

    async def dispatch(self, request: Request, call_next):
        # Skip authentication for public endpoints
        public_paths = [
            "/health",
            "/",
            "/api/docs",
            "/api/redoc",
            "/api/openapi.json",
            "/api/v1/auth/login",
            "/api/v1/auth/register",
        ]

        if request.url.path in public_paths:
            return await call_next(request)

        # Extract JWT token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
                detail="Missing or invalid authorization header",
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
                raise HTTPException(
                    status_code=401,
                    detail="Invalid token: missing tenant_id claim",
                )

            # Attach tenant_id and user_id to request state
            request.state.tenant_id = tenant_id
            request.state.user_id = user_id

        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        response = await call_next(request)
        return response
