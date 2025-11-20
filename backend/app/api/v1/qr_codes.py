"""QR Code API endpoints"""

from typing import Dict, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.models.qr_code import QRCode
from app.models.user import User
from app.schemas.qr_code import (
    QRCodeCreate,
    QRCodeListResponse,
    QRCodeResponse,
    QRCodeUpdate,
)
from app.services.qr_code_service import QRCodeService

router = APIRouter(prefix="/qr-codes", tags=["qr-codes"])


@router.post(
    "",
    response_model=QRCodeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create QR Code",
    description="Create a new QR code for an assessment",
)
async def create_qr_code(
    assessment_id: UUID,
    qr_data: QRCodeCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> QRCodeResponse:
    """
    Create a new QR code for an assessment.

    Args:
        assessment_id: Assessment UUID
        qr_data: QR code creation data
        current_user: Authenticated user
        db: Database session

    Returns:
        Created QR code

    Raises:
        404: Assessment not found
        400: Invalid data
    """
    service = QRCodeService(db)

    try:
        qr_code = await service.create_qr_code(
            tenant_id=current_user.tenant_id,
            assessment_id=assessment_id,
            qr_data=qr_data,
        )
        return QRCodeResponse.model_validate(qr_code)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create QR code: {str(e)}",
        )


@router.get(
    "",
    response_model=QRCodeListResponse,
    summary="List QR Codes",
    description="Get list of QR codes for the current tenant",
)
async def list_qr_codes(
    assessment_id: Optional[UUID] = Query(None, description="Filter by assessment"),
    enabled: Optional[bool] = Query(None, description="Filter by enabled status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> QRCodeListResponse:
    """
    Get paginated list of QR codes.

    Args:
        assessment_id: Optional assessment filter
        enabled: Optional enabled status filter
        page: Page number (1-indexed)
        limit: Items per page
        current_user: Authenticated user
        db: Database session

    Returns:
        Paginated QR code list
    """
    # Build query with filters
    query = select(QRCode).where(QRCode.tenant_id == current_user.tenant_id)

    if assessment_id:
        query = query.where(QRCode.assessment_id == assessment_id)

    if enabled is not None:
        query = query.where(QRCode.enabled == enabled)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    # Paginate
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit).order_by(QRCode.created_at.desc())

    result = await db.execute(query)
    qr_codes = result.scalars().all()

    # Calculate pages
    pages = (total + limit - 1) // limit  # Ceiling division

    return QRCodeListResponse(
        qr_codes=[QRCodeResponse.model_validate(qr) for qr in qr_codes],
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


@router.get(
    "/{qr_code_id}",
    response_model=QRCodeResponse,
    summary="Get QR Code",
    description="Get details of a specific QR code",
)
async def get_qr_code(
    qr_code_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> QRCodeResponse:
    """
    Get QR code by ID.

    Args:
        qr_code_id: QR code UUID
        current_user: Authenticated user
        db: Database session

    Returns:
        QR code details

    Raises:
        404: QR code not found
    """
    result = await db.execute(select(QRCode).where(and_(QRCode.id == qr_code_id, QRCode.tenant_id == current_user.tenant_id)))
    qr_code = result.scalar_one_or_none()

    if not qr_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"QR code {qr_code_id} not found",
        )

    return QRCodeResponse.model_validate(qr_code)


@router.patch(
    "/{qr_code_id}",
    response_model=QRCodeResponse,
    summary="Update QR Code",
    description="Update QR code properties (name, enabled status)",
)
async def update_qr_code(
    qr_code_id: UUID,
    update_data: QRCodeUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> QRCodeResponse:
    """
    Update QR code.

    Args:
        qr_code_id: QR code UUID
        update_data: Update data
        current_user: Authenticated user
        db: Database session

    Returns:
        Updated QR code

    Raises:
        404: QR code not found
    """
    # Fetch QR code
    result = await db.execute(select(QRCode).where(and_(QRCode.id == qr_code_id, QRCode.tenant_id == current_user.tenant_id)))
    qr_code = result.scalar_one_or_none()

    if not qr_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"QR code {qr_code_id} not found",
        )

    # Apply updates
    update_dict = update_data.dict(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(qr_code, key, value)

    await db.commit()
    await db.refresh(qr_code)

    return QRCodeResponse.model_validate(qr_code)


@router.delete(
    "/{qr_code_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete QR Code",
    description="Delete a QR code",
)
async def delete_qr_code(
    qr_code_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete QR code.

    Args:
        qr_code_id: QR code UUID
        current_user: Authenticated user
        db: Database session

    Raises:
        404: QR code not found
    """
    # Fetch QR code
    result = await db.execute(select(QRCode).where(and_(QRCode.id == qr_code_id, QRCode.tenant_id == current_user.tenant_id)))
    qr_code = result.scalar_one_or_none()

    if not qr_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"QR code {qr_code_id} not found",
        )

    await db.delete(qr_code)
    await db.commit()


@router.post(
    "/{qr_code_id}/regenerate",
    response_model=QRCodeResponse,
    summary="Regenerate QR Image",
    description="Regenerate QR code image with updated style",
)
async def regenerate_qr_image(
    qr_code_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> QRCodeResponse:
    """
    Regenerate QR code image.

    Useful when style is updated or image needs to be recreated.

    Args:
        qr_code_id: QR code UUID
        current_user: Authenticated user
        db: Database session

    Returns:
        Updated QR code with new image URL

    Raises:
        404: QR code not found
    """
    service = QRCodeService(db)

    try:
        qr_code = await service.regenerate_qr_image(qr_code_id=qr_code_id, tenant_id=current_user.tenant_id)
        return QRCodeResponse.model_validate(qr_code)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to regenerate QR image: {str(e)}",
        )


@router.get(
    "/{qr_code_id}/analytics",
    summary="Get QR Code Analytics",
    description="Get comprehensive analytics for a QR code",
)
async def get_qr_analytics(
    qr_code_id: UUID,
    days: int = Query(30, ge=1, le=90, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get analytics for a QR code.

    Includes:
    - Summary statistics
    - Scans by date
    - Scans by device type
    - Scans by country
    - Conversion funnel

    Args:
        qr_code_id: QR code UUID
        days: Number of days to analyze (1-90)
        current_user: Authenticated user
        db: Database session

    Returns:
        Analytics data

    Raises:
        404: QR code not found
    """
    from datetime import datetime, timedelta

    from app.models.qr_code_scan import QRCodeScan

    # Verify QR code exists and belongs to tenant
    qr_result = await db.execute(select(QRCode).where(and_(QRCode.id == qr_code_id, QRCode.tenant_id == current_user.tenant_id)))
    qr_code = qr_result.scalar_one_or_none()

    if not qr_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"QR code {qr_code_id} not found",
        )

    # Date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # Get all scans in date range
    scans_result = await db.execute(select(QRCodeScan).where(and_(QRCodeScan.qr_code_id == qr_code_id, QRCodeScan.scanned_at >= start_date)))
    scans = scans_result.scalars().all()

    # Summary statistics
    total_scans = len(scans)
    started = sum(1 for s in scans if s.assessment_started)
    completed = sum(1 for s in scans if s.assessment_completed)
    leads = sum(1 for s in scans if s.lead_created)

    conversion_rate = (completed / total_scans * 100) if total_scans > 0 else 0.0

    summary = {
        "total_scans": total_scans,
        "unique_scans": qr_code.unique_scan_count,
        "assessment_started": started,
        "assessment_completed": completed,
        "leads_created": leads,
        "conversion_rate": round(conversion_rate, 2),
    }

    # Scans by date
    scans_by_date_dict: Dict[str, int] = {}
    for scan in scans:
        date_str = scan.scanned_at.strftime("%Y-%m-%d")
        scans_by_date_dict[date_str] = scans_by_date_dict.get(date_str, 0) + 1

    scans_by_date = [{"date": date, "scans": count} for date, count in sorted(scans_by_date_dict.items())]

    # Scans by device
    device_counts = {"mobile": 0, "tablet": 0, "desktop": 0, "unknown": 0}
    for scan in scans:
        device_type = scan.device_type or "unknown"
        if device_type in device_counts:
            device_counts[device_type] += 1
        else:
            device_counts["unknown"] += 1

    scans_by_device = device_counts

    # Scans by country
    country_counts: Dict[str, int] = {}
    for scan in scans:
        if scan.country:
            country_counts[scan.country] = country_counts.get(scan.country, 0) + 1

    scans_by_country = {
        "country_scans": dict(sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:10])  # Top 10 countries
    }

    # Conversion funnel
    funnel = {
        "scanned": total_scans,
        "started": started,
        "completed": completed,
        "converted": leads,
    }

    return {
        "summary": summary,
        "scans_by_date": scans_by_date,
        "scans_by_device": scans_by_device,
        "scans_by_country": scans_by_country,
        "funnel": funnel,
    }
