"""
API routes for PDF form filling
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from app.models.schemas import PDFPrefillRequest
from app.services.pdf_service import pdf_service
from app.utils.logger import logger

router = APIRouter(prefix="/prefill-pdf", tags=["pdf"])


@router.post("")
async def prefill_pdf(request: PDFPrefillRequest) -> Response:
    """
    Fill a PDF form with provided field values

    Args:
        request: Form type and field values

    Returns:
        Filled PDF file as downloadable response
    """
    try:
        logger.info(
            f"Processing PDF prefill request: form_type={request.form_type}, "
            f"fields={len(request.fields)}"
        )

        # Generate filled PDF
        pdf_bytes = pdf_service.fill_pdf_form(request.form_type, request.fields)

        logger.info("PDF generated successfully")

        # Return as downloadable file
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={request.form_type}_filled.pdf"
            },
        )

    except Exception as e:
        logger.error(f"PDF generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")
