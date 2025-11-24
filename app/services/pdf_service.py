"""
PDF generation and form filling service
"""
from typing import Dict
from pathlib import Path
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter
import os

from app.utils.logger import logger


class PDFService:
    """Service for PDF generation and form filling"""

    def __init__(self):
        """Initialize PDF service"""
        self.templates_dir = Path("templates")
        self.templates_dir.mkdir(exist_ok=True)

    def fill_pdf_form(self, form_type: str, fields: Dict[str, str]) -> bytes:
        """
        Fill a PDF form with provided data

        Args:
            form_type: Type of form template to use
            fields: Dictionary of field names to values

        Returns:
            Filled PDF as bytes
        """
        template_path = self.templates_dir / f"{form_type}.pdf"

        # Check if template exists
        if not template_path.exists():
            logger.info(f"Template not found, generating new PDF: {form_type}")
            return self._generate_simple_pdf(fields)

        try:
            # Try to fill existing form
            return self._fill_existing_form(template_path, fields)
        except Exception as e:
            logger.error(f"Failed to fill form: {str(e)}")
            # Fall back to generating a simple PDF
            return self._generate_simple_pdf(fields)

    def _fill_existing_form(self, template_path: Path, fields: Dict[str, str]) -> bytes:
        """
        Fill an existing PDF form

        Args:
            template_path: Path to PDF template
            fields: Field values

        Returns:
            Filled PDF as bytes
        """
        reader = PdfReader(str(template_path))
        writer = PdfWriter()

        # Copy pages
        for page in reader.pages:
            writer.add_page(page)

        # Try to fill form fields if they exist
        if "/AcroForm" in reader.trailer["/Root"]:
            writer.update_page_form_field_values(writer.pages[0], fields)

        # Write to bytes
        output = BytesIO()
        writer.write(output)
        output.seek(0)

        return output.read()

    def _generate_simple_pdf(self, fields: Dict[str, str]) -> bytes:
        """
        Generate a simple PDF with field values

        Args:
            fields: Dictionary of field names to values

        Returns:
            PDF as bytes
        """
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Add title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, "Personal Information Form")

        # Add fields
        c.setFont("Helvetica", 12)
        y_position = height - 100

        for field_name, field_value in fields.items():
            if y_position < 50:
                c.showPage()
                y_position = height - 50

            # Format field name nicely
            display_name = field_name.replace("_", " ").title()

            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y_position, f"{display_name}:")

            c.setFont("Helvetica", 12)
            c.drawString(250, y_position, str(field_value or "N/A"))

            y_position -= 30

        c.save()
        buffer.seek(0)

        return buffer.read()

    def create_sample_template(self) -> None:
        """Create a sample PDF template for testing"""
        template_path = self.templates_dir / "sample_form.pdf"

        if template_path.exists():
            return

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Create a simple form template
        c.setFont("Helvetica-Bold", 18)
        c.drawString(200, height - 50, "Sample Application Form")

        c.setFont("Helvetica", 12)
        y_pos = height - 100

        fields_layout = [
            ("Full Name:", 120),
            ("Date of Birth:", 140),
            ("Address:", 160),
            ("ID Number:", 180),
            ("Expiry Date:", 200),
        ]

        for label, offset in fields_layout:
            c.drawString(50, height - offset, label)
            c.line(200, height - offset, 500, height - offset)

        c.save()
        buffer.seek(0)

        # Save template
        with open(template_path, "wb") as f:
            f.write(buffer.read())

        logger.info(f"Created sample template at {template_path}")


# Global service instance
pdf_service = PDFService()
