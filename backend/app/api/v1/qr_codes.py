"""QR Code API endpoints"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.qr_code import QRCode
from app.services.qr_code_service import QRCodeService
from app.schemas.qr_code import (
    QRCodeCreate,
    QRCodeUpdate,
    QRCodeResponse,
    QRCodeListResponse,
)


router = APIRouter(prefix="/qr-codes", tags=["qr-codes"])


@router.post(
    "",
    response_model=QRCodeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create QR Code",
    description="Create a new QR code for an assessment"
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
            qr_data=qr_data
        )
        return QRCodeResponse.from_orm(qr_code)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create QR code: {str(e)}"
        )


@router.get(
    "",
    response_model=QRCodeListResponse,
    summary="List QR Codes",
    description="Get list of QR codes for the current tenant"
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
        qr_codes=[QRCodeResponse.from_orm(qr) for qr in qr_codes],
        total=total,
        page=page,
        limit=limit,
        pages=pages
    )


@router.get(
    "/{qr_code_id}",
    response_model=QRCodeResponse,
    summary="Get QR Code",
    description="Get details of a specific QR code"
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
    result = await db.execute(
        select(QRCode).where(
            and_(
                QRCode.id == qr_code_id,
                QRCode.tenant_id == current_user.tenant_id
            )
        )
    )
    qr_code = result.scalar_one_or_none()
    
    if not qr_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"QR code {qr_code_id} not found"
        )
    
    return QRCodeResponse.from_orm(qr_code)


@router.patch(
    "/{qr_code_id}",
    response_model=QRCodeResponse,
    summary="Update QR Code",
    description="Update QR code properties (name, enabled status)"
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
    result = await db.execute(
        select(QRCode).where(
            and_(
                QRCode.id == qr_code_id,
                QRCode.tenant_id == current_user.tenant_id
            )
        )
    )
    qr_code = result.scalar_one_or_none()
    
    if not qr_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"QR code {qr_code_id} not found"
        )
    
    # Apply updates
    update_dict = update_data.dict(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(qr_code, key, value)
    
    await db.commit()
    await db.refresh(qr_code)
    
    return QRCodeResponse.from_orm(qr_code)


@router.delete(
    "/{qr_code_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete QR Code",
    description="Delete a QR code"
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
    result = await db.execute(
        select(QRCode).where(
            and_(
                QRCode.id == qr_code_id,
                QRCode.tenant_id == current_user.tenant_id
            )
        )
    )
    qr_code = result.scalar_one_or_none()
    
    if not qr_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"QR code {qr_code_id} not found"
        )
    
    await db.delete(qr_code)
    await db.commit()


@router.post(
    "/{qr_code_id}/regenerate",
    response_model=QRCodeResponse,
    summary="Regenerate QR Image",
    description="Regenerate QR code image with updated style"
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
        qr_code = await service.regenerate_qr_image(
            qr_code_id=qr_code_id,
            tenant_id=current_user.tenant_id
        )
        return QRCodeResponse.from_orm(qr_code)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to regenerate QR image: {str(e)}"
        )
