"""
OAuth State Management

Manages OAuth state tokens for CSRF protection during OAuth flows.
"""

import secrets
from typing import Optional
from uuid import UUID
from datetime import datetime, timedelta, timezone


# In-memory state store (for development)
# TODO: Replace with Redis in production for horizontal scaling
_state_store: dict[str, tuple[str, datetime]] = {}


def generate_oauth_state(tenant_id: UUID, crm_type: str) -> str:
    """
    Generate a secure OAuth state token.

    The state token is used to prevent CSRF attacks during OAuth flows.
    It contains the tenant_id and CRM type encoded for validation.

    Args:
        tenant_id: Tenant UUID
        crm_type: 'salesforce' or 'hubspot'

    Returns:
        Secure random state token (32 bytes, URL-safe)

    Example:
        >>> state = generate_oauth_state(tenant_id, 'salesforce')
        >>> # Redirect user to OAuth URL with state parameter
    """
    # Generate cryptographically secure random token
    state = secrets.token_urlsafe(32)

    # Store state with tenant_id and expiration (15 minutes)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
    _state_store[state] = (f"{tenant_id}:{crm_type}", expires_at)

    # Clean up expired states
    _cleanup_expired_states()

    return state


def verify_oauth_state(state: str) -> Optional[tuple[UUID, str]]:
    """
    Verify OAuth state token and return tenant_id and CRM type.

    Args:
        state: OAuth state token to verify

    Returns:
        Tuple of (tenant_id, crm_type) if valid, None if invalid/expired

    Raises:
        ValueError: If state is invalid or expired

    Example:
        >>> tenant_id, crm_type = verify_oauth_state(state)
        >>> # Proceed with OAuth callback processing
    """
    if state not in _state_store:
        raise ValueError("Invalid or expired OAuth state token")

    value, expires_at = _state_store[state]

    # Check expiration
    if datetime.now(timezone.utc) > expires_at:
        del _state_store[state]
        raise ValueError("OAuth state token has expired")

    # Delete state token (one-time use)
    del _state_store[state]

    # Parse tenant_id and crm_type
    tenant_id_str, crm_type = value.split(":", 1)
    tenant_id = UUID(tenant_id_str)

    return tenant_id, crm_type


def _cleanup_expired_states():
    """
    Remove expired state tokens from store.

    This is called automatically during state generation.
    """
    now = datetime.now(timezone.utc)
    expired_keys = [
        key for key, (_, expires_at) in _state_store.items() if now > expires_at
    ]

    for key in expired_keys:
        del _state_store[key]


# Redis-based implementation (for production)
# Uncomment and configure when Redis is available

# import redis
# from app.core.config import settings
#
# redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
#
# def generate_oauth_state_redis(tenant_id: UUID, crm_type: str) -> str:
#     """Generate OAuth state token and store in Redis."""
#     state = secrets.token_urlsafe(32)
#     value = f"{tenant_id}:{crm_type}"
#
#     # Store in Redis with 15-minute expiration
#     redis_client.setex(f"oauth_state:{state}", 900, value)
#
#     return state
#
# def verify_oauth_state_redis(state: str) -> Optional[tuple[UUID, str]]:
#     """Verify OAuth state token from Redis."""
#     value = redis_client.get(f"oauth_state:{state}")
#
#     if not value:
#         raise ValueError("Invalid or expired OAuth state token")
#
#     # Delete token (one-time use)
#     redis_client.delete(f"oauth_state:{state}")
#
#     # Parse tenant_id and crm_type
#     tenant_id_str, crm_type = value.split(":", 1)
#     tenant_id = UUID(tenant_id_str)
#
#     return tenant_id, crm_type
