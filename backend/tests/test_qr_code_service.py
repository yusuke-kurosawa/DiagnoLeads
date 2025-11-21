"""Unit tests for QRCode Service"""

from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

import pytest
from PIL import Image

from app.models.assessment import Assessment
from app.models.qr_code import QRCode
from app.models.tenant import Tenant
from app.schemas.qr_code import QRCodeCreate, QRCodeStyleBase
from app.services.qr_code_service import QRCodeService


class TestShortCodeGeneration:
    """Tests for short code generation logic"""

    @pytest.fixture
    def service(self):
        """Create service with mock database"""
        mock_db = AsyncMock()
        return QRCodeService(db=mock_db)

    def test_generate_short_code_length(self, service):
        """Test short code has correct length"""
        code = service.generate_short_code(length=7)
        assert len(code) == 7

    def test_generate_short_code_alphanumeric(self, service):
        """Test short code contains only alphanumeric characters"""
        code = service.generate_short_code(length=10)
        assert code.isalnum()

    def test_generate_short_code_uniqueness(self, service):
        """Test that multiple calls generate different codes (probabilistic)"""
        codes = set()
        for _ in range(100):
            code = service.generate_short_code()
            codes.add(code)

        # With 62^7 possible codes, 100 should be unique
        assert len(codes) == 100

    @pytest.mark.asyncio
    async def test_is_short_code_unique_true(self, service):
        """Test uniqueness check when code is unique"""
        # Mock database to return no results
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        service.db.execute = AsyncMock(return_value=mock_result)

        is_unique = await service.is_short_code_unique("abc123")
        assert is_unique is True

    @pytest.mark.asyncio
    async def test_is_short_code_unique_false(self, service):
        """Test uniqueness check when code exists"""
        # Mock database to return existing code
        existing_qr = QRCode(short_code="abc123")
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = existing_qr
        service.db.execute = AsyncMock(return_value=mock_result)

        is_unique = await service.is_short_code_unique("abc123")
        assert is_unique is False

    @pytest.mark.asyncio
    async def test_generate_unique_short_code_success(self, service):
        """Test successful unique code generation"""
        # Mock database to return no results (unique)
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        service.db.execute = AsyncMock(return_value=mock_result)

        code = await service.generate_unique_short_code()
        assert len(code) == 7
        assert code.isalnum()

    @pytest.mark.asyncio
    async def test_generate_unique_short_code_collision_handling(self, service):
        """Test collision handling in unique code generation"""
        # Mock: first 3 attempts return existing codes, 4th is unique
        call_count = 0

        def mock_execute(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            mock_result = Mock()
            if call_count < 4:
                # Return existing code
                mock_result.scalar_one_or_none.return_value = QRCode(short_code="test")
            else:
                # Return None (unique)
                mock_result.scalar_one_or_none.return_value = None
            return mock_result

        service.db.execute = AsyncMock(side_effect=mock_execute)

        code = await service.generate_unique_short_code()
        assert len(code) == 7
        assert call_count == 4

    @pytest.mark.asyncio
    async def test_generate_unique_short_code_max_attempts_exceeded(self, service):
        """Test exception when max attempts exceeded"""
        # Mock database to always return existing code
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = QRCode(short_code="test")
        service.db.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(RuntimeError, match="Failed to generate unique short code"):
            await service.generate_unique_short_code(max_attempts=5)


class TestQRImageGeneration:
    """Tests for QR code image generation"""

    @pytest.fixture
    def service(self):
        """Create service with mock database"""
        mock_db = AsyncMock()
        return QRCodeService(db=mock_db)

    def test_generate_qr_image_returns_image(self, service):
        """Test QR image generation returns PIL Image"""
        url = "https://example.com/test"
        img = service.generate_qr_image(url)

        assert isinstance(img, Image.Image)
        assert img.size == (512, 512)  # Default size

    def test_generate_qr_image_custom_size(self, service):
        """Test QR image with custom size"""
        url = "https://example.com/test"
        img = service.generate_qr_image(url, size=256)

        assert img.size == (256, 256)

    def test_generate_qr_image_custom_color(self, service):
        """Test QR image with custom color"""
        url = "https://example.com/test"
        # Color is applied during generation, hard to test directly
        # Just verify it doesn't raise exception
        img = service.generate_qr_image(url, color="#FF0000")

        assert isinstance(img, Image.Image)

    def test_qr_image_to_bytes_png(self, service):
        """Test converting QR image to PNG bytes"""
        url = "https://example.com/test"
        img = service.generate_qr_image(url, size=256)

        img_bytes = service.qr_image_to_bytes(img, format="PNG")

        assert isinstance(img_bytes, bytes)
        assert len(img_bytes) > 0
        # Check PNG magic bytes
        assert img_bytes[:8] == b"\x89PNG\r\n\x1a\n"

    def test_generate_qr_with_logo_no_logo(self, service):
        """Test QR generation without logo"""
        url = "https://example.com/test"
        img = service.generate_qr_with_logo(url, logo_path=None)

        assert isinstance(img, Image.Image)

    @patch("app.services.qr_code_service.Image.open")
    def test_generate_qr_with_logo_success(self, mock_open, service):
        """Test QR generation with logo"""
        # Create mock logo
        mock_logo = Image.new("RGB", (100, 100), color="red")
        mock_open.return_value = mock_logo

        url = "https://example.com/test"
        img = service.generate_qr_with_logo(url, logo_path="/fake/logo.png")

        assert isinstance(img, Image.Image)
        mock_open.assert_called_once_with("/fake/logo.png")

    @patch("app.services.qr_code_service.Image.open")
    def test_generate_qr_with_logo_failure_fallback(self, mock_open, service):
        """Test QR generation falls back when logo fails"""
        # Mock logo opening to raise exception
        mock_open.side_effect = IOError("File not found")

        url = "https://example.com/test"
        img = service.generate_qr_with_logo(url, logo_path="/fake/logo.png")

        # Should still return valid image without logo
        assert isinstance(img, Image.Image)


class TestCloudStorageUpload:
    """Tests for cloud storage upload"""

    @pytest.fixture
    def service(self):
        """Create service with mock database"""
        mock_db = AsyncMock()
        return QRCodeService(db=mock_db)

    @pytest.mark.asyncio
    async def test_upload_to_storage_placeholder(self, service):
        """Test storage upload returns placeholder URL"""
        file_data = b"fake image data"
        filename = "test.png"

        url = await service.upload_to_storage(file_data, filename)

        assert isinstance(url, str)
        assert filename in url
        assert url.startswith("https://")


class TestCompleteQRCodeCreation:
    """Tests for complete QR code creation flow"""

    @pytest.fixture
    def service(self):
        """Create service with mock database"""
        mock_db = AsyncMock()
        return QRCodeService(db=mock_db)

    @pytest.fixture
    def mock_tenant(self):
        """Create mock tenant"""
        return Tenant(id=uuid4(), name="Test Company", slug="test-company")

    @pytest.fixture
    def mock_assessment(self, mock_tenant):
        """Create mock assessment"""
        return Assessment(
            id=uuid4(),
            tenant_id=mock_tenant.id,
            title="Test Assessment",
            status="published",
        )

    @pytest.fixture
    def qr_create_data(self):
        """Create QR code creation data"""
        return QRCodeCreate(
            name="Test QR Code",
            utm_source="booth",
            utm_medium="qr",
            utm_campaign="expo_2025",
            style=QRCodeStyleBase(color="#1E40AF", size=512),
        )

    @pytest.mark.asyncio
    async def test_create_qr_code_success(self, service, mock_tenant, mock_assessment, qr_create_data):
        """Test successful QR code creation"""

        # Mock database queries
        def mock_execute(query):
            mock_result = Mock()
            # Determine which query based on call order
            if not hasattr(mock_execute, "call_count"):
                mock_execute.call_count = 0

            mock_execute.call_count += 1

            if mock_execute.call_count == 1:
                # Tenant query
                mock_result.scalar_one_or_none.return_value = mock_tenant
            elif mock_execute.call_count == 2:
                # Assessment query
                mock_result.scalar_one_or_none.return_value = mock_assessment
            else:
                # Short code uniqueness check
                mock_result.scalar_one_or_none.return_value = None

            return mock_result

        service.db.execute = AsyncMock(side_effect=mock_execute)
        service.db.add = Mock()  # db.add() is synchronous
        service.db.commit = AsyncMock()
        service.db.refresh = AsyncMock()

        # Mock storage upload
        service.upload_to_storage = AsyncMock(return_value="https://storage.test.com/qr_abc123.png")

        # Create QR code
        qr_code = await service.create_qr_code(
            tenant_id=mock_tenant.id,
            assessment_id=mock_assessment.id,
            qr_data=qr_create_data,
        )

        # Verify result
        assert isinstance(qr_code, QRCode)
        assert qr_code.name == "Test QR Code"
        assert qr_code.tenant_id == mock_tenant.id
        assert qr_code.assessment_id == mock_assessment.id
        assert qr_code.utm_source == "booth"
        assert qr_code.utm_campaign == "expo_2025"
        assert len(qr_code.short_code) == 7
        assert qr_code.short_url.startswith("https://dgnl.ds/")

    @pytest.mark.asyncio
    async def test_create_qr_code_tenant_not_found(self, service, qr_create_data):
        """Test QR code creation fails when tenant not found"""
        # Mock database to return None for tenant
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        service.db.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(ValueError, match="Tenant .* not found"):
            await service.create_qr_code(tenant_id=uuid4(), assessment_id=uuid4(), qr_data=qr_create_data)

    @pytest.mark.asyncio
    async def test_create_qr_code_assessment_not_found(self, service, mock_tenant, qr_create_data):
        """Test QR code creation fails when assessment not found"""

        # Mock: tenant found, assessment not found
        def mock_execute(query):
            mock_result = Mock()
            if not hasattr(mock_execute, "called"):
                # First call: tenant found
                mock_execute.called = True
                mock_result.scalar_one_or_none.return_value = mock_tenant
            else:
                # Second call: assessment not found
                mock_result.scalar_one_or_none.return_value = None
            return mock_result

        service.db.execute = AsyncMock(side_effect=mock_execute)

        with pytest.raises(ValueError, match="Assessment .* not found"):
            await service.create_qr_code(tenant_id=mock_tenant.id, assessment_id=uuid4(), qr_data=qr_create_data)


# Run tests with: pytest tests/test_qr_code_service.py -v
