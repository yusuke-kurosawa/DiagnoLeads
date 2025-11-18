"""
Report Schemas

Pydantic models for report requests and responses.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class ReportConfig(BaseModel):
    """Report configuration"""

    metrics: List[str] = Field(
        ...,
        description="Metrics to include: leads_total, conversion_rate, average_score, etc.",
        examples=[["leads_total", "conversion_rate", "average_score"]],
    )
    filters: Optional[Dict[str, Any]] = Field(
        None,
        description="Filters to apply",
        examples=[
            {
                "date_range": {"start": "2024-01-01", "end": "2024-12-31"},
                "status": ["new", "qualified"],
                "score_range": {"min": 60, "max": 100},
            }
        ],
    )
    group_by: Optional[str] = Field(
        None, description="Group results by: status|industry|date|assessment"
    )
    visualization: str = Field(
        default="table",
        description="Visualization type: bar_chart|line_chart|pie_chart|table",
    )
    sort_by: Optional[str] = Field(None, description="Sort by metric name")
    sort_order: str = Field(default="desc", description="Sort order: asc|desc")


class ScheduleConfig(BaseModel):
    """Report schedule configuration"""

    frequency: str = Field(..., description="Frequency: daily|weekly|monthly")
    day_of_week: Optional[int] = Field(
        None, ge=0, le=6, description="For weekly reports (0=Monday)"
    )
    day_of_month: Optional[int] = Field(
        None, ge=1, le=31, description="For monthly reports"
    )
    time: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="Time in HH:MM format")
    timezone: str = Field(default="Asia/Tokyo", description="Timezone")
    recipients: List[str] = Field(..., description="Email recipients")


class ReportCreate(BaseModel):
    """Request to create a new report"""

    name: str = Field(..., min_length=1, max_length=255, description="Report name")
    description: Optional[str] = Field(None, max_length=1000)
    report_type: str = Field(
        default="custom",
        description="Report type: custom|lead_analysis|assessment_performance|conversion_funnel|ai_insights",
    )
    config: ReportConfig
    is_scheduled: bool = Field(default=False)
    schedule_config: Optional[ScheduleConfig] = None
    is_public: bool = Field(default=False, description="Visible to all tenant users")


class ReportUpdate(BaseModel):
    """Request to update a report"""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    config: Optional[ReportConfig] = None
    is_scheduled: Optional[bool] = None
    schedule_config: Optional[ScheduleConfig] = None
    is_public: Optional[bool] = None


class ReportResponse(BaseModel):
    """Report definition response"""

    id: UUID
    tenant_id: UUID
    name: str
    description: Optional[str]
    report_type: str
    config: Dict[str, Any]
    is_scheduled: bool
    schedule_config: Optional[Dict[str, Any]]
    last_generated_at: Optional[datetime]
    created_by: Optional[UUID]
    is_public: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReportDataPoint(BaseModel):
    """Single data point in report results"""

    label: str = Field(..., description="Label for this data point")
    values: Dict[str, Any] = Field(..., description="Metric values")


class ReportResultsResponse(BaseModel):
    """Report execution results"""

    report_id: UUID
    report_name: str
    generated_at: datetime
    config: Dict[str, Any]
    data_points: List[ReportDataPoint]
    summary: Dict[str, Any] = Field(..., description="Summary statistics")
    total_records: int


class ExportFormat(BaseModel):
    """Export format specification"""

    format: str = Field(..., pattern="^(pdf|xlsx|csv)$", description="Export format")
    include_charts: bool = Field(default=True, description="Include visualizations")
    page_size: str = Field(default="A4", description="Page size for PDF")
    orientation: str = Field(default="portrait", description="Orientation: portrait|landscape")


class ReportExportRequest(BaseModel):
    """Request to export report"""

    report_id: UUID
    export_format: ExportFormat
    filters: Optional[Dict[str, Any]] = Field(
        None, description="Override report filters for this export"
    )
