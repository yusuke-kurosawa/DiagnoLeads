"""
Report Service

Business logic for custom report generation, management, and execution.
"""

from uuid import UUID
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.models.report import Report
from app.models.lead import Lead
from app.models.assessment import Assessment
from app.schemas.report import ReportCreate, ReportUpdate, ReportDataPoint


class ReportService:
    """
    Report service with multi-tenant isolation

    Handles custom report creation, execution, and data aggregation.
    """

    def __init__(self, db: Session):
        self.db = db

    # CRUD Operations

    def create(self, data: ReportCreate, tenant_id: UUID, user_id: UUID) -> Report:
        """Create a new report"""
        report = Report(
            tenant_id=tenant_id,
            name=data.name,
            description=data.description,
            report_type=data.report_type,
            config=data.config.model_dump(),
            is_scheduled=data.is_scheduled,
            schedule_config=(
                data.schedule_config.model_dump() if data.schedule_config else None
            ),
            created_by=user_id,
            is_public=data.is_public,
        )

        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)

        return report

    def get_by_id(self, report_id: UUID, tenant_id: UUID) -> Optional[Report]:
        """Get report by ID with tenant check"""
        return (
            self.db.query(Report)
            .filter(and_(Report.id == report_id, Report.tenant_id == tenant_id))
            .first()
        )

    def list_reports(
        self, tenant_id: UUID, user_id: UUID, include_private: bool = False
    ) -> List[Report]:
        """
        List reports for a tenant

        Args:
            tenant_id: Tenant ID
            user_id: Current user ID
            include_private: If True, include private reports created by user
        """
        query = self.db.query(Report).filter(Report.tenant_id == tenant_id)

        if include_private:
            # Show public reports or reports created by this user
            query = query.filter(
                or_(Report.is_public == True, Report.created_by == user_id)
            )
        else:
            # Show only public reports
            query = query.filter(Report.is_public == True)

        return query.order_by(Report.created_at.desc()).all()

    def update(
        self, report_id: UUID, data: ReportUpdate, tenant_id: UUID
    ) -> Optional[Report]:
        """Update a report"""
        report = self.get_by_id(report_id, tenant_id)
        if not report:
            return None

        update_data = data.model_dump(exclude_unset=True)

        # Handle nested models
        if "config" in update_data and update_data["config"]:
            update_data["config"] = update_data["config"].model_dump()
        if "schedule_config" in update_data and update_data["schedule_config"]:
            update_data["schedule_config"] = update_data["schedule_config"].model_dump()

        for key, value in update_data.items():
            setattr(report, key, value)

        self.db.commit()
        self.db.refresh(report)

        return report

    def delete(self, report_id: UUID, tenant_id: UUID) -> bool:
        """Delete a report"""
        report = self.get_by_id(report_id, tenant_id)
        if not report:
            return False

        self.db.delete(report)
        self.db.commit()

        return True

    # Report Execution

    def execute_report(self, report_id: UUID, tenant_id: UUID) -> Dict[str, Any]:
        """
        Execute a report and return results

        Returns:
            Dictionary with data_points and summary
        """
        report = self.get_by_id(report_id, tenant_id)
        if not report:
            raise ValueError("Report not found")

        config = report.config
        metrics = config.get("metrics", [])
        filters = config.get("filters", {})
        group_by = config.get("group_by")

        # Update last_generated_at
        report.last_generated_at = datetime.utcnow()
        self.db.commit()

        # Execute based on report type
        if report.report_type == "lead_analysis":
            return self._execute_lead_analysis_report(
                tenant_id, metrics, filters, group_by
            )
        elif report.report_type == "assessment_performance":
            return self._execute_assessment_performance_report(
                tenant_id, metrics, filters, group_by
            )
        else:
            # Custom report - generic execution
            return self._execute_custom_report(tenant_id, metrics, filters, group_by)

    def _execute_lead_analysis_report(
        self,
        tenant_id: UUID,
        metrics: List[str],
        filters: Dict[str, Any],
        group_by: Optional[str],
    ) -> Dict[str, Any]:
        """Execute lead analysis report"""
        # Build query with filters
        query = self.db.query(Lead).filter(Lead.tenant_id == tenant_id)
        query = self._apply_lead_filters(query, filters)

        leads = query.all()

        # Group and aggregate
        if group_by:
            data_points = self._group_leads(leads, group_by, metrics)
        else:
            data_points = [self._aggregate_leads(leads, metrics, "All Leads")]

        # Calculate summary
        summary = self._calculate_lead_summary(leads, metrics)

        return {
            "data_points": data_points,
            "summary": summary,
            "total_records": len(leads),
        }

    def _execute_assessment_performance_report(
        self,
        tenant_id: UUID,
        metrics: List[str],
        filters: Dict[str, Any],
        group_by: Optional[str],
    ) -> Dict[str, Any]:
        """Execute assessment performance report"""
        query = self.db.query(Assessment).filter(Assessment.tenant_id == tenant_id)
        query = self._apply_assessment_filters(query, filters)

        assessments = query.all()

        # Group and aggregate
        if group_by:
            data_points = self._group_assessments(assessments, group_by, metrics)
        else:
            data_points = [
                self._aggregate_assessments(assessments, metrics, "All Assessments")
            ]

        summary = self._calculate_assessment_summary(assessments, metrics)

        return {
            "data_points": data_points,
            "summary": summary,
            "total_records": len(assessments),
        }

    def _execute_custom_report(
        self,
        tenant_id: UUID,
        metrics: List[str],
        filters: Dict[str, Any],
        group_by: Optional[str],
    ) -> Dict[str, Any]:
        """Execute custom report (combines leads and assessments)"""
        # For custom reports, combine multiple data sources
        lead_query = self.db.query(Lead).filter(Lead.tenant_id == tenant_id)
        lead_query = self._apply_lead_filters(lead_query, filters)
        leads = lead_query.all()

        assessment_query = self.db.query(Assessment).filter(
            Assessment.tenant_id == tenant_id
        )
        assessment_query = self._apply_assessment_filters(assessment_query, filters)
        assessments = assessment_query.all()

        # Aggregate based on metrics requested
        data_points = []
        summary = {}

        if any("lead" in m for m in metrics):
            lead_data = self._aggregate_leads(leads, metrics, "Leads")
            data_points.append(lead_data)
            summary.update(self._calculate_lead_summary(leads, metrics))

        if any("assessment" in m for m in metrics):
            assessment_data = self._aggregate_assessments(
                assessments, metrics, "Assessments"
            )
            data_points.append(assessment_data)
            summary.update(self._calculate_assessment_summary(assessments, metrics))

        return {
            "data_points": data_points,
            "summary": summary,
            "total_records": len(leads) + len(assessments),
        }

    # Filtering

    def _apply_lead_filters(self, query, filters: Dict[str, Any]):
        """Apply filters to lead query"""
        if not filters:
            return query

        # Date range filter
        if "date_range" in filters:
            date_range = filters["date_range"]
            if "start" in date_range:
                start_date = datetime.fromisoformat(date_range["start"])
                query = query.filter(Lead.created_at >= start_date)
            if "end" in date_range:
                end_date = datetime.fromisoformat(date_range["end"])
                query = query.filter(Lead.created_at <= end_date)

        # Status filter
        if "status" in filters and filters["status"]:
            query = query.filter(Lead.status.in_(filters["status"]))

        # Score range filter
        if "score_range" in filters:
            score_range = filters["score_range"]
            if "min" in score_range:
                query = query.filter(Lead.score >= score_range["min"])
            if "max" in score_range:
                query = query.filter(Lead.score <= score_range["max"])

        return query

    def _apply_assessment_filters(self, query, filters: Dict[str, Any]):
        """Apply filters to assessment query"""
        if not filters:
            return query

        # Date range filter
        if "date_range" in filters:
            date_range = filters["date_range"]
            if "start" in date_range:
                start_date = datetime.fromisoformat(date_range["start"])
                query = query.filter(Assessment.created_at >= start_date)
            if "end" in date_range:
                end_date = datetime.fromisoformat(date_range["end"])
                query = query.filter(Assessment.created_at <= end_date)

        # Status filter
        if "status" in filters and filters["status"]:
            query = query.filter(Assessment.status.in_(filters["status"]))

        # AI generation filter
        if "ai_generated" in filters and filters["ai_generated"]:
            query = query.filter(Assessment.ai_generated.in_(filters["ai_generated"]))

        return query

    # Grouping and Aggregation

    def _group_leads(
        self, leads: List[Lead], group_by: str, metrics: List[str]
    ) -> List[Dict[str, Any]]:
        """Group leads and aggregate metrics"""
        groups = {}

        for lead in leads:
            if group_by == "status":
                key = lead.status
            elif group_by == "date":
                key = lead.created_at.date().isoformat()
            else:
                key = "Other"

            if key not in groups:
                groups[key] = []
            groups[key].append(lead)

        data_points = []
        for label, group_leads in groups.items():
            data_points.append(self._aggregate_leads(group_leads, metrics, label))

        return data_points

    def _group_assessments(
        self, assessments: List[Assessment], group_by: str, metrics: List[str]
    ) -> List[Dict[str, Any]]:
        """Group assessments and aggregate metrics"""
        groups = {}

        for assessment in assessments:
            if group_by == "status":
                key = assessment.status
            elif group_by == "date":
                key = assessment.created_at.date().isoformat()
            elif group_by == "ai_generated":
                key = assessment.ai_generated or "manual"
            else:
                key = "Other"

            if key not in groups:
                groups[key] = []
            groups[key].append(assessment)

        data_points = []
        for label, group_assessments in groups.items():
            data_points.append(
                self._aggregate_assessments(group_assessments, metrics, label)
            )

        return data_points

    def _aggregate_leads(
        self, leads: List[Lead], metrics: List[str], label: str
    ) -> Dict[str, Any]:
        """Aggregate lead metrics"""
        values = {}

        if "leads_total" in metrics:
            values["leads_total"] = len(leads)

        if "average_score" in metrics:
            values["average_score"] = (
                round(sum(lead.score for lead in leads) / len(leads), 2)
                if leads
                else 0.0
            )

        if "conversion_rate" in metrics:
            converted = sum(1 for lead in leads if lead.status == "converted")
            values["conversion_rate"] = (
                round((converted / len(leads)) * 100, 2) if leads else 0.0
            )

        if "hot_leads" in metrics:
            values["hot_leads"] = sum(1 for lead in leads if lead.score >= 61)

        return {"label": label, "values": values}

    def _aggregate_assessments(
        self, assessments: List[Assessment], metrics: List[str], label: str
    ) -> Dict[str, Any]:
        """Aggregate assessment metrics"""
        values = {}

        if "assessments_total" in metrics:
            values["assessments_total"] = len(assessments)

        if "published_count" in metrics:
            values["published_count"] = sum(
                1 for a in assessments if a.status == "published"
            )

        if "ai_generated_count" in metrics:
            values["ai_generated_count"] = sum(
                1 for a in assessments if a.ai_generated == "ai"
            )

        return {"label": label, "values": values}

    # Summary Calculations

    def _calculate_lead_summary(
        self, leads: List[Lead], metrics: List[str]
    ) -> Dict[str, Any]:
        """Calculate summary statistics for leads"""
        summary = {"period": "custom", "total_leads": len(leads)}

        if leads and "average_score" in metrics:
            summary["overall_average_score"] = round(
                sum(lead.score for lead in leads) / len(leads), 2
            )

        if leads and "conversion_rate" in metrics:
            converted = sum(1 for lead in leads if lead.status == "converted")
            summary["overall_conversion_rate"] = round(
                (converted / len(leads)) * 100, 2
            )

        return summary

    def _calculate_assessment_summary(
        self, assessments: List[Assessment], metrics: List[str]
    ) -> Dict[str, Any]:
        """Calculate summary statistics for assessments"""
        summary = {"period": "custom", "total_assessments": len(assessments)}

        if assessments and "published_count" in metrics:
            published = sum(1 for a in assessments if a.status == "published")
            summary["published_percentage"] = round(
                (published / len(assessments)) * 100, 2
            )

        return summary
