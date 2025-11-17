"""
QR Code Image Generator

Generates QR code images in various formats (PNG, SVG) with customization options.
"""

import io
import base64
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer, CircleModuleDrawer, SquareModuleDrawer


class QRCodeImageGenerator:
    """
    Generate QR code images with custom styling.

    Features:
    - Multiple formats (PNG, SVG)
    - Custom colors and sizes
    - Logo embedding
    - Different styles (rounded, circle, square)
    """

    def __init__(self):
        self.default_size = 512
        self.default_color = "#000000"
        self.default_bg_color = "#FFFFFF"

    def generate_png(
        self,
        data: str,
        size: int = 512,
        color: str = "#000000",
        bg_color: str = "#FFFFFF",
        style: str = "square",
        logo_path: Optional[str] = None,
        error_correction: str = "H"
    ) -> bytes:
        """
        Generate QR code as PNG image.

        Args:
            data: Data to encode in QR code (URL)
            size: Image size in pixels
            color: Foreground color (hex)
            bg_color: Background color (hex)
            style: Module style - 'square', 'rounded', 'circle'
            logo_path: Optional path to logo image to embed
            error_correction: Error correction level (L/M/Q/H)

        Returns:
            PNG image as bytes
        """
        # Error correction mapping
        error_correction_map = {
            "L": qrcode.constants.ERROR_CORRECT_L,  # ~7%
            "M": qrcode.constants.ERROR_CORRECT_M,  # ~15%
            "Q": qrcode.constants.ERROR_CORRECT_Q,  # ~25%
            "H": qrcode.constants.ERROR_CORRECT_H,  # ~30% (best for logo embedding)
        }

        # Module drawer mapping
        module_drawer_map = {
            "square": SquareModuleDrawer(),
            "rounded": RoundedModuleDrawer(),
            "circle": CircleModuleDrawer(),
        }

        # Create QR code instance
        qr = qrcode.QRCode(
            version=1,  # Auto-determine
            error_correction=error_correction_map.get(error_correction, qrcode.constants.ERROR_CORRECT_H),
            box_size=10,
            border=4,
        )

        qr.add_data(data)
        qr.make(fit=True)

        # Generate image with style
        img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=module_drawer_map.get(style, SquareModuleDrawer()),
            fill_color=color,
            back_color=bg_color
        )

        # Resize to desired size
        img = img.resize((size, size), Image.Resampling.LANCZOS)

        # Embed logo if provided
        if logo_path:
            img = self._embed_logo(img, logo_path)

        # Convert to bytes
        buffer = io.BytesIO()
        img.save(buffer, format="PNG", optimize=True)
        buffer.seek(0)

        return buffer.getvalue()

    def generate_svg(
        self,
        data: str,
        color: str = "#000000",
        bg_color: str = "#FFFFFF",
        error_correction: str = "H"
    ) -> str:
        """
        Generate QR code as SVG.

        Args:
            data: Data to encode in QR code
            color: Foreground color (hex)
            bg_color: Background color (hex)
            error_correction: Error correction level

        Returns:
            SVG as string
        """
        from qrcode.image.svg import SvgPathImage

        # Error correction mapping
        error_correction_map = {
            "L": qrcode.constants.ERROR_CORRECT_L,
            "M": qrcode.constants.ERROR_CORRECT_M,
            "Q": qrcode.constants.ERROR_CORRECT_Q,
            "H": qrcode.constants.ERROR_CORRECT_H,
        }

        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=error_correction_map.get(error_correction, qrcode.constants.ERROR_CORRECT_H),
            box_size=10,
            border=4,
            image_factory=SvgPathImage
        )

        qr.add_data(data)
        qr.make(fit=True)

        # Generate SVG
        img = qr.make_image(fill_color=color, back_color=bg_color)

        # Convert to string
        buffer = io.BytesIO()
        img.save(buffer)
        buffer.seek(0)

        return buffer.getvalue().decode('utf-8')

    def generate_base64(
        self,
        data: str,
        size: int = 512,
        color: str = "#000000",
        bg_color: str = "#FFFFFF",
        style: str = "square"
    ) -> str:
        """
        Generate QR code as base64-encoded PNG for inline use.

        Args:
            data: Data to encode
            size: Image size
            color: Foreground color
            bg_color: Background color
            style: Module style

        Returns:
            Base64-encoded PNG with data URI prefix
        """
        png_bytes = self.generate_png(data, size, color, bg_color, style)
        base64_str = base64.b64encode(png_bytes).decode('utf-8')
        return f"data:image/png;base64,{base64_str}"

    def generate_with_frame(
        self,
        data: str,
        title: str,
        description: Optional[str] = None,
        size: int = 800,
        qr_color: str = "#000000",
        bg_color: str = "#FFFFFF",
        style: str = "square"
    ) -> bytes:
        """
        Generate QR code with decorative frame and text.

        Args:
            data: Data to encode
            title: Title text above QR code
            description: Optional description below QR code
            size: Canvas size
            qr_color: QR code color
            bg_color: Background color
            style: Module style

        Returns:
            PNG image with frame as bytes
        """
        # Generate QR code (70% of canvas)
        qr_size = int(size * 0.7)
        qr_bytes = self.generate_png(data, qr_size, qr_color, bg_color, style)
        qr_img = Image.open(io.BytesIO(qr_bytes))

        # Create canvas
        canvas = Image.new('RGB', (size, size), bg_color)
        draw = ImageDraw.Draw(canvas)

        # Try to load font, fall back to default if not available
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
            desc_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        except:
            title_font = ImageFont.load_default()
            desc_font = ImageFont.load_default()

        # Calculate positions
        qr_x = (size - qr_size) // 2
        title_height = 80
        qr_y = title_height + 20

        # Draw title
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (size - title_width) // 2
        draw.text((title_x, 20), title, fill=qr_color, font=title_font)

        # Paste QR code
        canvas.paste(qr_img, (qr_x, qr_y))

        # Draw description if provided
        if description:
            desc_y = qr_y + qr_size + 20
            desc_bbox = draw.textbbox((0, 0), description, font=desc_font)
            desc_width = desc_bbox[2] - desc_bbox[0]
            desc_x = (size - desc_width) // 2
            draw.text((desc_x, desc_y), description, fill=qr_color, font=desc_font)

        # Convert to bytes
        buffer = io.BytesIO()
        canvas.save(buffer, format="PNG", optimize=True)
        buffer.seek(0)

        return buffer.getvalue()

    def _embed_logo(
        self,
        qr_image: Image.Image,
        logo_path: str,
        logo_size_ratio: float = 0.25
    ) -> Image.Image:
        """
        Embed logo in center of QR code.

        Args:
            qr_image: QR code PIL Image
            logo_path: Path to logo image
            logo_size_ratio: Logo size as ratio of QR code size

        Returns:
            QR code with embedded logo
        """
        try:
            # Load logo
            logo = Image.open(logo_path)

            # Calculate logo size (max 25% of QR code)
            qr_width, qr_height = qr_image.size
            logo_max_size = int(qr_width * logo_size_ratio)

            # Resize logo maintaining aspect ratio
            logo.thumbnail((logo_max_size, logo_max_size), Image.Resampling.LANCZOS)

            # Add white background to logo for better visibility
            logo_with_bg = Image.new('RGB', logo.size, 'white')
            if logo.mode == 'RGBA':
                logo_with_bg.paste(logo, (0, 0), logo)
            else:
                logo_with_bg.paste(logo, (0, 0))

            # Calculate position (center)
            logo_x = (qr_width - logo.width) // 2
            logo_y = (qr_height - logo.height) // 2

            # Paste logo
            qr_image.paste(logo_with_bg, (logo_x, logo_y))

        except Exception as e:
            print(f"Warning: Failed to embed logo: {e}")

        return qr_image


# Convenience functions
def generate_qr_png(url: str, size: int = 512, style: dict = None) -> bytes:
    """
    Quick function to generate QR code PNG.

    Args:
        url: URL to encode
        size: Image size in pixels
        style: Optional style dict with keys: color, bg_color, module_style

    Returns:
        PNG bytes
    """
    generator = QRCodeImageGenerator()

    if style is None:
        style = {}

    return generator.generate_png(
        data=url,
        size=size,
        color=style.get("color", "#000000"),
        bg_color=style.get("bg_color", "#FFFFFF"),
        style=style.get("module_style", "square")
    )


def generate_qr_svg(url: str, style: dict = None) -> str:
    """
    Quick function to generate QR code SVG.

    Args:
        url: URL to encode
        style: Optional style dict with keys: color, bg_color

    Returns:
        SVG string
    """
    generator = QRCodeImageGenerator()

    if style is None:
        style = {}

    return generator.generate_svg(
        data=url,
        color=style.get("color", "#000000"),
        bg_color=style.get("bg_color", "#FFFFFF")
    )
