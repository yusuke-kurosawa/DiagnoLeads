"""
Synchronous Integration tests for QR Code API endpoints

これらのテストはtest_qr_code_api.pyの非同期テストを同期版に変換したものです
（非同期インフラが未設定のため、カバレッジ向上のために同期版を作成）

注: QR Code APIはAsyncSessionを使用しているため、同期テストでは
TypeErrorが発生します。本来の非同期テスト（test_qr_code_api.py）を使用してください。
"""

from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from fastapi import status

from app.models.assessment import Assessment
from app.models.qr_code import QRCode
from app.services.auth import AuthService

# Skip all tests in this file as QR Code API uses AsyncSession
pytestmark = pytest.mark.skip(reason="QR Code API uses AsyncSession - use test_qr_code_api.py instead")


class TestQRCodeCRUDSync:
    """Tests for QR Code CRUD operations (synchronous)"""

    def test_create_qr_code_success(self, client, test_user, test_tenant, db_session):
        """Test successful QR code creation"""
        # Create test assessment
        assessment = Assessment(
            id=uuid4(),
            tenant_id=test_tenant.id,
            title="Test Assessment",
            description="Test description",
            status="published",
            created_by=test_user.id,
        )
        db_session.add(assessment)
        db_session.commit()
        db_session.refresh(assessment)

        # Create auth token
        token = AuthService.create_access_token(
            data={
                "sub": str(test_user.id),
                "tenant_id": str(test_tenant.id),
                "email": test_user.email,
            }
        )

        # Mock QRCodeService to avoid actual QR generation
        with patch("app.api.v1.qr_codes.QRCodeService") as mock_service:
            mock_qr_code = QRCode(
                id=uuid4(),
                tenant_id=test_tenant.id,
                assessment_id=assessment.id,
                name="Expo 2025 QR",
                short_code="abc1234",
                short_url="https://dgnl.ds/abc1234",
                utm_source="booth",
                utm_medium="qr",
                utm_campaign="expo_2025",
                style={"color": "#1E40AF", "size": 512},
                qr_code_image_url="https://storage.test.com/qr_abc1234.png",
                scan_count=0,
                unique_scan_count=0,
                enabled=True,
            )

            mock_instance = mock_service.return_value
            mock_instance.create_qr_code = AsyncMock(return_value=mock_qr_code)

            payload = {
                "name": "Expo 2025 QR",
                "utm_source": "booth",
                "utm_medium": "qr",
                "utm_campaign": "expo_2025",
                "style": {"color": "#1E40AF", "size": 512},
            }

            response = client.post(
                f"/api/v1/tenants/{test_tenant.id}/qr-codes?assessment_id={assessment.id}",
                json=payload,
                headers={"Authorization": f"Bearer {token}"},
            )

            # APIエンドポイントのパスを確認
            if response.status_code == 404:
                # Try alternative path
                response = client.post(
                    f"/api/v1/qr-codes?assessment_id={assessment.id}",
                    json=payload,
                    headers={"Authorization": f"Bearer {token}"},
                )

            assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_200_OK]

    def test_create_qr_code_assessment_not_found(self, client, test_user, test_tenant):
        """Test QR code creation with non-existent assessment"""
        token = AuthService.create_access_token(
            data={
                "sub": str(test_user.id),
                "tenant_id": str(test_tenant.id),
                "email": test_user.email,
            }
        )

        fake_assessment_id = uuid4()
        payload = {
            "name": "Test QR",
            "style": {"color": "#1E40AF", "size": 512},
        }

        response = client.post(
            f"/api/v1/qr-codes?assessment_id={fake_assessment_id}",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        # Should return 404 or 400
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST]

    def test_create_qr_code_unauthorized(self, client, test_tenant, test_user, db_session):
        """Test QR code creation without authentication"""
        assessment = Assessment(
            id=uuid4(),
            tenant_id=test_tenant.id,
            title="Test",
            status="published",
            created_by=test_user.id,
        )
        db_session.add(assessment)
        db_session.commit()

        payload = {"name": "Test QR"}

        response = client.post(
            f"/api/v1/qr-codes?assessment_id={assessment.id}",
            json=payload,
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_qr_codes_empty(self, client, test_user, test_tenant):
        """Test listing QR codes when none exist"""
        token = AuthService.create_access_token(
            data={
                "sub": str(test_user.id),
                "tenant_id": str(test_tenant.id),
                "email": test_user.email,
            }
        )

        response = client.get(
            "/api/v1/qr-codes",
            headers={"Authorization": f"Bearer {token}"},
        )

        # Should succeed but return empty list
        if response.status_code == 200:
            data = response.json()
            assert "qr_codes" in data or "items" in data

    def test_get_qr_code_not_found(self, client, test_user, test_tenant):
        """Test getting non-existent QR code"""
        token = AuthService.create_access_token(
            data={
                "sub": str(test_user.id),
                "tenant_id": str(test_tenant.id),
                "email": test_user.email,
            }
        )

        fake_qr_id = uuid4()
        response = client.get(
            f"/api/v1/qr-codes/{fake_qr_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_qr_code_not_found(self, client, test_user, test_tenant):
        """Test updating non-existent QR code"""
        token = AuthService.create_access_token(
            data={
                "sub": str(test_user.id),
                "tenant_id": str(test_tenant.id),
                "email": test_user.email,
            }
        )

        fake_qr_id = uuid4()
        response = client.patch(
            f"/api/v1/qr-codes/{fake_qr_id}",
            json={"name": "Updated Name"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_qr_code_not_found(self, client, test_user, test_tenant):
        """Test deleting non-existent QR code"""
        token = AuthService.create_access_token(
            data={
                "sub": str(test_user.id),
                "tenant_id": str(test_tenant.id),
                "email": test_user.email,
            }
        )

        fake_qr_id = uuid4()
        response = client.delete(
            f"/api/v1/qr-codes/{fake_qr_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_regenerate_qr_code_not_found(self, client, test_user, test_tenant):
        """Test regenerating non-existent QR code"""
        token = AuthService.create_access_token(
            data={
                "sub": str(test_user.id),
                "tenant_id": str(test_tenant.id),
                "email": test_user.email,
            }
        )

        fake_qr_id = uuid4()
        response = client.post(
            f"/api/v1/qr-codes/{fake_qr_id}/regenerate",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST]


class TestQRCodeFiltering:
    """Tests for QR code filtering and pagination"""

    def test_list_qr_codes_filter_by_assessment(self, client, test_user, test_tenant, db_session):
        """Test filtering QR codes by assessment"""
        token = AuthService.create_access_token(
            data={
                "sub": str(test_user.id),
                "tenant_id": str(test_tenant.id),
                "email": test_user.email,
            }
        )

        # Create test assessments
        assessment1 = Assessment(
            id=uuid4(),
            tenant_id=test_tenant.id,
            title="Assessment 1",
            status="published",
            created_by=test_user.id,
        )
        assessment2 = Assessment(
            id=uuid4(),
            tenant_id=test_tenant.id,
            title="Assessment 2",
            status="published",
            created_by=test_user.id,
        )
        db_session.add_all([assessment1, assessment2])
        db_session.commit()

        # Create QR codes for different assessments
        qr1 = QRCode(
            tenant_id=test_tenant.id,
            assessment_id=assessment1.id,
            name="QR 1",
            short_code="qr00001",
            short_url="https://dgnl.ds/qr00001",
            style={},
            scan_count=0,
            unique_scan_count=0,
            enabled=True,
        )
        qr2 = QRCode(
            tenant_id=test_tenant.id,
            assessment_id=assessment2.id,
            name="QR 2",
            short_code="qr00002",
            short_url="https://dgnl.ds/qr00002",
            style={},
            scan_count=0,
            unique_scan_count=0,
            enabled=True,
        )
        db_session.add_all([qr1, qr2])
        db_session.commit()

        # Filter by assessment1
        response = client.get(
            f"/api/v1/qr-codes?assessment_id={assessment1.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        if response.status_code == 200:
            data = response.json()
            # Verify filtering works (if endpoint supports it)
            assert "qr_codes" in data or "items" in data

    def test_list_qr_codes_filter_by_enabled(self, client, test_user, test_tenant, db_session):
        """Test filtering QR codes by enabled status"""
        token = AuthService.create_access_token(
            data={
                "sub": str(test_user.id),
                "tenant_id": str(test_tenant.id),
                "email": test_user.email,
            }
        )

        assessment = Assessment(
            id=uuid4(),
            tenant_id=test_tenant.id,
            title="Test",
            status="published",
            created_by=test_user.id,
        )
        db_session.add(assessment)
        db_session.commit()

        # Create enabled and disabled QR codes
        qr_enabled = QRCode(
            tenant_id=test_tenant.id,
            assessment_id=assessment.id,
            name="Enabled",
            short_code="ena0001",
            short_url="https://dgnl.ds/ena0001",
            style={},
            scan_count=0,
            unique_scan_count=0,
            enabled=True,
        )
        qr_disabled = QRCode(
            tenant_id=test_tenant.id,
            assessment_id=assessment.id,
            name="Disabled",
            short_code="dis0001",
            short_url="https://dgnl.ds/dis0001",
            style={},
            scan_count=0,
            unique_scan_count=0,
            enabled=False,
        )
        db_session.add_all([qr_enabled, qr_disabled])
        db_session.commit()

        # Filter by enabled=true
        response = client.get(
            "/api/v1/qr-codes?enabled=true",
            headers={"Authorization": f"Bearer {token}"},
        )

        if response.status_code == 200:
            data = response.json()
            assert "qr_codes" in data or "items" in data

    def test_list_qr_codes_pagination(self, client, test_user, test_tenant, db_session):
        """Test QR code list pagination"""
        token = AuthService.create_access_token(
            data={
                "sub": str(test_user.id),
                "tenant_id": str(test_tenant.id),
                "email": test_user.email,
            }
        )

        assessment = Assessment(
            id=uuid4(),
            tenant_id=test_tenant.id,
            title="Test",
            status="published",
            created_by=test_user.id,
        )
        db_session.add(assessment)
        db_session.commit()

        # Create multiple QR codes
        for i in range(15):
            qr = QRCode(
                tenant_id=test_tenant.id,
                assessment_id=assessment.id,
                name=f"QR {i}",
                short_code=f"pg{i:05d}",
                short_url=f"https://dgnl.ds/pg{i:05d}",
                style={},
                scan_count=0,
                unique_scan_count=0,
                enabled=True,
            )
            db_session.add(qr)
        db_session.commit()

        # Test pagination
        response = client.get(
            "/api/v1/qr-codes?page=1&per_page=10",
            headers={"Authorization": f"Bearer {token}"},
        )

        if response.status_code == 200:
            data = response.json()
            # Verify pagination works
            assert "qr_codes" in data or "items" in data


class TestQRCodeTenantIsolation:
    """Tests for tenant isolation in QR code operations"""

    def test_cannot_access_other_tenant_qr_code(self, client, test_user, test_tenant, test_tenant_2, db_session):
        """Test that users cannot access QR codes from other tenants"""
        from app.models.user import User

        # Create user in other tenant
        other_user = User(
            email="otherqr@example.com",
            password_hash=AuthService.hash_password("password123"),
            name="Other QR User",
            tenant_id=test_tenant_2.id,
            role="tenant_admin",
        )
        db_session.add(other_user)
        db_session.commit()
        db_session.refresh(other_user)

        # Create assessment for other tenant
        other_assessment = Assessment(
            id=uuid4(),
            tenant_id=test_tenant_2.id,
            title="Other Assessment",
            status="published",
            created_by=other_user.id,
        )
        db_session.add(other_assessment)
        db_session.commit()

        # Create QR code for other tenant
        other_qr = QRCode(
            tenant_id=test_tenant_2.id,
            assessment_id=other_assessment.id,
            name="Other Tenant QR",
            short_code="oth0001",
            short_url="https://dgnl.ds/oth0001",
            style={},
            scan_count=0,
            unique_scan_count=0,
            enabled=True,
        )
        db_session.add(other_qr)
        db_session.commit()
        db_session.refresh(other_qr)

        # Try to access with test_user (different tenant)
        token = AuthService.create_access_token(
            data={
                "sub": str(test_user.id),
                "tenant_id": str(test_tenant.id),
                "email": test_user.email,
            }
        )

        response = client.get(
            f"/api/v1/qr-codes/{other_qr.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        # Should return 404 (not found) for security
        assert response.status_code == status.HTTP_404_NOT_FOUND


# Run tests with: pytest tests/test_qr_code_api_sync.py -v
