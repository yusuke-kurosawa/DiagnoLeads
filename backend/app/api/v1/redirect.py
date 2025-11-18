"""QR Code Redirect and Tracking API"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from user_agents import parse as parse_user_agent

from app.core.deps import get_db
from app.models.qr_code import QRCode
from app.models.qr_code_scan import QRCodeScan


router = APIRouter(tags=["redirect"])


def parse_device_info(user_agent_string: str) -> dict:
    """Parse user agent string to extract device information.
    
    Args:
        user_agent_string: User-Agent header value
    
    Returns:
        Dict with device_type, os, browser
    """
    ua = parse_user_agent(user_agent_string)
    
    # Determine device type
    if ua.is_mobile:
        device_type = "mobile"
    elif ua.is_tablet:
        device_type = "tablet"
    elif ua.is_pc:
        device_type = "desktop"
    else:
        device_type = "unknown"
    
    # Get OS and browser
    os_name = ua.os.family if ua.os.family else "Unknown"
    browser_name = ua.browser.family if ua.browser.family else "Unknown"
    
    return {
        "device_type": device_type,
        "os": os_name,
        "browser": browser_name
    }


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request.
    
    Handles X-Forwarded-For header for proxied requests.
    
    Args:
        request: FastAPI request
    
    Returns:
        Client IP address
    """
    # Check X-Forwarded-For header (for proxied requests)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Take first IP in the chain
        return forwarded_for.split(",")[0].strip()
    
    # Fall back to direct connection IP
    if request.client:
        return request.client.host
    
    return "unknown"


async def get_geo_location(ip_address: str) -> dict:
    """Get geographic location from IP address using GeoIP.
    
    NOTE: This is a placeholder. In production, integrate with:
    - MaxMind GeoIP2
    - ipapi.co
    - ip-api.com
    
    Args:
        ip_address: IP address
    
    Returns:
        Dict with country, city, latitude, longitude
    """
    # TODO: Implement actual GeoIP lookup
    # Example with MaxMind GeoIP2:
    # import geoip2.database
    # reader = geoip2.database.Reader('/path/to/GeoLite2-City.mmdb')
    # response = reader.city(ip_address)
    # return {
    #     "country": response.country.iso_code,
    #     "city": response.city.name,
    #     "latitude": response.location.latitude,
    #     "longitude": response.location.longitude
    # }
    
    # Placeholder response
    return {
        "country": None,
        "city": None,
        "latitude": None,
        "longitude": None
    }


@router.get(
    "/{short_code}",
    response_class=RedirectResponse,
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    summary="QR Code Redirect",
    description="Redirect short URL to assessment and track scan",
    include_in_schema=False  # Hide from OpenAPI docs (public endpoint)
)
async def redirect_qr_code(
    short_code: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    """
    Redirect QR code short URL to assessment.
    
    This endpoint:
    1. Looks up QR code by short_code
    2. Creates scan tracking record
    3. Increments scan counter
    4. Redirects to assessment URL
    
    Args:
        short_code: 7-character short code
        request: FastAPI request (for headers, IP)
        db: Database session
    
    Returns:
        Redirect to assessment URL
    
    Raises:
        404: QR code not found or disabled
    """
    # 1. Look up QR code
    result = await db.execute(
        select(QRCode).where(QRCode.short_code == short_code)
    )
    qr_code = result.scalar_one_or_none()
    
    if not qr_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"QR code '{short_code}' not found"
        )
    
    # Check if QR code is enabled
    if not qr_code.enabled:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="This QR code has been disabled"
        )
    
    # 2. Extract tracking data
    user_agent_string = request.headers.get("User-Agent", "")
    device_info = parse_device_info(user_agent_string)
    
    ip_address = get_client_ip(request)
    geo_info = await get_geo_location(ip_address)
    
    # Get session ID from cookie (if exists)
    session_id = request.cookies.get("session_id")
    
    # 3. Create scan tracking record
    scan = QRCodeScan(
        qr_code_id=qr_code.id,
        user_agent=user_agent_string,
        device_type=device_info["device_type"],
        os=device_info["os"],
        browser=device_info["browser"],
        ip_address=ip_address,  # Note: Hash this in production for privacy
        country=geo_info["country"],
        city=geo_info["city"],
        latitude=geo_info["latitude"],
        longitude=geo_info["longitude"],
        scanned_at=datetime.utcnow(),
        session_id=session_id,
        assessment_started=False,
        assessment_completed=False,
        lead_created=False,
    )
    
    db.add(scan)
    
    # 4. Increment scan counters
    qr_code.scan_count += 1
    qr_code.last_scanned_at = datetime.utcnow()
    
    # TODO: Implement unique scan counting logic
    # (e.g., based on session_id or IP+User-Agent fingerprint)
    
    await db.commit()
    
    # 5. Build redirect URL
    base_url = f"https://app.diagnoleads.com/assessments/{qr_code.assessment_id}"
    
    # Add UTM parameters
    utm_params = []
    if qr_code.utm_source:
        utm_params.append(f"utm_source={qr_code.utm_source}")
    if qr_code.utm_medium:
        utm_params.append(f"utm_medium={qr_code.utm_medium}")
    if qr_code.utm_campaign:
        utm_params.append(f"utm_campaign={qr_code.utm_campaign}")
    if qr_code.utm_term:
        utm_params.append(f"utm_term={qr_code.utm_term}")
    if qr_code.utm_content:
        utm_params.append(f"utm_content={qr_code.utm_content}")
    
    # Add QR code tracking parameter
    utm_params.append(f"qr={short_code}")
    
    # Add scan ID for tracking (optional)
    utm_params.append(f"scan_id={scan.id}")
    
    redirect_url = f"{base_url}?{'&'.join(utm_params)}"
    
    # 6. Redirect
    return RedirectResponse(url=redirect_url)


@router.get(
    "/api/v1/qr-codes/{short_code}/preview",
    summary="Preview QR Code URL",
    description="Get redirect URL without tracking (for testing)",
    tags=["qr-codes"]
)
async def preview_qr_redirect(
    short_code: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Preview the redirect URL for a QR code without tracking.
    
    Useful for testing and debugging.
    
    Args:
        short_code: 7-character short code
        db: Database session
    
    Returns:
        Dict with redirect_url and QR code info
    
    Raises:
        404: QR code not found
    """
    result = await db.execute(
        select(QRCode).where(QRCode.short_code == short_code)
    )
    qr_code = result.scalar_one_or_none()
    
    if not qr_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"QR code '{short_code}' not found"
        )
    
    # Build URL
    base_url = f"https://app.diagnoleads.com/assessments/{qr_code.assessment_id}"
    
    utm_params = []
    if qr_code.utm_source:
        utm_params.append(f"utm_source={qr_code.utm_source}")
    if qr_code.utm_medium:
        utm_params.append(f"utm_medium={qr_code.utm_medium}")
    if qr_code.utm_campaign:
        utm_params.append(f"utm_campaign={qr_code.utm_campaign}")
    if qr_code.utm_term:
        utm_params.append(f"utm_term={qr_code.utm_term}")
    if qr_code.utm_content:
        utm_params.append(f"utm_content={qr_code.utm_content}")
    
    utm_params.append(f"qr={short_code}")
    
    redirect_url = f"{base_url}?{'&'.join(utm_params)}"
    
    return {
        "short_code": short_code,
        "short_url": qr_code.short_url,
        "redirect_url": redirect_url,
        "enabled": qr_code.enabled,
        "scan_count": qr_code.scan_count,
    }
