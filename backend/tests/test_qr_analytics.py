"""Tests for QR Code Analytics and Tracking"""

from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assessment import Assessment
from app.models.lead import Lead
from app.models.qr_code import QRCode
from app.models.qr_code_scan import QRCodeScan


@pytest.fixture
async def test_qr_with_scans(db: AsyncSession, test_assessment: Assessment) -> tuple[QRCode, list[QRCodeScan]]:
    """Create test QR code with multiple scans"""
    # Create QR code
    qr = QRCode(
        tenant_id=test_assessment.tenant_id,
        assessment_id=test_assessment.id,
        name="Analytics Test QR",
        short_code="anl1234",
        short_url="https://dgnl.ds/anl1234",
        utm_source="test",
        style={},
        scan_count=0,
        unique_scan_count=0,
        enabled=True,
    )
    db.add(qr)
    await db.commit()
    await db.refresh(qr)

    # Create scans with different states
    scans = []
    now = datetime.utcnow()

    # Scan 1: Scanned only
    scan1 = QRCodeScan(
        qr_code_id=qr.id,
        user_agent="Mozilla/5.0",
        device_type="mobile",
        os="iOS",
        browser="Safari",
        ip_address="192.168.1.1",
        country="JP",
        city="Tokyo",
        scanned_at=now - timedelta(days=1),
        assessment_started=False,
        assessment_completed=False,
        lead_created=False,
    )
    scans.append(scan1)

    # Scan 2: Started
    scan2 = QRCodeScan(
        qr_code_id=qr.id,
        user_agent="Mozilla/5.0",
        device_type="desktop",
        os="Windows",
        browser="Chrome",
        ip_address="192.168.1.2",
        country="US",
        city="New York",
        scanned_at=now - timedelta(hours=12),
        assessment_started=True,
        assessment_completed=False,
        lead_created=False,
    )
    scans.append(scan2)

    # Scan 3: Completed
    scan3 = QRCodeScan(
        qr_code_id=qr.id,
        user_agent="Mozilla/5.0",
        device_type="tablet",
        os="Android",
        browser="Chrome",
        ip_address="192.168.1.3",
        country="JP",
        city="Osaka",
        scanned_at=now - timedelta(hours=6),
        assessment_started=True,
        assessment_completed=True,
        lead_created=False,
    )
    scans.append(scan3)

    # Scan 4: Converted to lead
    lead = Lead(
        tenant_id=test_assessment.tenant_id,
        name="Test Lead",
        email="test@example.com",
        status="new",
        score=75,
    )
    db.add(lead)
    await db.commit()
    await db.refresh(lead)

    scan4 = QRCodeScan(
        qr_code_id=qr.id,
        user_agent="Mozilla/5.0",
        device_type="mobile",
        os="iOS",
        browser="Safari",
        ip_address="192.168.1.4",
        country="JP",
        city="Tokyo",
        scanned_at=now - timedelta(hours=2),
        assessment_started=True,
        assessment_completed=True,
        lead_created=True,
        lead_id=lead.id,
    )
    scans.append(scan4)

    for scan in scans:
        db.add(scan)

    qr.scan_count = len(scans)
    qr.unique_scan_count = len(scans)

    await db.commit()

    return qr, scans


class TestScanTracking:
    """Tests for scan tracking updates"""

    @pytest.mark.asyncio
    async def test_mark_assessment_started(self, client: AsyncClient, db: AsyncSession, test_qr_with_scans: tuple):
        """Test marking assessment as started"""
        qr, scans = test_qr_with_scans
        scan = scans[0]  # Use scan that hasn't started

        response = await client.put(f"/api/v1/scans/{scan.id}/started")

        assert response.status_code == 204

        # Verify in database
        await db.refresh(scan)
        assert scan.assessment_started is True

    @pytest.mark.asyncio
    async def test_mark_assessment_completed(self, client: AsyncClient, db: AsyncSession, test_qr_with_scans: tuple):
        """Test marking assessment as completed"""
        qr, scans = test_qr_with_scans
        scan = scans[1]  # Use scan that started but not completed

        response = await client.put(f"/api/v1/scans/{scan.id}/completed")

        assert response.status_code == 204

        # Verify in database
        await db.refresh(scan)
        assert scan.assessment_completed is True
        assert scan.assessment_started is True  # Should auto-mark

    @pytest.mark.asyncio
    async def test_link_lead_to_scan(self, client: AsyncClient, db: AsyncSession, test_qr_with_scans: tuple):
        """Test linking lead to scan"""
        qr, scans = test_qr_with_scans
        scan = scans[2]  # Use completed scan

        # Create lead
        lead = Lead(
            tenant_id=qr.tenant_id,
            name="New Lead",
            email="new@example.com",
            status="new",
            score=80,
        )
        db.add(lead)
        await db.commit()
        await db.refresh(lead)

        response = await client.put(f"/api/v1/scans/{scan.id}/lead", params={"lead_id": str(lead.id)})

        assert response.status_code == 204

        # Verify in database
        await db.refresh(scan)
        assert scan.lead_id == lead.id
        assert scan.lead_created is True

    @pytest.mark.asyncio
    async def test_get_scan_details(self, client: AsyncClient, test_qr_with_scans: tuple):
        """Test getting scan details"""
        qr, scans = test_qr_with_scans
        scan = scans[3]  # Use fully converted scan

        response = await client.get(f"/api/v1/scans/{scan.id}")

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == str(scan.id)
        assert data["device_type"] == "mobile"
        assert data["os"] == "iOS"
        assert data["assessment_started"] is True
        assert data["assessment_completed"] is True
        assert data["lead_created"] is True


class TestQRAnalytics:
    """Tests for QR code analytics"""

    @pytest.mark.asyncio
    async def test_get_analytics(self, client: AsyncClient, test_qr_with_scans: tuple, auth_headers: dict):
        """Test getting QR code analytics"""
        qr, scans = test_qr_with_scans

        response = await client.get(f"/api/v1/qr-codes/{qr.id}/analytics", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Verify summary
        assert "summary" in data
        summary = data["summary"]
        assert summary["total_scans"] == 4
        assert summary["assessment_started"] == 3
        assert summary["assessment_completed"] == 2
        assert summary["leads_created"] == 1
        assert summary["conversion_rate"] == 50.0  # 2/4 = 50%

        # Verify scans by date
        assert "scans_by_date" in data
        assert len(data["scans_by_date"]) > 0

        # Verify scans by device
        assert "scans_by_device" in data
        devices = data["scans_by_device"]
        assert devices["mobile"] == 2
        assert devices["desktop"] == 1
        assert devices["tablet"] == 1

        # Verify scans by country
        assert "scans_by_country" in data
        countries = data["scans_by_country"]["country_scans"]
        assert "JP" in countries
        assert "US" in countries

        # Verify funnel
        assert "funnel" in data
        funnel = data["funnel"]
        assert funnel["scanned"] == 4
        assert funnel["started"] == 3
        assert funnel["completed"] == 2
        assert funnel["converted"] == 1

    @pytest.mark.asyncio
    async def test_analytics_with_custom_days(self, client: AsyncClient, test_qr_with_scans: tuple, auth_headers: dict):
        """Test analytics with custom date range"""
        qr, scans = test_qr_with_scans

        # Request last 7 days
        response = await client.get(f"/api/v1/qr-codes/{qr.id}/analytics?days=7", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "summary" in data

    @pytest.mark.asyncio
    async def test_analytics_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test analytics for non-existent QR code"""
        fake_id = uuid4()

        response = await client.get(f"/api/v1/qr-codes/{fake_id}/analytics", headers=auth_headers)

        assert response.status_code == 404


# Run tests with: pytest tests/test_qr_analytics.py -v
