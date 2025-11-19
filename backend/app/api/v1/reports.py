"""
Reports API Endpoints

REST API for custom report management and execution.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.report import (
    ReportCreate,
    ReportResponse,
    ReportResultsResponse,
    ReportUpdate,
)
from app.services.report_export_service import ReportExportService
from app.services.report_service import ReportService

router = APIRouter()


@router.post(
    "/tenants/{tenant_id}/reports",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a custom report",
)
async def create_report(
    tenant_id: UUID,
    data: ReportCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new custom report

    Allows users to define custom reports with specific metrics, filters,
    and visualization settings.

    **Security**: Only accessible by authenticated users within their tenant.
    """
    # Verify user belongs to this tenant
    if current_user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden",
        )

    service = ReportService(db)
    report = service.create(data, tenant_id, current_user.id)

    return report


@router.get(
    "/tenants/{tenant_id}/reports",
    response_model=List[ReportResponse],
    summary="List reports",
)
async def list_reports(
    tenant_id: UUID,
    include_private: bool = Query(False, description="Include private reports created by current user"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List all reports for a tenant

    Returns public reports and optionally private reports created by the current user.

    **Security**: Only accessible by authenticated users within their tenant.
    """
    if current_user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden",
        )

    service = ReportService(db)
    reports = service.list_reports(tenant_id, current_user.id, include_private)

    return reports


@router.get(
    "/tenants/{tenant_id}/reports/{report_id}",
    response_model=ReportResponse,
    summary="Get report by ID",
)
async def get_report(
    tenant_id: UUID,
    report_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a specific report by ID

    **Security**: Only accessible by authenticated users within their tenant.
    """
    if current_user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden",
        )

    service = ReportService(db)
    report = service.get_by_id(report_id, tenant_id)

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )

    return report


@router.put(
    "/tenants/{tenant_id}/reports/{report_id}",
    response_model=ReportResponse,
    summary="Update report",
)
async def update_report(
    tenant_id: UUID,
    report_id: UUID,
    data: ReportUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update a report

    **Security**: Only accessible by authenticated users within their tenant.
    """
    if current_user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden",
        )

    service = ReportService(db)
    report = service.update(report_id, data, tenant_id)

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )

    return report


@router.delete(
    "/tenants/{tenant_id}/reports/{report_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete report",
)
async def delete_report(
    tenant_id: UUID,
    report_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a report

    **Security**: Only accessible by authenticated users within their tenant.
    """
    if current_user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden",
        )

    service = ReportService(db)
    success = service.delete(report_id, tenant_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )


@router.post(
    "/tenants/{tenant_id}/reports/{report_id}/execute",
    response_model=ReportResultsResponse,
    summary="Execute report",
)
async def execute_report(
    tenant_id: UUID,
    report_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Execute a report and get results

    Runs the report with configured metrics and filters, returning
    aggregated data points and summary statistics.

    **Security**: Only accessible by authenticated users within their tenant.
    """
    if current_user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden",
        )

    service = ReportService(db)

    # Get report to verify it exists
    report = service.get_by_id(report_id, tenant_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )

    try:
        # Execute report
        results = service.execute_report(report_id, tenant_id)

        return ReportResultsResponse(
            report_id=report.id,
            report_name=report.name,
            generated_at=report.last_generated_at,
            config=report.config,
            data_points=results["data_points"],
            summary=results["summary"],
            total_records=results["total_records"],
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report execution failed: {str(e)}",
        )


@router.post(
    "/tenants/{tenant_id}/reports/{report_id}/export",
    summary="Export report",
)
async def export_report(
    tenant_id: UUID,
    report_id: UUID,
    format: str = Query("csv", pattern="^(pdf|xlsx|csv)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Export a report to PDF, Excel, or CSV

    Executes the report and exports results in the requested format.

    **Supported formats**:
    - `csv`: Comma-separated values
    - `xlsx`: Excel spreadsheet
    - `pdf`: PDF document with tables

    **Security**: Only accessible by authenticated users within their tenant.
    """
    if current_user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden",
        )

    service = ReportService(db)
    export_service = ReportExportService()

    # Get report
    report = service.get_by_id(report_id, tenant_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )

    try:
        # Execute report to get data
        results = service.execute_report(report_id, tenant_id)

        # Export based on format
        if format == "csv":
            content = export_service.export_to_csv(report.name, results["data_points"])
            media_type = "text/csv"
            filename = f"{report.name.replace(' ', '_')}.csv"

        elif format == "xlsx":
            content = export_service.export_to_excel(
                report.name,
                results["data_points"],
                results["summary"],
                report.config,
            )
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = f"{report.name.replace(' ', '_')}.xlsx"

        elif format == "pdf":
            content = export_service.export_to_pdf(
                report.name,
                results["data_points"],
                results["summary"],
                report.config,
            )
            media_type = "application/pdf"
            filename = f"{report.name.replace(' ', '_')}.pdf"

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported format: {format}",
            )

        # Return file
        return Response(
            content=content,
            media_type=media_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    except ImportError as e:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"Export format not available: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export failed: {str(e)}",
        )
