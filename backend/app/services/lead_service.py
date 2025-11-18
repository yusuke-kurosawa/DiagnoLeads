"""
Lead Service

Business logic for lead management with multi-tenant support.
"""

from uuid import UUID
from typing import List, Optional
from datetime import datetime
import os
import asyncio
import uuid as uuid_lib

from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, or_
from fastapi import HTTPException, status

from app.models.lead import Lead
from app.models.tenant import Tenant
from app.models.google_analytics_integration import GoogleAnalyticsIntegration
from app.schemas.lead import LeadCreate, LeadUpdate, LeadStatusUpdate, LeadScoreUpdate
from app.integrations.google_analytics.measurement_protocol import GA4MeasurementProtocol

# Teams integration
try:
    from app.integrations.microsoft.teams_webhook_client import TeamsWebhookClient
    TEAMS_INTEGRATION_AVAILABLE = True
except ImportError:
    TEAMS_INTEGRATION_AVAILABLE = False
    print("⚠️  Teams integration not available")


class LeadService:
    """
    Lead service with strict multi-tenant isolation

    **IMPORTANT**: All methods enforce tenant_id filtering
    """

    def __init__(self, db: Session):
        self.db = db
        self._teams_notification_enabled = TEAMS_INTEGRATION_AVAILABLE

    async def _send_ga4_event(
        self,
        tenant_id: UUID,
        event_name: str,
        event_params: dict,
        client_id: Optional[str] = None
    ) -> None:
        """
        Send GA4 event via Measurement Protocol (async, non-blocking)

        Args:
            tenant_id: Tenant UUID
            event_name: GA4 event name
            event_params: Event parameters
            client_id: Optional client ID (generates if not provided)
        """
        try:
            # Get GA4 integration config for tenant
            ga_integration = self.db.query(GoogleAnalyticsIntegration).filter(
                GoogleAnalyticsIntegration.tenant_id == tenant_id
            ).first()

            # Check if GA4 is enabled and configured for server-side tracking
            if not ga_integration or not ga_integration.enabled:
                return

            if not ga_integration.track_server_events:
                return

            if not ga_integration.measurement_protocol_api_secret:
                print(f"⚠️  GA4 Measurement Protocol API Secret not configured for tenant {tenant_id}")
                return

            # Create GA4 client
            client = GA4MeasurementProtocol(
                measurement_id=ga_integration.measurement_id,
                api_secret=ga_integration.measurement_protocol_api_secret,
                debug=False
            )

            # Generate client_id if not provided
            if not client_id:
                client_id = f"server-{uuid_lib.uuid4()}"

            # Add tenant_id to event params
            event_params["tenant_id"] = str(tenant_id)

            # Send event
            success = await client.send_event(
                client_id=client_id,
                event_name=event_name,
                event_params=event_params
            )

            if success:
                print(f"✅ GA4 event sent: {event_name} for tenant {tenant_id}")
            else:
                print(f"⚠️  GA4 event failed: {event_name} for tenant {tenant_id}")

        except Exception as e:
            # Log error but don't fail lead operations
            print(f"⚠️  Failed to send GA4 event {event_name}: {str(e)}")

    async def _send_teams_notification(self, lead: Lead, tenant: Tenant) -> None:
        """
        Send Teams notification for hot lead (async)
        
        Args:
            lead: Lead object
            tenant: Tenant object
        """
        if not self._teams_notification_enabled:
            return
        
        # Get webhook URL from tenant settings or environment
        webhook_url = tenant.settings.get("teams_webhook_url") or os.getenv("TEAMS_WEBHOOK_URL")
        
        if not webhook_url:
            print(f"⚠️  No Teams webhook URL configured for tenant {tenant.name}")
            return
        
        # Check if lead is hot (score >= 80)
        if lead.score < 80:
            return
        
        try:
            teams_client = TeamsWebhookClient(webhook_url)
            
            # Prepare lead data
            lead_data = {
                "lead_id": str(lead.id),
                "company_name": lead.company or "N/A",
                "contact_name": lead.name,
                "job_title": lead.job_title or "N/A",
                "email": lead.email,
                "phone": lead.phone or "未提供",
                "score": lead.score,
                "assessment_title": "診断完了",  # TODO: Get from assessment
            }
            
            # TODO: Construct actual dashboard URL
            dashboard_url = f"https://app.diagnoleads.com/leads/{lead.id}"
            
            await teams_client.send_hot_lead_notification(
                lead_data=lead_data,
                dashboard_url=dashboard_url
            )
            
            print(f"✅ Teams notification sent for lead {lead.id} (score: {lead.score})")
            
        except Exception as e:
            # Log error but don't fail lead creation
            print(f"⚠️  Failed to send Teams notification: {str(e)}")

    def list_by_tenant(
        self,
        tenant_id: UUID,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        min_score: Optional[int] = None,
        max_score: Optional[int] = None,
        assigned_to: Optional[UUID] = None,
    ) -> List[Lead]:
        """
        List all leads for a specific tenant with optional filters
        """
        query = self.db.query(Lead).filter(
            Lead.tenant_id == tenant_id  # REQUIRED: Tenant filtering
        )

        # Optional filters
        if status:
            query = query.filter(Lead.status == status)
        
        if min_score is not None:
            query = query.filter(Lead.score >= min_score)
        
        if max_score is not None:
            query = query.filter(Lead.score <= max_score)
        
        if assigned_to:
            query = query.filter(Lead.assigned_to == assigned_to)

        # Sort by score (highest first), then creation date
        leads = (
            query.order_by(desc(Lead.score), desc(Lead.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

        return leads

    def get_by_id(self, lead_id: UUID, tenant_id: UUID) -> Optional[Lead]:
        """
        Get lead by ID with tenant isolation
        """
        lead = self.db.query(Lead).filter(
            and_(
                Lead.id == lead_id,
                Lead.tenant_id == tenant_id,  # REQUIRED: Tenant filtering
            )
        ).first()

        return lead

    def get_by_email(self, email: str, tenant_id: UUID) -> Optional[Lead]:
        """
        Get lead by email with tenant isolation
        """
        lead = self.db.query(Lead).filter(
            and_(
                Lead.email == email,
                Lead.tenant_id == tenant_id,  # REQUIRED: Tenant filtering
            )
        ).first()

        return lead

    def create(
        self, data: LeadCreate, tenant_id: UUID, created_by: UUID
    ) -> Lead:
        """
        Create a new lead

        Raises:
            HTTPException: If email already exists in tenant
        """
        # Check for duplicate email within tenant
        existing_lead = self.get_by_email(email=data.email, tenant_id=tenant_id)
        if existing_lead:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Lead with email {data.email} already exists in this tenant",
            )

        lead = Lead(
            **data.model_dump(),
            tenant_id=tenant_id,  # REQUIRED: Set tenant_id
            created_by=created_by,
            score=0,  # Initialize score
            last_activity_at=datetime.utcnow(),
        )

        self.db.add(lead)
        self.db.commit()
        self.db.refresh(lead)

        is_hot_lead = lead.score >= 80

        # Send GA4 events (async, non-blocking)
        try:
            # Send lead_generated event
            asyncio.create_task(self._send_ga4_event(
                tenant_id=tenant_id,
                event_name="lead_generated",
                event_params={
                    "lead_id": str(lead.id),
                    "lead_score": lead.score,
                    "lead_status": lead.status,
                    "company": lead.company or "unknown",
                }
            ))

            # Send hot_lead_generated conversion event if applicable
            if is_hot_lead:
                asyncio.create_task(self._send_ga4_event(
                    tenant_id=tenant_id,
                    event_name="hot_lead_generated",
                    event_params={
                        "lead_id": str(lead.id),
                        "lead_score": lead.score,
                        "company": lead.company or "unknown",
                        "value": lead.score,  # Use score as conversion value
                    }
                ))
        except RuntimeError:
            # No event loop running, skip GA4 events
            print("⚠️  Cannot send GA4 events: no event loop")

        # Send Teams notification if hot lead (async, non-blocking)
        if is_hot_lead:
            tenant = self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
            if tenant:
                try:
                    # Run async notification in background
                    asyncio.create_task(self._send_teams_notification(lead, tenant))
                except RuntimeError:
                    # No event loop running, skip notification
                    print("⚠️  Cannot send Teams notification: no event loop")

        return lead

    def update(
        self, lead_id: UUID, data: LeadUpdate, tenant_id: UUID, updated_by: UUID
    ) -> Optional[Lead]:
        """
        Update an existing lead
        """
        # Get lead with tenant filtering
        lead = self.get_by_id(lead_id=lead_id, tenant_id=tenant_id)

        if not lead:
            return None

        # Check email uniqueness if email is being updated
        update_data = data.model_dump(exclude_unset=True)
        if "email" in update_data and update_data["email"] != lead.email:
            existing_lead = self.get_by_email(
                email=update_data["email"], tenant_id=tenant_id
            )
            if existing_lead:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Lead with email {update_data['email']} already exists in this tenant",
                )

        # Update fields
        for field, value in update_data.items():
            setattr(lead, field, value)

        lead.updated_by = updated_by
        lead.last_activity_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(lead)

        return lead

    def update_status(
        self, lead_id: UUID, data: LeadStatusUpdate, tenant_id: UUID, updated_by: UUID
    ) -> Optional[Lead]:
        """
        Update lead status with validation
        """
        lead = self.get_by_id(lead_id=lead_id, tenant_id=tenant_id)

        if not lead:
            return None

        # Status transition validation
        old_status = lead.status
        new_status = data.status

        # Cannot change from 'converted'
        if old_status == "converted" and new_status != "converted":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change status from 'converted'",
            )

        lead.status = new_status
        lead.updated_by = updated_by
        lead.last_activity_at = datetime.utcnow()

        # Update last_contacted_at if status is 'contacted'
        if new_status == "contacted" and old_status == "new":
            lead.last_contacted_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(lead)

        # Send GA4 event for status change (async, non-blocking)
        if old_status != new_status:
            try:
                asyncio.create_task(self._send_ga4_event(
                    tenant_id=tenant_id,
                    event_name="lead_status_changed",
                    event_params={
                        "lead_id": str(lead.id),
                        "old_status": old_status,
                        "new_status": new_status,
                        "lead_score": lead.score,
                    }
                ))

                # Send conversion event if status changed to 'converted'
                if new_status == "converted":
                    asyncio.create_task(self._send_ga4_event(
                        tenant_id=tenant_id,
                        event_name="lead_converted",
                        event_params={
                            "lead_id": str(lead.id),
                            "lead_score": lead.score,
                            "company": lead.company or "unknown",
                            "value": 100,  # Conversion value
                        }
                    ))
            except RuntimeError:
                # No event loop running, skip GA4 events
                print("⚠️  Cannot send GA4 events: no event loop")

        return lead

    def update_score(
        self, lead_id: UUID, data: LeadScoreUpdate, tenant_id: UUID
    ) -> Optional[Lead]:
        """
        Update lead score and send Teams notification if hot lead
        """
        lead = self.get_by_id(lead_id=lead_id, tenant_id=tenant_id)

        if not lead:
            return None

        old_score = lead.score
        new_score = data.score

        lead.score = new_score
        lead.last_activity_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(lead)

        # Send GA4 events if lead becomes hot (score crosses threshold)
        if old_score < 80 and new_score >= 80:
            try:
                asyncio.create_task(self._send_ga4_event(
                    tenant_id=tenant_id,
                    event_name="hot_lead_generated",
                    event_params={
                        "lead_id": str(lead.id),
                        "lead_score": new_score,
                        "old_score": old_score,
                        "company": lead.company or "unknown",
                        "value": new_score,  # Use score as conversion value
                    }
                ))
            except RuntimeError:
                # No event loop running, skip GA4 events
                print("⚠️  Cannot send GA4 events: no event loop")

        # Send Teams notification if lead becomes hot (score crosses threshold)
        if old_score < 80 and new_score >= 80:
            tenant = self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
            if tenant:
                try:
                    # Run async notification in background
                    asyncio.create_task(self._send_teams_notification(lead, tenant))
                except RuntimeError:
                    # No event loop running, skip notification
                    print("⚠️  Cannot send Teams notification: no event loop")

        return lead

    def delete(self, lead_id: UUID, tenant_id: UUID) -> bool:
        """
        Delete a lead (physical delete for GDPR compliance)
        """
        lead = self.get_by_id(lead_id=lead_id, tenant_id=tenant_id)

        if not lead:
            return False

        self.db.delete(lead)
        self.db.commit()

        return True

    def count_by_tenant(
        self, tenant_id: UUID, status: Optional[str] = None
    ) -> int:
        """
        Count leads for a tenant
        """
        query = self.db.query(Lead).filter(
            Lead.tenant_id == tenant_id  # REQUIRED: Tenant filtering
        )

        if status:
            query = query.filter(Lead.status == status)

        return query.count()

    def search(
        self, tenant_id: UUID, query: str, limit: int = 10
    ) -> List[Lead]:
        """
        Search leads by name, email, or company
        """
        search_pattern = f"%{query}%"

        leads = (
            self.db.query(Lead)
            .filter(
                and_(
                    Lead.tenant_id == tenant_id,  # REQUIRED: Tenant filtering
                    or_(
                        Lead.name.ilike(search_pattern),
                        Lead.email.ilike(search_pattern),
                        Lead.company.ilike(search_pattern),
                    ),
                )
            )
            .limit(limit)
            .all()
        )

        return leads

    def get_hot_leads(self, tenant_id: UUID, threshold: int = 61) -> List[Lead]:
        """
        Get hot leads (score >= threshold) for a tenant
        """
        leads = (
            self.db.query(Lead)
            .filter(
                and_(
                    Lead.tenant_id == tenant_id,  # REQUIRED: Tenant filtering
                    Lead.score >= threshold,
                    Lead.status.in_(["new", "contacted", "qualified"]),
                )
            )
            .order_by(desc(Lead.score))
            .all()
        )

        return leads
