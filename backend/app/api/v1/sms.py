"""
SMS Campaign API Endpoints

REST API for SMS campaign management and sending.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.sms_campaign import SMSCampaign, SMSMessage, SMSStatus
from app.models.qr_code import QRCode
from app.services.sms_service import SMSService


router = APIRouter()


# Schemas
class SMSCampaignCreate(BaseModel):
    """SMS campaign creation request"""
    name: str = Field(..., min_length=1, max_length=255, description="Campaign name")
    assessment_id: UUID = Field(..., description="Assessment ID")
    qr_code_id: Optional[UUID] = Field(None, description="Optional QR code for short URL")
    message_template: str = Field(..., min_length=1, description="Message template with {url} placeholder")
    recipients: List[str] = Field(..., min_items=1, max_items=1000, description="List of phone numbers")
    scheduled_at: Optional[str] = Field(None, description="Scheduled send time (ISO format)")

    @validator("message_template")
    def validate_template(cls, v):
        if "{url}" not in v:
            raise ValueError("Message template must contain {url} placeholder")
        if len(v) > 1600:  # SMS limit
            raise ValueError("Message too long (max 1600 characters)")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "name": "展示会フォローアップ",
                "assessment_id": "123e4567-e89b-12d3-a456-426614174000",
                "qr_code_id": "123e4567-e89b-12d3-a456-426614174001",
                "message_template": "DiagnoLeadsから診断のご案内です。{url} ※3分で完了",
                "recipients": ["+819012345678", "+819087654321"]
            }
        }


class SMSCampaignResponse(BaseModel):
    """SMS campaign response"""
    id: UUID
    name: str
    assessment_id: UUID
    qr_code_id: Optional[UUID]
    message_template: str
    total_recipients: int
    sent_count: int
    delivered_count: int
    failed_count: int
    status: SMSStatus
    created_at: str
    sent_at: Optional[str]

    class Config:
        from_attributes = True


class SMSTestRequest(BaseModel):
    """Test SMS request"""
    phone_number: str = Field(..., description="Test phone number (E.164 format)")
    message: str = Field(default="これはDiagnoLeadsからのテストSMSです", description="Test message")


class SMSEstimateRequest(BaseModel):
    """Cost estimation request"""
    num_recipients: int = Field(..., ge=1, le=10000, description="Number of recipients")
    region: str = Field(default="JP", description="Region code (JP, US, etc.)")


# API Endpoints
@router.post(
    "/tenants/{tenant_id}/sms/campaigns",
    response_model=SMSCampaignResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create SMS Campaign",
    operation_id="createSMSCampaign",
)
async def create_sms_campaign(
    tenant_id: UUID,
    campaign_data: SMSCampaignCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create and send SMS campaign"""
    # Permission check
    if current_user.tenant_id != tenant_id and current_user.role != "system_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden"
        )

    # Validate phone numbers
    sms_service = SMSService()
    validated_numbers = []
    errors = []

    for phone in campaign_data.recipients:
        is_valid, result = sms_service.validate_phone_number(phone)
        if is_valid:
            validated_numbers.append(result)
        else:
            errors.append({"phone": phone, "error": result})

    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Invalid phone numbers", "errors": errors}
        )

    # Get QR code short URL if specified
    short_url = None
    if campaign_data.qr_code_id:
        qr_code = db.query(QRCode).filter(
            QRCode.id == campaign_data.qr_code_id,
            QRCode.tenant_id == tenant_id
        ).first()

        if not qr_code:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="QR code not found"
            )

        short_url = qr_code.short_url
    else:
        # Use assessment direct URL
        short_url = f"https://app.diagnoleads.com/a/{campaign_data.assessment_id}"

    # Create campaign
    campaign = SMSCampaign(
        tenant_id=tenant_id,
        assessment_id=campaign_data.assessment_id,
        qr_code_id=campaign_data.qr_code_id,
        created_by=current_user.id,
        name=campaign_data.name,
        message_template=campaign_data.message_template,
        recipients={"numbers": validated_numbers, "total": len(validated_numbers)},
        total_recipients=len(validated_numbers),
        status=SMSStatus.PENDING
    )

    db.add(campaign)
    db.commit()
    db.refresh(campaign)

    # Send SMS campaign (async)
    try:
        results = await sms_service.send_campaign(
            campaign=campaign,
            recipients=validated_numbers,
            short_url=short_url,
            db=db
        )

        return SMSCampaignResponse(
            id=campaign.id,
            name=campaign.name,
            assessment_id=campaign.assessment_id,
            qr_code_id=campaign.qr_code_id,
            message_template=campaign.message_template,
            total_recipients=campaign.total_recipients,
            sent_count=campaign.sent_count,
            delivered_count=campaign.delivered_count,
            failed_count=campaign.failed_count,
            status=campaign.status,
            created_at=campaign.created_at.isoformat(),
            sent_at=campaign.sent_at.isoformat() if campaign.sent_at else None
        )

    except Exception as e:
        # Mark campaign as failed
        campaign.status = SMSStatus.FAILED
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send SMS campaign: {str(e)}"
        )


@router.get(
    "/tenants/{tenant_id}/sms/campaigns",
    response_model=List[SMSCampaignResponse],
    summary="List SMS Campaigns",
    operation_id="listSMSCampaigns",
)
async def list_sms_campaigns(
    tenant_id: UUID,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all SMS campaigns for tenant"""
    # Permission check
    if current_user.tenant_id != tenant_id and current_user.role != "system_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden"
        )

    campaigns = db.query(SMSCampaign).filter(
        SMSCampaign.tenant_id == tenant_id
    ).order_by(SMSCampaign.created_at.desc()).offset(skip).limit(limit).all()

    return [
        SMSCampaignResponse(
            id=c.id,
            name=c.name,
            assessment_id=c.assessment_id,
            qr_code_id=c.qr_code_id,
            message_template=c.message_template,
            total_recipients=c.total_recipients,
            sent_count=c.sent_count,
            delivered_count=c.delivered_count,
            failed_count=c.failed_count,
            status=c.status,
            created_at=c.created_at.isoformat(),
            sent_at=c.sent_at.isoformat() if c.sent_at else None
        )
        for c in campaigns
    ]


@router.post(
    "/tenants/{tenant_id}/sms/test",
    summary="Send Test SMS",
    operation_id="sendTestSMS",
)
async def send_test_sms(
    tenant_id: UUID,
    test_data: SMSTestRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Send a test SMS to verify Twilio configuration"""
    # Permission check
    if current_user.tenant_id != tenant_id and current_user.role != "system_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden"
        )

    # Validate phone number
    sms_service = SMSService()
    is_valid, result = sms_service.validate_phone_number(test_data.phone_number)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result
        )

    # Send test SMS
    try:
        send_result = sms_service.send_sms(
            to=result,
            message=test_data.message
        )

        return {
            "status": "success",
            "message": "Test SMS sent successfully",
            "twilio_sid": send_result["sid"],
            "to": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send test SMS: {str(e)}"
        )


@router.post(
    "/tenants/{tenant_id}/sms/estimate",
    summary="Estimate SMS Cost",
    operation_id="estimateSMSCost",
)
async def estimate_sms_cost(
    tenant_id: UUID,
    estimate_data: SMSEstimateRequest,
    current_user: User = Depends(get_current_user),
):
    """Estimate cost for SMS campaign"""
    # Permission check
    if current_user.tenant_id != tenant_id and current_user.role != "system_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden"
        )

    sms_service = SMSService()
    estimation = sms_service.estimate_cost(
        num_messages=estimate_data.num_recipients,
        region=estimate_data.region
    )

    return estimation


@router.get(
    "/tenants/{tenant_id}/sms/campaigns/{campaign_id}/messages",
    summary="Get Campaign Messages",
    operation_id="getCampaignMessages",
)
async def get_campaign_messages(
    tenant_id: UUID,
    campaign_id: UUID,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get individual messages from campaign"""
    # Permission check
    if current_user.tenant_id != tenant_id and current_user.role != "system_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden"
        )

    # Get campaign
    campaign = db.query(SMSCampaign).filter(
        SMSCampaign.id == campaign_id,
        SMSCampaign.tenant_id == tenant_id
    ).first()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )

    # Get messages
    messages = db.query(SMSMessage).filter(
        SMSMessage.campaign_id == campaign_id
    ).offset(skip).limit(limit).all()

    return {
        "campaign_id": str(campaign_id),
        "campaign_name": campaign.name,
        "total_messages": campaign.total_recipients,
        "messages": [
            {
                "id": str(msg.id),
                "phone_number": msg.phone_number,
                "status": msg.status,
                "twilio_sid": msg.twilio_sid,
                "sent_at": msg.sent_at.isoformat() if msg.sent_at else None,
                "delivered_at": msg.delivered_at.isoformat() if msg.delivered_at else None,
                "clicked": msg.clicked,
                "error_message": msg.error_message
            }
            for msg in messages
        ]
    }
