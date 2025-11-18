"""Integration tests for QR Code API endpoints"""

import pytest
from uuid import uuid4
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.qr_code import QRCode
from app.models.tenant import Tenant
from app.models.assessment import Assessment
from app.models.user import User


@pytest.fixture
async def test_tenant(db: AsyncSession) -> Tenant:
    """Create test tenant"""
    tenant = Tenant(
        id=uuid4(),
        name="Test Company",
        slug="test-company",
        plan="pro"
    )
    db.add(tenant)
    await db.commit()
    await db.refresh(tenant)
    return tenant


@pytest.fixture
async def test_user(db: AsyncSession, test_tenant: Tenant) -> User:
    """Create test user"""
    user = User(
        id=uuid4(),
        tenant_id=test_tenant.id,
        email="test@example.com",
        hashed_password="hashed_password",
        full_name="Test User",
        role="admin"
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def test_assessment(db: AsyncSession, test_tenant: Tenant, test_user: User) -> Assessment:
    """Create test assessment"""
    assessment = Assessment(
        id=uuid4(),
        tenant_id=test_tenant.id,
        title="Test Assessment",
        description="Test description",
        status="published",
        created_by=test_user.id
    )
    db.add(assessment)
    await db.commit()
    await db.refresh(assessment)
    return assessment


@pytest.fixture
async def auth_headers(test_user: User) -> dict:
    """Create authentication headers"""
    # TODO: Generate actual JWT token
    # For now, return mock headers
    return {
        "Authorization": f"Bearer mock_token_{test_user.id}"
    }


class TestQRCodeCRUD:
    """Tests for QR Code CRUD operations"""

    @pytest.mark.asyncio
    async def test_create_qr_code(
        self,
        client: AsyncClient,
        db: AsyncSession,
        test_assessment: Assessment,
        auth_headers: dict
    ):
        """Test QR code creation"""
        payload = {
            "name": "Expo 2025 QR",
            "utm_source": "booth",
            "utm_medium": "qr",
            "utm_campaign": "expo_2025",
            "style": {
                "color": "#1E40AF",
                "size": 512
            }
        }
        
        response = await client.post(
            f"/api/v1/qr-codes?assessment_id={test_assessment.id}",
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["name"] == "Expo 2025 QR"
        assert data["utm_source"] == "booth"
        assert data["utm_campaign"] == "expo_2025"
        assert len(data["short_code"]) == 7
        assert data["short_url"].startswith("https://")
        assert data["enabled"] is True

    @pytest.mark.asyncio
    async def test_list_qr_codes(
        self,
        client: AsyncClient,
        db: AsyncSession,
        test_assessment: Assessment,
        auth_headers: dict
    ):
        """Test QR code listing"""
        # Create test QR codes
        for i in range(3):
            qr = QRCode(
                tenant_id=test_assessment.tenant_id,
                assessment_id=test_assessment.id,
                name=f"Test QR {i}",
                short_code=f"test{i:03d}",
                short_url=f"https://dgnl.ds/test{i:03d}",
                style={},
                scan_count=0,
                unique_scan_count=0,
                enabled=True
            )
            db.add(qr)
        
        await db.commit()
        
        # List QR codes
        response = await client.get(
            "/api/v1/qr-codes",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total"] >= 3
        assert len(data["qr_codes"]) >= 3
        assert data["page"] == 1

    @pytest.mark.asyncio
    async def test_get_qr_code(
        self,
        client: AsyncClient,
        db: AsyncSession,
        test_assessment: Assessment,
        auth_headers: dict
    ):
        """Test getting single QR code"""
        # Create test QR code
        qr = QRCode(
            tenant_id=test_assessment.tenant_id,
            assessment_id=test_assessment.id,
            name="Test QR",
            short_code="abc1234",
            short_url="https://dgnl.ds/abc1234",
            style={},
            scan_count=10,
            unique_scan_count=8,
            enabled=True
        )
        db.add(qr)
        await db.commit()
        await db.refresh(qr)
        
        # Get QR code
        response = await client.get(
            f"/api/v1/qr-codes/{qr.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == str(qr.id)
        assert data["name"] == "Test QR"
        assert data["short_code"] == "abc1234"
        assert data["scan_count"] == 10

    @pytest.mark.asyncio
    async def test_update_qr_code(
        self,
        client: AsyncClient,
        db: AsyncSession,
        test_assessment: Assessment,
        auth_headers: dict
    ):
        """Test QR code update"""
        # Create test QR code
        qr = QRCode(
            tenant_id=test_assessment.tenant_id,
            assessment_id=test_assessment.id,
            name="Old Name",
            short_code="xyz9999",
            short_url="https://dgnl.ds/xyz9999",
            style={},
            scan_count=0,
            unique_scan_count=0,
            enabled=True
        )
        db.add(qr)
        await db.commit()
        await db.refresh(qr)
        
        # Update QR code
        response = await client.patch(
            f"/api/v1/qr-codes/{qr.id}",
            json={"name": "New Name", "enabled": False},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "New Name"
        assert data["enabled"] is False

    @pytest.mark.asyncio
    async def test_delete_qr_code(
        self,
        client: AsyncClient,
        db: AsyncSession,
        test_assessment: Assessment,
        auth_headers: dict
    ):
        """Test QR code deletion"""
        # Create test QR code
        qr = QRCode(
            tenant_id=test_assessment.tenant_id,
            assessment_id=test_assessment.id,
            name="To Delete",
            short_code="del9999",
            short_url="https://dgnl.ds/del9999",
            style={},
            scan_count=0,
            unique_scan_count=0,
            enabled=True
        )
        db.add(qr)
        await db.commit()
        await db.refresh(qr)
        
        # Delete QR code
        response = await client.delete(
            f"/api/v1/qr-codes/{qr.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204


class TestQRCodeRedirect:
    """Tests for QR code redirect and tracking"""

    @pytest.mark.asyncio
    async def test_redirect_qr_code(
        self,
        client: AsyncClient,
        db: AsyncSession,
        test_assessment: Assessment
    ):
        """Test QR code redirect"""
        # Create test QR code
        qr = QRCode(
            tenant_id=test_assessment.tenant_id,
            assessment_id=test_assessment.id,
            name="Redirect Test",
            short_code="rdr1234",
            short_url="https://dgnl.ds/rdr1234",
            utm_source="test",
            utm_medium="qr",
            style={},
            scan_count=0,
            unique_scan_count=0,
            enabled=True
        )
        db.add(qr)
        await db.commit()
        
        # Follow redirect (allow_redirects=False to check redirect response)
        response = await client.get(
            "/rdr1234",
            follow_redirects=False,
            headers={"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0)"}
        )
        
        assert response.status_code == 307  # Temporary Redirect
        assert "location" in response.headers
        
        redirect_url = response.headers["location"]
        assert str(test_assessment.id) in redirect_url
        assert "utm_source=test" in redirect_url
        assert "qr=rdr1234" in redirect_url
        
        # Verify scan was tracked
        await db.refresh(qr)
        assert qr.scan_count == 1

    @pytest.mark.asyncio
    async def test_redirect_disabled_qr(
        self,
        client: AsyncClient,
        db: AsyncSession,
        test_assessment: Assessment
    ):
        """Test redirect fails for disabled QR code"""
        # Create disabled QR code
        qr = QRCode(
            tenant_id=test_assessment.tenant_id,
            assessment_id=test_assessment.id,
            name="Disabled",
            short_code="dis1234",
            short_url="https://dgnl.ds/dis1234",
            style={},
            scan_count=0,
            unique_scan_count=0,
            enabled=False
        )
        db.add(qr)
        await db.commit()
        
        # Try to redirect
        response = await client.get("/dis1234", follow_redirects=False)
        
        assert response.status_code == 410  # Gone

    @pytest.mark.asyncio
    async def test_redirect_not_found(self, client: AsyncClient):
        """Test redirect fails for non-existent QR code"""
        response = await client.get("/notfound", follow_redirects=False)
        
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_preview_redirect_url(
        self,
        client: AsyncClient,
        db: AsyncSession,
        test_assessment: Assessment
    ):
        """Test preview redirect URL"""
        # Create test QR code
        qr = QRCode(
            tenant_id=test_assessment.tenant_id,
            assessment_id=test_assessment.id,
            name="Preview Test",
            short_code="prv1234",
            short_url="https://dgnl.ds/prv1234",
            utm_source="preview",
            style={},
            scan_count=5,
            unique_scan_count=3,
            enabled=True
        )
        db.add(qr)
        await db.commit()
        
        # Preview URL
        response = await client.get("/api/v1/qr-codes/prv1234/preview")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["short_code"] == "prv1234"
        assert data["enabled"] is True
        assert data["scan_count"] == 5
        assert "redirect_url" in data
        assert str(test_assessment.id) in data["redirect_url"]


# Run tests with: pytest tests/test_qr_code_api.py -v
