"""
Tests for Core Middleware

Comprehensive tests for TenantMiddleware and request handling.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import Request
from jose import jwt
from starlette.responses import JSONResponse

from app.core.config import settings
from app.core.middleware import TenantMiddleware


class TestTenantMiddleware:
    """Tests for TenantMiddleware"""

    @pytest.fixture
    def middleware(self):
        """Create middleware instance"""
        app = MagicMock()
        return TenantMiddleware(app)

    @pytest.fixture
    def mock_request(self):
        """Create mock request"""
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        return request

    @pytest.mark.asyncio
    async def test_options_request_passes_through(self, middleware, mock_request):
        """Test that OPTIONS requests bypass authentication"""
        mock_request.method = "OPTIONS"
        call_next = AsyncMock(return_value=JSONResponse(content={}))

        response = await middleware.dispatch(mock_request, call_next)

        call_next.assert_called_once_with(mock_request)
        assert response is not None

    @pytest.mark.asyncio
    async def test_public_path_passes_through(self, middleware, mock_request):
        """Test that public paths bypass authentication"""
        mock_request.method = "GET"
        mock_request.url.path = "/health"
        call_next = AsyncMock(return_value=JSONResponse(content={"status": "ok"}))

        response = await middleware.dispatch(mock_request, call_next)

        call_next.assert_called_once_with(mock_request)

    @pytest.mark.asyncio
    async def test_login_endpoint_is_public(self, middleware, mock_request):
        """Test that login endpoint is accessible without auth"""
        mock_request.method = "POST"
        mock_request.url.path = "/api/v1/auth/login"
        call_next = AsyncMock(return_value=JSONResponse(content={}))

        response = await middleware.dispatch(mock_request, call_next)

        call_next.assert_called_once()

    @pytest.mark.asyncio
    async def test_missing_authorization_header(self, middleware, mock_request):
        """Test request without Authorization header"""
        mock_request.method = "GET"
        mock_request.url.path = "/api/v1/leads"
        mock_request.headers.get.return_value = None

        response = await middleware.dispatch(mock_request, AsyncMock())

        assert isinstance(response, JSONResponse)
        assert response.status_code == 401
        assert "Missing or invalid authorization header" in str(response.body)

    @pytest.mark.asyncio
    async def test_invalid_authorization_format(self, middleware, mock_request):
        """Test authorization header without Bearer prefix"""
        mock_request.method = "GET"
        mock_request.url.path = "/api/v1/leads"
        mock_request.headers.get.return_value = "InvalidFormat token123"

        response = await middleware.dispatch(mock_request, AsyncMock())

        assert isinstance(response, JSONResponse)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_valid_token_with_tenant_id(self, middleware, mock_request):
        """Test valid JWT token with tenant_id"""
        tenant_id = "tenant-123"
        user_id = "user-456"

        # Create valid token
        token_payload = {"tenant_id": tenant_id, "user_id": user_id}
        token = jwt.encode(token_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

        mock_request.method = "GET"
        mock_request.url.path = "/api/v1/leads"
        mock_request.headers.get.return_value = f"Bearer {token}"

        call_next = AsyncMock(return_value=JSONResponse(content={"data": []}))

        response = await middleware.dispatch(mock_request, call_next)

        # Verify tenant_id and user_id were set on request state
        assert mock_request.state.tenant_id == tenant_id
        assert mock_request.state.user_id == user_id

        # Verify request proceeded
        call_next.assert_called_once()

    @pytest.mark.asyncio
    async def test_token_missing_tenant_id(self, middleware, mock_request):
        """Test token without tenant_id claim"""
        # Create token without tenant_id
        token_payload = {"user_id": "user-123"}
        token = jwt.encode(token_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        mock_request.method = "GET"
        mock_request.url.path = "/api/v1/leads"
        mock_request.headers.get.return_value = f"Bearer {token}"

        response = await middleware.dispatch(mock_request, AsyncMock())

        assert isinstance(response, JSONResponse)
        assert response.status_code == 401
        assert "missing tenant_id claim" in str(response.body)

    @pytest.mark.asyncio
    async def test_expired_token(self, middleware, mock_request):
        """Test expired JWT token"""
        # Create expired token (using wrong secret will also cause JWTError)
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjB9.invalid"
        
        mock_request.method = "GET"
        mock_request.url.path = "/api/v1/leads"
        mock_request.headers.get.return_value = f"Bearer {token}"

        response = await middleware.dispatch(mock_request, AsyncMock())

        assert isinstance(response, JSONResponse)
        assert response.status_code == 401
        assert "Invalid or expired token" in str(response.body)

    @pytest.mark.asyncio
    async def test_malformed_token(self, middleware, mock_request):
        """Test malformed JWT token"""
        mock_request.method = "GET"
        mock_request.url.path = "/api/v1/leads"
        mock_request.headers.get.return_value = "Bearer malformed.token.here"

        response = await middleware.dispatch(mock_request, AsyncMock())

        assert isinstance(response, JSONResponse)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_docs_endpoint_is_public(self, middleware, mock_request):
        """Test that API documentation endpoints are public"""
        for path in ["/api/docs", "/api/redoc", "/api/openapi.json"]:
            mock_request.method = "GET"
            mock_request.url.path = path
            call_next = AsyncMock(return_value=JSONResponse(content={}))

            response = await middleware.dispatch(mock_request, call_next)

            call_next.assert_called()

    @pytest.mark.asyncio
    async def test_register_endpoint_is_public(self, middleware, mock_request):
        """Test that registration endpoint is public"""
        mock_request.method = "POST"
        mock_request.url.path = "/api/v1/auth/register"
        call_next = AsyncMock(return_value=JSONResponse(content={}))

        response = await middleware.dispatch(mock_request, call_next)

        call_next.assert_called_once()

    @pytest.mark.asyncio
    async def test_password_reset_endpoints_are_public(self, middleware, mock_request):
        """Test that password reset endpoints are public"""
        for path in ["/api/v1/auth/password-reset", "/api/v1/auth/password-reset/confirm"]:
            mock_request.method = "POST"
            mock_request.url.path = path
            call_next = AsyncMock(return_value=JSONResponse(content={}))

            response = await middleware.dispatch(mock_request, call_next)

            call_next.assert_called()
