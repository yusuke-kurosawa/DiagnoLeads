"""QR Code Scan Tracking API

Endpoints for updating scan tracking data (assessment progress, lead conversion).
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.models.lead import Lead
from app.models.qr_code_scan import QRCodeScan

router = APIRouter(prefix="/scans", tags=["qr-scans"])


@router.put(
    "/{scan_id}/started",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Mark Assessment Started",
    description="Update scan to indicate user started the assessment",
)
async def mark_assessment_started(
    scan_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Mark that user started the assessment.

    Called by frontend when assessment page loads.

    Args:
        scan_id: Scan UUID (from URL parameter)
        db: Database session

    Raises:
        404: Scan not found
    """
    # Fetch scan
    result = await db.execute(select(QRCodeScan).where(QRCodeScan.id == scan_id))
    scan = result.scalar_one_or_none()

    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Scan {scan_id} not found")

    # Update flag
    if not scan.assessment_started:
        scan.assessment_started = True
        await db.commit()


@router.put(
    "/{scan_id}/completed",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Mark Assessment Completed",
    description="Update scan to indicate user completed the assessment",
)
async def mark_assessment_completed(
    scan_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Mark that user completed the assessment.

    Called by frontend when assessment is submitted.

    Args:
        scan_id: Scan UUID
        db: Database session

    Raises:
        404: Scan not found
    """
    result = await db.execute(select(QRCodeScan).where(QRCodeScan.id == scan_id))
    scan = result.scalar_one_or_none()

    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Scan {scan_id} not found")

    # Update flags
    if not scan.assessment_completed:
        scan.assessment_completed = True
        # Auto-mark as started if not already
        if not scan.assessment_started:
            scan.assessment_started = True
        await db.commit()


@router.put(
    "/{scan_id}/lead",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Link Lead to Scan",
    description="Update scan to link it with created lead",
)
async def link_lead_to_scan(
    scan_id: UUID,
    lead_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Link a lead to a scan.

    Called by backend when lead is created from assessment.

    Args:
        scan_id: Scan UUID
        lead_id: Lead UUID
        db: Database session

    Raises:
        404: Scan or lead not found
    """
    # Fetch scan
    scan_result = await db.execute(select(QRCodeScan).where(QRCodeScan.id == scan_id))
    scan = scan_result.scalar_one_or_none()

    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Scan {scan_id} not found")

    # Verify lead exists
    lead_result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = lead_result.scalar_one_or_none()

    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Lead {lead_id} not found")

    # Update scan
    scan.lead_id = lead_id
    scan.lead_created = True

    # Auto-mark as completed if not already
    if not scan.assessment_completed:
        scan.assessment_completed = True
    if not scan.assessment_started:
        scan.assessment_started = True

    await db.commit()


@router.get(
    "/{scan_id}",
    summary="Get Scan Details",
    description="Get scan tracking information",
)
async def get_scan_details(
    scan_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get scan details.

    Args:
        scan_id: Scan UUID
        db: Database session

    Returns:
        Scan information

    Raises:
        404: Scan not found
    """
    result = await db.execute(select(QRCodeScan).where(QRCodeScan.id == scan_id))
    scan = result.scalar_one_or_none()

    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Scan {scan_id} not found")

    return {
        "id": str(scan.id),
        "qr_code_id": str(scan.qr_code_id),
        "device_type": scan.device_type,
        "os": scan.os,
        "browser": scan.browser,
        "country": scan.country,
        "city": scan.city,
        "scanned_at": scan.scanned_at.isoformat() if scan.scanned_at else None,
        "assessment_started": scan.assessment_started,
        "assessment_completed": scan.assessment_completed,
        "lead_created": scan.lead_created,
        "lead_id": str(scan.lead_id) if scan.lead_id else None,
    }
