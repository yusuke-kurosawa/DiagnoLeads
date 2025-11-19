"""
Advanced Tests for QR Code Service

Additional test coverage for edge cases and error handling
Target: 100% coverage for qr_code_service.py
"""

import io
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from PIL import Image

from app.services.qr_code_service import QRCodeService


class TestQRCodeServiceImageConversion:
    """Tests for image conversion methods"""

    @pytest.fixture
    def service(self, db_session):
        """Create service instance"""
        return QRCodeService(db_session)

    def test_qr_image_to_bytes_jpeg(self, service):
        """Test converting image to JPEG bytes"""
        # Create a simple image
        img = Image.new("RGB", (100, 100), color="red")

        # Convert to JPEG
        result = service.qr_image_to_bytes(img, format="JPEG")

        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_qr_image_to_bytes_different_sizes(self, service):
        """Test converting images of different sizes"""
        # Small image
        small_img = Image.new("RGB", (50, 50), color="blue")
        small_bytes = service.qr_image_to_bytes(small_img)

        # Large image
        large_img = Image.new("RGB", (1000, 1000), color="green")
        large_bytes = service.qr_image_to_bytes(large_img)

        # Larger image should produce more bytes
        assert len(large_bytes) > len(small_bytes)


class TestQRCodeServiceLogoHandling:
    """Tests for logo handling in QR codes"""

    @pytest.fixture
    def service(self, db_session):
        """Create service instance"""
        return QRCodeService(db_session)

    @patch("builtins.open")
    @patch("app.services.qr_code_service.Image.open")
    def test_generate_qr_with_logo_rgba_mode(self, mock_image_open, mock_open, service):
        """Test adding logo with RGBA (transparency) mode"""
        # Generate base QR code
        qr_img = service.generate_qr_image("https://example.com")

        # Create mock RGBA logo
        mock_logo = MagicMock()
        mock_logo.mode = "RGBA"  # Has alpha channel
        mock_logo.size = (100, 100)
        mock_logo.resize.return_value = mock_logo

        mock_image_open.return_value = mock_logo
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Generate with logo
        result = service.generate_qr_with_logo("https://example.com", "logo.png")

        assert isinstance(result, Image.Image)
        # Verify logo was opened
        mock_image_open.assert_called_once()

    @patch("builtins.open")
    @patch("app.services.qr_code_service.Image.open")
    def test_generate_qr_with_logo_rgb_mode(self, mock_image_open, mock_open, service):
        """Test adding logo with RGB (no transparency) mode"""
        # Generate base QR code
        qr_img = service.generate_qr_image("https://example.com")

        # Create mock RGB logo
        mock_logo = MagicMock()
        mock_logo.mode = "RGB"  # No alpha channel
        mock_logo.size = (100, 100)
        mock_logo.resize.return_value = mock_logo

        mock_image_open.return_value = mock_logo
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Generate with logo
        result = service.generate_qr_with_logo("https://example.com", "logo.png")

        assert isinstance(result, Image.Image)


class TestQRCodeServiceErrorCorrection:
    """Tests for different error correction levels"""

    @pytest.fixture
    def service(self, db_session):
        """Create service instance"""
        return QRCodeService(db_session)

    def test_generate_qr_with_low_error_correction(self, service):
        """Test QR generation with low error correction"""
        img = service.generate_qr_image("https://example.com", error_correction="L")

        assert isinstance(img, Image.Image)

    def test_generate_qr_with_medium_error_correction(self, service):
        """Test QR generation with medium error correction"""
        img = service.generate_qr_image("https://example.com", error_correction="M")

        assert isinstance(img, Image.Image)

    def test_generate_qr_with_quartile_error_correction(self, service):
        """Test QR generation with quartile error correction"""
        img = service.generate_qr_image("https://example.com", error_correction="Q")

        assert isinstance(img, Image.Image)

    def test_generate_qr_with_high_error_correction(self, service):
        """Test QR generation with high error correction"""
        img = service.generate_qr_image("https://example.com", error_correction="H")

        assert isinstance(img, Image.Image)


class TestQRCodeServiceURLHandling:
    """Tests for URL handling in QR codes"""

    @pytest.fixture
    def service(self, db_session):
        """Create service instance"""
        return QRCodeService(db_session)

    def test_generate_qr_with_long_url(self, service):
        """Test QR generation with very long URL"""
        long_url = "https://example.com/" + "a" * 500
        img = service.generate_qr_image(long_url)

        assert isinstance(img, Image.Image)

    def test_generate_qr_with_special_characters_in_url(self, service):
        """Test QR generation with special characters"""
        url = "https://example.com/path?param=value&other=データ"
        img = service.generate_qr_image(url)

        assert isinstance(img, Image.Image)

    def test_generate_qr_with_unicode_url(self, service):
        """Test QR generation with Unicode characters"""
        url = "https://example.com/日本語/パス"
        img = service.generate_qr_image(url)

        assert isinstance(img, Image.Image)


class TestQRCodeServiceShortCodeEdgeCases:
    """Tests for short code edge cases"""

    @pytest.fixture
    def service(self, db_session):
        """Create service instance"""
        return QRCodeService(db_session)

    def test_generate_short_code_custom_length(self, service):
        """Test generating short code with custom length"""
        short_code = service.generate_short_code(length=10)

        assert len(short_code) == 10
        assert short_code.isalnum()

    def test_generate_short_code_minimum_length(self, service):
        """Test generating short code with minimum length"""
        short_code = service.generate_short_code(length=1)

        assert len(short_code) == 1

    def test_generate_short_code_maximum_length(self, service):
        """Test generating short code with large length"""
        short_code = service.generate_short_code(length=50)

        assert len(short_code) == 50


class TestQRCodeServiceStorageUpload:
    """Tests for storage upload functionality"""

    @pytest.fixture
    def service(self, db_session):
        """Create service instance"""
        return QRCodeService(db_session)

    @pytest.mark.asyncio
    async def test_upload_to_storage_returns_url(self, service):
        """Test that upload_to_storage returns placeholder URL"""
        file_data = b"test image data"
        filename = "test_qr.png"

        result = await service.upload_to_storage(file_data, filename)

        assert isinstance(result, str)
        assert filename in result

    @pytest.mark.asyncio
    async def test_upload_to_storage_different_content_types(self, service):
        """Test upload with different content types"""
        file_data = b"test data"

        # PNG
        result_png = await service.upload_to_storage(file_data, "test.png", "image/png")
        assert "test.png" in result_png

        # JPEG
        result_jpeg = await service.upload_to_storage(file_data, "test.jpg", "image/jpeg")
        assert "test.jpg" in result_jpeg


class TestQRCodeServiceColorHandling:
    """Tests for custom color handling"""

    @pytest.fixture
    def service(self, db_session):
        """Create service instance"""
        return QRCodeService(db_session)

    def test_generate_qr_with_hex_color(self, service):
        """Test QR generation with hex color"""
        img = service.generate_qr_image("https://example.com", color="#FF0000")

        assert isinstance(img, Image.Image)

    def test_generate_qr_with_different_colors(self, service):
        """Test QR generation with various colors"""
        colors = ["#000000", "#FFFFFF", "#FF5733", "#33FF57"]

        for color in colors:
            img = service.generate_qr_image("https://example.com", color=color)
            assert isinstance(img, Image.Image)
