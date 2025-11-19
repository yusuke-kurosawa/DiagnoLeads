"""QR Code Service

Handles QR code generation, short URL creation, and cloud storage uploads.
"""

import io
import secrets
import string
from typing import Optional
from uuid import UUID

import qrcode
from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.qr_code import QRCode
from app.models.tenant import Tenant
from app.models.assessment import Assessment
from app.schemas.qr_code import QRCodeCreate


class QRCodeService:
    """Service for QR code generation and management."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ========================================================================
    # Short Code Generation
    # ========================================================================

    def generate_short_code(self, length: int = 7) -> str:
        """Generate a unique short code for QR code URL.

        Args:
            length: Length of the short code (default: 7)

        Returns:
            Alphanumeric short code (e.g., "a3bC7xZ")
        """
        # Use alphanumeric characters (uppercase, lowercase, digits)
        characters = string.ascii_letters + string.digits
        short_code = "".join(secrets.choice(characters) for _ in range(length))
        return short_code

    async def is_short_code_unique(self, short_code: str) -> bool:
        """Check if a short code is unique in the database.

        Args:
            short_code: The short code to check

        Returns:
            True if unique, False if already exists
        """
        result = await self.db.execute(
            select(QRCode).where(QRCode.short_code == short_code)
        )
        existing = result.scalar_one_or_none()
        return existing is None

    async def generate_unique_short_code(self, max_attempts: int = 10) -> str:
        """Generate a unique short code with collision checking.

        Args:
            max_attempts: Maximum number of generation attempts

        Returns:
            Unique short code

        Raises:
            RuntimeError: If unable to generate unique code after max_attempts
        """
        for attempt in range(max_attempts):
            short_code = self.generate_short_code()
            if await self.is_short_code_unique(short_code):
                return short_code

        raise RuntimeError(
            f"Failed to generate unique short code after {max_attempts} attempts"
        )

    # ========================================================================
    # QR Code Image Generation
    # ========================================================================

    def generate_qr_image(
        self,
        url: str,
        color: str = "#1E40AF",
        size: int = 512,
        error_correction: str = "H",
    ) -> Image.Image:
        """Generate QR code image using qrcode library.

        Args:
            url: URL to encode in QR code
            color: QR code color in hex format (default: blue)
            size: Image size in pixels (default: 512)
            error_correction: Error correction level (L, M, Q, H)

        Returns:
            PIL Image object
        """
        # Map error correction level
        error_correction_map = {
            "L": qrcode.constants.ERROR_CORRECT_L,  # ~7% correction
            "M": qrcode.constants.ERROR_CORRECT_M,  # ~15% correction
            "Q": qrcode.constants.ERROR_CORRECT_Q,  # ~25% correction
            "H": qrcode.constants.ERROR_CORRECT_H,  # ~30% correction
        }

        error_level = error_correction_map.get(
            error_correction.upper(), qrcode.constants.ERROR_CORRECT_H
        )

        # Create QR code
        qr = qrcode.QRCode(
            version=1,  # Auto-adjust version based on data
            error_correction=error_level,
            box_size=10,
            border=4,
        )

        qr.add_data(url)
        qr.make(fit=True)

        # Generate image
        img = qr.make_image(fill_color=color, back_color="white")

        # Resize to desired size
        img = img.resize((size, size), Image.Resampling.LANCZOS)

        return img

    def generate_qr_with_logo(
        self,
        url: str,
        logo_path: Optional[str] = None,
        color: str = "#1E40AF",
        size: int = 512,
    ) -> Image.Image:
        """Generate QR code with optional logo in the center.

        Args:
            url: URL to encode
            logo_path: Path to logo image file (optional)
            color: QR code color
            size: Image size in pixels

        Returns:
            PIL Image with logo overlay
        """
        # Generate base QR code
        qr_img = self.generate_qr_image(url, color, size, error_correction="H")

        # If no logo, return base QR code
        if not logo_path:
            return qr_img

        # Open and process logo
        try:
            logo = Image.open(logo_path)

            # Calculate logo size (20% of QR code size)
            logo_size = int(size * 0.2)
            logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)

            # Create white background for logo (for better visibility)
            logo_bg_size = int(logo_size * 1.2)
            logo_bg = Image.new("RGB", (logo_bg_size, logo_bg_size), "white")

            # Calculate position to center logo
            logo_pos = (
                (qr_img.size[0] - logo_bg_size) // 2,
                (qr_img.size[1] - logo_bg_size) // 2,
            )

            logo_offset = (
                (logo_bg_size - logo_size) // 2,
                (logo_bg_size - logo_size) // 2,
            )

            # Paste logo background and logo
            qr_img.paste(logo_bg, logo_pos)

            # Handle transparency if logo has alpha channel
            if logo.mode == "RGBA":
                qr_img.paste(
                    logo,
                    (logo_pos[0] + logo_offset[0], logo_pos[1] + logo_offset[1]),
                    logo,
                )
            else:
                qr_img.paste(
                    logo, (logo_pos[0] + logo_offset[0], logo_pos[1] + logo_offset[1])
                )

            return qr_img

        except Exception as e:
            # If logo processing fails, return QR code without logo
            print(f"Warning: Failed to add logo to QR code: {e}")
            return qr_img

    def qr_image_to_bytes(self, img: Image.Image, format: str = "PNG") -> bytes:
        """Convert PIL Image to bytes.

        Args:
            img: PIL Image object
            format: Image format (PNG, JPEG, etc.)

        Returns:
            Image as bytes
        """
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format=format)
        img_byte_arr.seek(0)
        return img_byte_arr.getvalue()

    # ========================================================================
    # Cloud Storage Upload (Placeholder)
    # ========================================================================

    async def upload_to_storage(
        self, file_data: bytes, filename: str, content_type: str = "image/png"
    ) -> str:
        """Upload file to cloud storage (S3, R2, etc.).

        NOTE: This is a placeholder implementation. In production, integrate with:
        - AWS S3
        - Cloudflare R2
        - Google Cloud Storage
        - Azure Blob Storage

        Args:
            file_data: File content as bytes
            filename: Target filename
            content_type: MIME type

        Returns:
            Public URL of uploaded file
        """
        # TODO: Implement actual cloud storage integration
        # For now, return a placeholder URL

        # Example implementation with boto3 (AWS S3):
        # import boto3
        # s3_client = boto3.client('s3')
        # s3_client.put_object(
        #     Bucket='diagnoleads-qr-codes',
        #     Key=filename,
        #     Body=file_data,
        #     ContentType=content_type
        # )
        # return f"https://diagnoleads-qr-codes.s3.amazonaws.com/{filename}"

        # Placeholder URL
        return f"https://storage.diagnoleads.com/qr-codes/{filename}"

    # ========================================================================
    # Complete QR Code Creation Flow
    # ========================================================================

    async def create_qr_code(
        self,
        tenant_id: UUID,
        assessment_id: UUID,
        qr_data: QRCodeCreate,
        short_url_domain: str = "dgnl.ds",
    ) -> QRCode:
        """Create a new QR code with image generation and storage.

        Complete flow:
        1. Validate tenant and assessment
        2. Generate unique short code
        3. Generate QR code image
        4. Upload to cloud storage
        5. Create database record

        Args:
            tenant_id: Tenant UUID
            assessment_id: Assessment UUID
            qr_data: QR code creation data
            short_url_domain: Domain for short URLs

        Returns:
            Created QRCode instance

        Raises:
            ValueError: If tenant or assessment not found
        """
        # 1. Validate tenant
        tenant_result = await self.db.execute(
            select(Tenant).where(Tenant.id == tenant_id)
        )
        tenant = tenant_result.scalar_one_or_none()
        if not tenant:
            raise ValueError(f"Tenant {tenant_id} not found")

        # 2. Validate assessment (and check tenant ownership)
        assessment_result = await self.db.execute(
            select(Assessment).where(
                Assessment.id == assessment_id, Assessment.tenant_id == tenant_id
            )
        )
        assessment = assessment_result.scalar_one_or_none()
        if not assessment:
            raise ValueError(
                f"Assessment {assessment_id} not found for tenant {tenant_id}"
            )

        # 3. Generate unique short code
        short_code = await self.generate_unique_short_code()

        # 4. Build short URL
        short_url = f"https://{short_url_domain}/{short_code}"

        # 5. Build full URL with UTM parameters
        base_url = f"https://app.diagnoleads.com/assessments/{assessment_id}"
        utm_params = []

        if qr_data.utm_source:
            utm_params.append(f"utm_source={qr_data.utm_source}")
        if qr_data.utm_medium:
            utm_params.append(f"utm_medium={qr_data.utm_medium}")
        if qr_data.utm_campaign:
            utm_params.append(f"utm_campaign={qr_data.utm_campaign}")
        if qr_data.utm_term:
            utm_params.append(f"utm_term={qr_data.utm_term}")
        if qr_data.utm_content:
            utm_params.append(f"utm_content={qr_data.utm_content}")

        # Add short code parameter for tracking
        utm_params.append(f"qr={short_code}")

        full_url = f"{base_url}?{'&'.join(utm_params)}" if utm_params else base_url

        # 6. Generate QR code image
        qr_color = qr_data.style.color if qr_data.style else "#1E40AF"
        qr_size = qr_data.style.size if qr_data.style else 512

        qr_img = self.generate_qr_image(
            url=full_url, color=qr_color, size=qr_size, error_correction="H"
        )

        # 7. Convert to bytes
        png_bytes = self.qr_image_to_bytes(qr_img, format="PNG")

        # 8. Upload to storage
        filename_png = f"qr_{short_code}.png"
        image_url = await self.upload_to_storage(
            file_data=png_bytes, filename=filename_png, content_type="image/png"
        )

        # 9. Create database record
        qr_code = QRCode(
            tenant_id=tenant_id,
            assessment_id=assessment_id,
            name=qr_data.name,
            short_code=short_code,
            short_url=short_url,
            utm_source=qr_data.utm_source,
            utm_medium=qr_data.utm_medium,
            utm_campaign=qr_data.utm_campaign,
            utm_term=qr_data.utm_term,
            utm_content=qr_data.utm_content,
            style=qr_data.style.dict() if qr_data.style else {},
            qr_code_image_url=image_url,
            scan_count=0,
            unique_scan_count=0,
            enabled=True,
        )

        self.db.add(qr_code)
        await self.db.commit()
        await self.db.refresh(qr_code)

        return qr_code

    async def regenerate_qr_image(self, qr_code_id: UUID, tenant_id: UUID) -> QRCode:
        """Regenerate QR code image with updated style.

        Args:
            qr_code_id: QR code UUID
            tenant_id: Tenant UUID (for security check)

        Returns:
            Updated QRCode instance

        Raises:
            ValueError: If QR code not found
        """
        # Fetch existing QR code
        result = await self.db.execute(
            select(QRCode).where(QRCode.id == qr_code_id, QRCode.tenant_id == tenant_id)
        )
        qr_code = result.scalar_one_or_none()

        if not qr_code:
            raise ValueError(f"QR code {qr_code_id} not found")

        # Build full URL
        base_url = f"https://app.diagnoleads.com/assessments/{qr_code.assessment_id}"
        utm_params = []

        if qr_code.utm_source:
            utm_params.append(f"utm_source={qr_code.utm_source}")
        if qr_code.utm_medium:
            utm_params.append(f"utm_medium={qr_code.utm_medium}")
        if qr_code.utm_campaign:
            utm_params.append(f"utm_campaign={qr_code.utm_campaign}")
        if qr_code.utm_term:
            utm_params.append(f"utm_term={qr_code.utm_term}")
        if qr_code.utm_content:
            utm_params.append(f"utm_content={qr_code.utm_content}")

        utm_params.append(f"qr={qr_code.short_code}")
        full_url = f"{base_url}?{'&'.join(utm_params)}"

        # Generate new image with current style
        qr_color = qr_code.style.get("color", "#1E40AF")
        qr_size = qr_code.style.get("size", 512)

        qr_img = self.generate_qr_image(
            url=full_url, color=qr_color, size=qr_size, error_correction="H"
        )

        # Upload
        png_bytes = self.qr_image_to_bytes(qr_img, format="PNG")
        filename_png = f"qr_{qr_code.short_code}_v2.png"
        image_url = await self.upload_to_storage(
            file_data=png_bytes, filename=filename_png, content_type="image/png"
        )

        # Update database
        qr_code.qr_code_image_url = image_url
        await self.db.commit()
        await self.db.refresh(qr_code)

        return qr_code
