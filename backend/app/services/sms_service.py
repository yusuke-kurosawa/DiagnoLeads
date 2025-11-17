"""
SMS Service

Handles SMS sending via Twilio for assessment distribution.
"""

import os
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from app.models.sms_campaign import SMSCampaign, SMSMessage, SMSStatus


class SMSService:
    """
    SMS sending service using Twilio.

    Features:
    - Send individual SMS
    - Send bulk SMS campaigns
    - Track delivery status
    - Handle Twilio webhooks
    """

    def __init__(self):
        """Initialize Twilio client."""
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_PHONE_NUMBER")

        if not all([self.account_sid, self.auth_token, self.from_number]):
            raise ValueError(
                "Twilio credentials not configured. "
                "Please set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER"
            )

        self.client = Client(self.account_sid, self.auth_token)

    def send_sms(
        self,
        to: str,
        message: str,
        short_url: Optional[str] = None
    ) -> dict:
        """
        Send a single SMS.

        Args:
            to: Recipient phone number (E.164 format, e.g., +819012345678)
            message: SMS message body
            short_url: Optional short URL to track clicks

        Returns:
            Dict with Twilio message info

        Raises:
            TwilioRestException: If sending fails
        """
        try:
            # Replace {url} placeholder with actual short URL
            if short_url and "{url}" in message:
                message = message.replace("{url}", short_url)

            # Send via Twilio
            twilio_message = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to
            )

            return {
                "sid": twilio_message.sid,
                "status": twilio_message.status,
                "to": to,
                "body": message,
                "sent_at": datetime.utcnow().isoformat()
            }

        except TwilioRestException as e:
            raise Exception(f"Failed to send SMS to {to}: {e.msg}")

    async def send_campaign(
        self,
        campaign: SMSCampaign,
        recipients: List[str],
        short_url: str,
        db
    ) -> dict:
        """
        Send SMS campaign to multiple recipients.

        Args:
            campaign: SMSCampaign object
            recipients: List of phone numbers
            short_url: Short URL to include in messages
            db: Database session

        Returns:
            Campaign results summary
        """
        results = {
            "total": len(recipients),
            "sent": 0,
            "failed": 0,
            "errors": []
        }

        # Update campaign status
        campaign.status = SMSStatus.SENT
        campaign.sent_at = datetime.utcnow()
        campaign.total_recipients = len(recipients)

        for phone_number in recipients:
            try:
                # Send SMS
                result = self.send_sms(
                    to=phone_number,
                    message=campaign.message_template,
                    short_url=short_url
                )

                # Create message record
                sms_message = SMSMessage(
                    campaign_id=campaign.id,
                    tenant_id=campaign.tenant_id,
                    phone_number=phone_number,
                    message_body=result["body"],
                    short_url=short_url,
                    twilio_sid=result["sid"],
                    status=SMSStatus.SENT,
                    sent_at=datetime.utcnow()
                )

                db.add(sms_message)
                results["sent"] += 1
                campaign.sent_count += 1

            except Exception as e:
                # Log failure
                sms_message = SMSMessage(
                    campaign_id=campaign.id,
                    tenant_id=campaign.tenant_id,
                    phone_number=phone_number,
                    message_body=campaign.message_template,
                    short_url=short_url,
                    status=SMSStatus.FAILED,
                    error_message=str(e)
                )

                db.add(sms_message)
                results["failed"] += 1
                results["errors"].append({
                    "phone": phone_number,
                    "error": str(e)
                })
                campaign.failed_count += 1

        # Mark campaign as completed
        campaign.completed_at = datetime.utcnow()

        # Commit all changes
        db.commit()

        return results

    def handle_status_callback(
        self,
        message_sid: str,
        message_status: str,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> dict:
        """
        Handle Twilio status callback webhook.

        Args:
            message_sid: Twilio message SID
            message_status: Message status (sent, delivered, failed, etc.)
            error_code: Optional error code
            error_message: Optional error message

        Returns:
            Processing result
        """
        # Map Twilio status to our SMSStatus
        status_mapping = {
            "queued": SMSStatus.PENDING,
            "sending": SMSStatus.PENDING,
            "sent": SMSStatus.SENT,
            "delivered": SMSStatus.DELIVERED,
            "failed": SMSStatus.FAILED,
            "undelivered": SMSStatus.UNDELIVERED
        }

        return {
            "message_sid": message_sid,
            "status": status_mapping.get(message_status, SMSStatus.FAILED),
            "error_code": error_code,
            "error_message": error_message,
            "updated_at": datetime.utcnow().isoformat()
        }

    def validate_phone_number(self, phone: str) -> tuple[bool, str]:
        """
        Validate phone number format.

        Args:
            phone: Phone number to validate

        Returns:
            Tuple of (is_valid, formatted_number or error_message)
        """
        # Remove spaces and dashes
        phone = phone.replace(" ", "").replace("-", "")

        # Check E.164 format
        if not phone.startswith("+"):
            return False, "Phone number must start with '+' (E.164 format)"

        if len(phone) < 10 or len(phone) > 15:
            return False, "Phone number length must be 10-15 digits"

        if not phone[1:].isdigit():
            return False, "Phone number must contain only digits after '+'"

        return True, phone

    def estimate_cost(self, num_messages: int, region: str = "JP") -> dict:
        """
        Estimate SMS campaign cost.

        Args:
            num_messages: Number of messages
            region: Region code (JP, US, etc.)

        Returns:
            Cost estimation
        """
        # Twilio pricing (approximate, as of 2024)
        # Prices vary by region and volume
        price_per_sms = {
            "JP": 0.073,  # $0.073 per SMS to Japan
            "US": 0.0079, # $0.0079 per SMS to US
            "DEFAULT": 0.05
        }

        price = price_per_sms.get(region, price_per_sms["DEFAULT"])
        total_cost = num_messages * price

        return {
            "num_messages": num_messages,
            "price_per_sms": price,
            "currency": "USD",
            "estimated_total": round(total_cost, 2),
            "note": "Actual costs may vary. Check Twilio pricing for your region."
        }


# Convenience functions
def send_assessment_sms(
    phone_number: str,
    assessment_title: str,
    short_url: str,
    tenant_name: str = "DiagnoLeads"
) -> dict:
    """
    Quick function to send assessment invitation via SMS.

    Args:
        phone_number: Recipient phone number
        assessment_title: Assessment title
        short_url: Short URL to assessment
        tenant_name: Tenant name for branding

    Returns:
        Send result
    """
    service = SMSService()

    message = (
        f"{tenant_name}から診断のご案内です。\n"
        f"「{assessment_title}」\n"
        f"{short_url}\n"
        f"※3分程度で完了します"
    )

    return service.send_sms(
        to=phone_number,
        message=message,
        short_url=short_url
    )
